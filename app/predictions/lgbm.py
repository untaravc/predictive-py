import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
import pickle
from datetime import datetime
import os
from app.utils.oracle_db import fetch_all, execute_query
from app.configs.base_conf import settings
from app.services.generator_service import build_merge_query
from app.utils.helper import chunk_list
from datetime import datetime, timezone, timedelta
from app.configs.lgbm_conf import lgbm_config
warnings.filterwarnings('ignore')

# Path ke file model dan data
# MODELS_FILE = "/Users/macbookpro/Documents/Projects/Pse/code/storage/unit1/v5/all_models.pkl"
# DATA_PATH = "/Users/macbookpro/Documents/Projects/Pse/code/storage/unit1/v5/Dataset.xlsx"
# OUTPUT_DIR = "/Users/macbookpro/Documents/Projects/Pse/code/storage/lgbm"

# Pengaturan Prediksi
# FREQ = '5T'
# INPUT_WINDOW = 6048        # 3 minggu data terakhir sebagai input (5 min * 6048 = 21 hari)
# HORIZON = 2016             # Prediksi 1 minggu ke depan (5 min * 2016 = 7 hari)
# PLOT_HISTORY = 2016        # Tampilkan 1 minggu data historis di plot (5 min * 2016 = 7 hari)

# Filter model (kosongkan untuk prediksi semua model)
# Contoh: ['SKR1.METAL TEMP 1 U1', 'SKR1.OIL TEMP. U1']
MODELS_TO_PREDICT = []     # Kosongkan untuk prediksi semua

def recursive_predict(fcst, history_df, horizon, model_name, unit):
    config = lgbm_config(unit)
    predictions = []
    timestamps = []
    current_history = history_df.copy()

    for step in range(horizon):
        try:
            # Prediksi 1 step ke depan
            pred_df = fcst.predict(h=1, new_df=current_history)
            pred_value = pred_df.iloc[0]['LGBMRegressor']
            predictions.append(pred_value)

            # Generate timestamp untuk prediksi
            last_row = current_history.iloc[-1]
            next_timestamp = last_row['ds'] + pd.Timedelta(config['FREQ'])
            timestamps.append(next_timestamp)

            # Tambahkan prediksi ke history untuk step berikutnya
            next_row = last_row.copy()
            next_row['ds'] = next_timestamp
            next_row['y'] = pred_value

            current_history = pd.concat([current_history, pd.DataFrame([next_row])], ignore_index=True)

            # Progress indicator setiap 500 steps
            if (step + 1) % 500 == 0:
                print(f"      Progress: {step + 1}/{horizon} steps")

        except Exception as e:
            print(f"      Error pada step {step}: {e}")
            break

    return np.array(predictions), timestamps

def predict_model(model_name, model_data, df_full, unit):
    config = lgbm_config(unit)
    """
    Prediksi data baru untuk satu model
    """
    print(f"\n{'='*70}")
    print(f"Prediksi Model: {model_name}")
    print(f"{'='*70}")

    fcst = model_data['fcst']
    features = model_data['features']
    group = model_data['group']

    # Siapkan data
    df_model = df_full[[model_name]].copy()
    df_long = df_model.copy()
    df_long.rename(columns={model_name: 'y'}, inplace=True)
    df_long.reset_index(inplace=True)
    df_long.rename(columns={df_long.columns[0]: 'ds'}, inplace=True)
    df_long['unique_id'] = model_name.replace(" ", "_").replace(".", "_")
    df_long = df_long[['unique_id', 'ds', 'y']]

    print(f"  Total data tersedia: {len(df_long)} baris")
    print(f"  Periode data: {df_long['ds'].iloc[0]} s/d {df_long['ds'].iloc[-1]}")

    # Ambil INPUT_WINDOW data terakhir sebagai input
    if len(df_long) < config['INPUT_WINDOW']:
        print(f"  WARNING: Data tidak cukup. Tersedia {len(df_long)}, butuh minimal {config['INPUT_WINDOW']} data")
        return None

    history_df = df_long.iloc[-config['INPUT_WINDOW']:].copy()
    print(f"  Menggunakan {config['INPUT_WINDOW']} data terakhir sebagai input")
    print(f"  Input periode: {history_df['ds'].iloc[0]} s/d {history_df['ds'].iloc[-1]}")
    print(f"  Horizon prediksi: {config['HORIZON']} steps ({config['HORIZON']*5/60/24:.1f} hari)")

    try:
        # Prediksi rekursif
        print(f"  Melakukan prediksi rekursif...")
        y_pred, pred_timestamps = recursive_predict(fcst, history_df, config['HORIZON'], model_name, unit)

        if len(y_pred) < config['HORIZON']:
            print(f"  WARNING: Prediksi tidak lengkap ({len(y_pred)}/{config['HORIZON']})")
        else:
            print(f"  Prediksi berhasil: {len(y_pred)} steps")

        # Buat dataframe hasil prediksi
        pred_df = pd.DataFrame({
            'Timestamp': pred_timestamps,
            model_name: y_pred
        })
        pred_df.set_index('Timestamp', inplace=True)

        print(f"  Periode prediksi: {pred_df.index[0]} s/d {pred_df.index[-1]}")
        print(f"  Nilai prediksi - Min: {y_pred.min():.2f}, Max: {y_pred.max():.2f}, Mean: {y_pred.mean():.2f}")

        return pred_df

    except Exception as e:
        print(f"  ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None

def run_lgbm(task):
    config = lgbm_config(task['PARAMS'])

    version = datetime.now().strftime("%Y%m%d%H%M%S")
    print("\n[1/4] Memuat model...")
    try:
        with open(config['MODEL_FILE'], 'rb') as f:
            all_models = pickle.load(f)
        print(f"  Berhasil memuat {len(all_models)} model")

        # Tampilkan daftar model
        print("\n  Daftar model yang tersedia:")
        for idx, (model_name, model_data) in enumerate(all_models.items(), 1):
            print(f"    {idx}. {model_name} (Group: {model_data['group']})")

    except Exception as e:
        print(f"  ERROR: Gagal memuat model - {e}")
        exit(1)

    # Filter model jika diminta
    if config["TARGET_COLS"]:
        all_models = {k: v for k, v in all_models.items() if k in config["TARGET_COLS"]}
        print(f"\n  Filter aktif: Prediksi {len(all_models)} model terpilih")

    if len(all_models) == 0:
        print("  ERROR: Tidak ada model untuk diprediksi")
        exit(1)

    print(f"\n[2/4] Memuat data dari Excel...")
    # try:
        # Baca semua kolom dari Excel
        # df_all = pd.read_excel(DATA_PATH, index_col=0, parse_dates=True)
    df_all = prepare_data_input(task, 21)
    df_all.to_csv(config['OUTPUT_DIR'] + "Dataset_"+ version +".csv")

    df_all = df_all.sort_index()
    df_all.replace('I/O Timeout', np.nan, inplace=True)

    # Konversi semua kolom ke numerik
    for col in df_all.columns:
        df_all[col] = pd.to_numeric(df_all[col], errors='coerce')

    # Interpolasi missing values
    df_all = df_all.interpolate(method="time", limit_direction="both").ffill().bfill()

    print(f"  Berhasil memuat data: {df_all.shape[0]} baris, {df_all.shape[1]} kolom")
    print(f"  Periode data: {df_all.index[0]} s/d {df_all.index[-1]}")
    print(f"  Kolom yang tersedia: {list(df_all.columns)}")

    # except Exception as e:
    #     print(f"  ERROR: Gagal memuat data - {e}")
    #     exit(1)

    print(f"\n[3/4] Memulai prediksi untuk {len(all_models)} model...")

    all_predictions = {}
    successful_predictions = 0

    for idx, (model_name, model_data) in enumerate(all_models.items(), 1):
        print(f"\n{'#'*70}")
        print(f"Progress: {idx}/{len(all_models)}")

        # Cek apakah kolom ada di data
        if model_name not in df_all.columns:
            print(f"  WARNING: Kolom '{model_name}' tidak ditemukan dalam data")
            continue

        try:
            # Prediksi model
            pred_df = predict_model(model_name, model_data, df_all, task['PARAMS'])

            if pred_df is not None:
                all_predictions[model_name] = pred_df
                successful_predictions += 1

        except Exception as e:
            print(f"  ERROR: Gagal memproses {model_name} - {e}")
            import traceback
            traceback.print_exc()
            continue

    print(f"\n[4/4] Menyusun hasil prediksi...")
    if all_predictions:
        # Gabungkan semua prediksi menjadi satu dataframe
        combined_predictions = pd.concat(all_predictions.values(), axis=1)
        os.makedirs(config['OUTPUT_DIR'], exist_ok=True)

        combined_predictions.to_csv(config['OUTPUT_DIR'] + "/result" + version + ".csv", index=True)

         # Reset index so timestamp becomes a column
        df_reset = combined_predictions.reset_index().rename(columns={"index": "Timestamp"})

        # Melt to long format
        long_df = df_reset.melt(
            id_vars=["Timestamp"],
            var_name="Name",
            value_name="Value"
        )

        # Convert to list of dicts
        result = long_df.to_dict(orient="records")

        insert_update_db(result, task)

        return {
            "status": "success",
        }
    else:
        print("  WARNING: Tidak ada prediksi yang berhasil")

def insert_update_db(array, task):
    print('Start input db ', len(array))
    config = lgbm_config(task['PARAMS'])
    sensors = fetch_all("SELECT * FROM "+ settings.TABLE_SENSORS +" WHERE NAME like '"+config['SENSOR_NAME_QUERY']+"'")

    for sensor in sensors:
        sensor['list'] = []

        for arr in array:
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

def prepare_data_input(task, days: int = 21):
    config = lgbm_config(task['PARAMS'])

    now = datetime.strptime(task['START_AT'].strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")

    date_to = now.strftime("%Y-%m-%d")
    date_from = (now - timedelta(days=days)).strftime("%Y-%m-%d")
    print('date from ', date_from, ' date to ', date_to)

    sensors = fetch_all("SELECT * FROM "+ settings.TABLE_SENSORS +" WHERE NAME like '"+config['SENSOR_NAME_QUERY']+"'")
    input_sensors_ids = []

    # compare with UNIT1_INPUT_COLS
    for sensor in sensors:
        if sensor["NAME"] in config["INPUT_COLS"]:
            input_sensors_ids.append(sensor["ID"])
    
    query_select = "SELECT " + settings.TABLE_RECORDS +".*, "+ settings.TABLE_SENSORS +".NAME FROM "+ settings.TABLE_RECORDS 
    query_select = query_select +" LEFT JOIN "+ settings.TABLE_SENSORS +" ON "+ settings.TABLE_RECORDS +".SENSOR_ID = "+ settings.TABLE_SENSORS +".ID"
    query_select = query_select +" WHERE SENSOR_ID IN (" + ",".join(map(str, input_sensors_ids)) + ") AND RECORD_TIME >= TO_DATE(:date_from, 'YYYY-MM-DD')"
    query_select = query_select +" AND RECORD_TIME < TO_DATE(:date_to, 'YYYY-MM-DD') + INTERVAL '1' DAY"
    params = {"date_from": date_from, "date_to": date_to}

    data_records = fetch_all(query_select, params)

    print('data_records_count: ', len(data_records))
    

   # --- 1️⃣ Convert to DataFrame ---
    df_raw = pd.DataFrame(data_records)
    df_raw["RECORD_TIME"] = pd.to_datetime(df_raw["RECORD_TIME"])
    df_raw["VALUE"] = df_raw["VALUE"].astype(float)

    # --- 2️⃣ Build time index for one week with 5-minute intervals ---
    start_time = pd.Timestamp(date_from)
    time_index = pd.date_range(start=start_time, periods=config["INPUT_WINDOW"], freq="5min")

    # --- 3️⃣ Pivot data into time × sensor ---
    pivot_df = df_raw.pivot_table(index="RECORD_TIME", columns="NAME", values="VALUE")

    # --- 4️⃣ Reindex to full time range (introduce NaNs for missing times) ---
    pivot_df = pivot_df.reindex(time_index)

    # --- 5️⃣ Ensure all sensors exist ---
    for col in config["INPUT_COLS"]:
        if col not in pivot_df.columns:
            pivot_df[col] = np.nan

    # --- 6️⃣ Fill missing data: forward-fill, then fill remaining NaN with 0 ---
    pivot_df = pivot_df.sort_index().ffill().fillna(0)

    # --- 7️⃣ Reorder columns to match UNIT1_INPUT_COLS ---
    pivot_df = pivot_df[config["INPUT_COLS"]]

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