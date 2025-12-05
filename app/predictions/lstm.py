# PREDIKSI
import numpy as np
import pandas as pd
import tensorflow as tf
import joblib
import os
# from app.configs.oracle_conf import TABLE_SENSORS, TABLE_PREDICTIONS, TABLE_RECORDS
from app.utils.oracle_db import fetch_all, execute_query
from app.services.generator_service import build_merge_query
from datetime import datetime, timedelta, timezone
from app.utils.helper import chunk_list
from app.configs.base_conf import settings
from app.configs.unit_config import unit_config

# --- Konfigurasi ---

def run_lstm(task):
    version = datetime.now().strftime("%Y%m%d%H%M%S")
    config = unit_config(task['PARAMS'])
# --- 1. Load Model dan Scaler ---
    # Load model. `compile=False` mempercepat loading karena kita tidak akan training lagi.
    model = tf.keras.models.load_model(config['LSTM_MODEL_PATH'], compile=False)
    scaler_X = joblib.load(config['LSTM_SCALER_X_PATH'])
    scaler_y = joblib.load(config['LSTM_SCALER_Y_PATH'])
    print("Model and scalers loaded successfully. [1]")

    # --- 2. Siapkan Data Input untuk Prediksi ---
    # Asumsikan Anda memiliki DataFrame `df_new` yang berisi data terbaru.
    # Untuk contoh ini, kita akan menggunakan 100 baris terakhir dari data training asli
    # sebagai input untuk memprediksi 25 periode ke depan.
    # GANTI BAGIAN INI DENGAN DATA ASLI ANDA
    df = prepare_data_input(config, task)
    os.makedirs(config['LSTM_OUTPUT_DIR'], exist_ok=True)
    df.to_csv(os.path.join(config['LSTM_OUTPUT_DIR'], "Dataset_"+ version +".csv"))

    df = df.sort_index()
    df.replace('I/O Timeout', np.nan, inplace=True)
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df = df.interpolate(method="time", limit_direction="both").ffill().bfill()

    # Ambil 100 baris data terakhir (sesuai TIMESTEPS)
    if len(df) < config['LSTM_TIMESTEPS']:
        raise ValueError(f"Data tidak cukup. Butuh minimal {config['LSTM_TIMESTEPS']} baris, tapi hanya ada {len(df)}.")

    last_window_df = df[config['LSTM_INPUT_COLS']].iloc[-config['LSTM_TIMESTEPS']:]
    print(f"Menggunakan data dari {last_window_df.index.min()} hingga {last_window_df.index.max()} untuk prediksi.")

    # --- 3. Normalisasi dan Reshape Input ---
    # Normalisasi data input MENGGUNAKAN SCALER_X YANG SUDAH DI-LOAD
    last_window_scaled = scaler_X.transform(last_window_df.values)

    # Reshape data agar sesuai dengan input model: (batch_size, timesteps, n_features)
    # Di sini batch_size = 1 karena kita hanya memprediksi satu sequence

    input_for_model = np.expand_dims(last_window_scaled, axis=0)
    print("Input shape for model:", input_for_model.shape)
    print("Input shape should be model: 1," + str(config['LSTM_TIMESTEPS']) + "," + str(len(config['LSTM_INPUT_COLS'])))

    # # --- 4. Lakukan Prediksi ---
    # print("Making prediction...")
    prediction_scaled_flat = model.predict(input_for_model)

    # --- 5. Post-processing Hasil Prediksi ---
    # Hasil prediksi masih dalam bentuk flat (1, HORIZON * n_targets) dan ternormalisasi
    # Reshape hasil prediksi menjadi (HORIZON, n_targets)
    n_targets = len(config['LSTM_TARGET_COLS'])
    prediction_scaled = prediction_scaled_flat.reshape(config['LSTM_HORIZON'], n_targets)

    # Kembalikan hasil prediksi ke skala aslinya MENGGUNAKAN SCALER_Y
    prediction_original_scale = scaler_y.inverse_transform(prediction_scaled)

    # Buat DataFrame untuk hasil prediksi agar mudah dibaca
    last_timestamp = last_window_df.index[-1]
    # Asumsikan frekuensi data adalah 5 menit ("5T")
    forecast_timestamps = pd.date_range(start=last_timestamp, periods=config['LSTM_HORIZON'] + 1, freq="5min")[1:]

    forecast_df = pd.DataFrame(prediction_original_scale, index=forecast_timestamps, columns=config['LSTM_TARGET_COLS'])

    forecast_df_corrected = forecast_df 
    try:
        # 1. Hitung Rata-rata Nilai Input (hanya untuk kolom target)
        # Kita ambil rata-rata dari data historis yang digunakan untuk prediksi
        # Asumsi: TARGET_COLS adalah subset dari INPUT_COLS
        input_means = last_window_df[config['LSTM_TARGET_COLS']].mean()
        print("Rata-rata input historis (per kolom):")
        print(input_means.head())

        # 2. Hitung Rata-rata Nilai Output (prediksi mentah)
        output_means = forecast_df.mean()
        print("\nRata-rata output prediksi (per kolom):")
        print(output_means.head())

        # 3. Hitung Nilai Koreksi
        # Ini akan menjadi Series (satu nilai koreksi per kolom)
        nilai_koreksi = input_means - output_means
        print("\nNilai koreksi (per kolom):")
        print(nilai_koreksi.head())

        # 4. Hitung Prediksi Akhir
        # Tambahkan nilai koreksi ke setiap baris prediksi
        # Pandas akan otomatis (broadcast) menambahkan nilai Series ke setiap baris DataFrame
        forecast_df_corrected = forecast_df + nilai_koreksi

        print("\nKoreksi berhasil diterapkan.")

    except KeyError as e:
        print(f"\n--- WARNING: Gagal menerapkan koreksi ---")

    print( "Shape hasil prediksi: ", forecast_df.shape)
    forecast_df_corrected.to_csv(os.path.join(config['LSTM_OUTPUT_DIR'], "results_"+ version +".csv"), index=True, float_format='%.6f')

    # Reset index so timestamp becomes a column
    df_reset = forecast_df_corrected.reset_index().rename(columns={"index": "Timestamp"})

    # Melt to long format
    long_df = df_reset.melt(
        id_vars=["Timestamp"],
        var_name="Name",
        value_name="Value"
    )

    # Convert to list of dicts
    result = long_df.to_dict(orient="records")

    insert_update_db(result, config)

    return {
        "status": "success",
    }

def insert_update_db(array, config):
    print('Start input db ', len(array))
    sensors = fetch_all("SELECT * FROM "+ settings.TABLE_SENSORS +" WHERE NAME like '"+config['SENSOR_NAME_QUERY']+"'")

    for sensor in sensors:
        sensor['list'] = []

        for arr in array:
            if sensor["NAME"] in config['LSTM_TARGET_COLS']:
                if sensor["NAME"] == arr["Name"]:
                    ts = arr["Timestamp"]
                    # Ensure timezone-aware and format to ISO 8601 with 'Z'
                    arr["Timestamp"] = ts.tz_localize(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
                    sensor['list'].append(arr)

    for sensor in sensors:
        if len(sensor['list']) > 0:
            for i, chunk in enumerate(chunk_list(sensor['list'], 500), start=1):
                print(f"Processing batch {i} ({len(chunk)} records)")
                query, params = build_merge_query(settings.TABLE_PREDICTIONS, sensor["ID"], chunk)
                execute_query(query, params)

def prepare_data_input(config, task):
    now = datetime.strptime(task['START_AT'].strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")

    date_to = now.strftime("%Y-%m-%d")
    date_from = (now - timedelta(days=config['LSTM_PREPARE_DATA'])).strftime("%Y-%m-%d")
    print('date from ', date_from, ' date to ', date_to)
    sensors = fetch_all("SELECT * FROM "+ settings.TABLE_SENSORS +" WHERE NAME like '"+config['SENSOR_NAME_QUERY']+"'")
    input_sensors_ids = []
    print('sensors count: ', len(sensors))

    # compare with UNIT1_INPUT_COLS
    for sensor in sensors:
        # if sensor["NAME"] in UNIT2_INPUT_COLS:
            input_sensors_ids.append(sensor["ID"])
    
    query_select = "SELECT " + settings.TABLE_RECORDS +".*, "+ settings.TABLE_SENSORS +".NAME FROM "+ settings.TABLE_RECORDS 
    query_select = query_select +" LEFT JOIN "+ settings.TABLE_SENSORS +" ON "+ settings.TABLE_RECORDS +".SENSOR_ID = "+ settings.TABLE_SENSORS +".ID"
    query_select = query_select +" WHERE SENSOR_ID IN (" + ",".join(map(str, input_sensors_ids)) + ") AND RECORD_TIME >= TO_DATE(:date_from, 'YYYY-MM-DD')"
    query_select = query_select +" AND RECORD_TIME < TO_DATE(:date_to, 'YYYY-MM-DD') + INTERVAL '1' DAY"
    params = {"date_from": date_from, "date_to": date_to}

    data_records = fetch_all(query_select, params)
    print('data_records count: ', len(data_records))

   # --- 1️⃣ Convert to DataFrame ---
    df_raw = pd.DataFrame(data_records)
    df_raw["RECORD_TIME"] = pd.to_datetime(df_raw["RECORD_TIME"])
    df_raw["VALUE"] = df_raw["VALUE"].astype(float)

    # --- 2️⃣ Build time index for one week with 5-minute intervals ---
    start_time = pd.Timestamp(date_from)
    time_index = pd.date_range(start=start_time, periods=(2016 * 10), freq="5min")

    # --- 3️⃣ Pivot data into time × sensor ---
    pivot_df = df_raw.pivot_table(index="RECORD_TIME", columns="NAME", values="VALUE")

    # --- 4️⃣ Reindex to full time range (introduce NaNs for missing times) ---
    pivot_df = pivot_df.reindex(time_index)

    # --- 5️⃣ Ensure all sensors exist ---
    # for col in UNIT2_INPUT_COLS:
    # if col not in pivot_df.columns:
    #     pivot_df[col] = np.nan

    # --- 6️⃣ Fill missing data: forward-fill, then fill remaining NaN with 0 ---
    pivot_df = pivot_df.sort_index().ffill().fillna(0)

    # --- 7️⃣ Reorder columns to match UNIT1_INPUT_COLS ---
    # pivot_df = pivot_df[UNIT2_INPUT_COLS]

    pivot_df = fill_zero_with_last_valid(pivot_df).fillna(0)

    df = pivot_df.copy()

    return df

def fill_zero_with_last_valid(df):
    df_filled = df.copy()
    for col in df.columns:
        s = df_filled[col].replace(0, np.nan)
        s = s.ffill()
        df_filled[col] = s
    return df_filled