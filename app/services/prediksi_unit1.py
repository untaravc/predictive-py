# PREDIKSI
# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import tensorflow as tf
import joblib
import os

# --- Konfigurasi ---
# Pastikan path ini sama dengan yang digunakan saat training
OUTPUT_DIR = "/Users/macbookpro/Documents/Projects/Pse/code/storage/trainer/unit1"
MODEL_PATH = os.path.join(OUTPUT_DIR, "final_lstm_model.keras") # Gunakan model terbaik
SCALER_X_PATH = os.path.join(OUTPUT_DIR, "scaler_X.save")
SCALER_Y_PATH = os.path.join(OUTPUT_DIR, "scaler_y.save")
DATA_PATH = os.path.join(OUTPUT_DIR, "unit1completeFull.xlsx")

# Konfigurasi ini harus SAMA PERSIS dengan saat training
TIMESTEPS = 100
HORIZON = 25
INPUT_COLS  = ["SKR1.24VDC VOLTAGE BUSBAR A",
               "SKR1.24VDC VOLTAGE BUSBAR B",
               "SKR1.ACTIVE POWER U1",
               "SKR1.ACTIVE PWR",
               "SKR1.BUSBAR VOLTAGE",
               "SKR1.Current Inc To Trafo1",
               "SKR1.Current Inc To Trafo2",
              "SKR1.Current Incoming From 5M",
               "SKR1.Current Out To As Pulau",
               "SKR1.Current Out To MV/LV TR1",
               "SKR1.Current Out To MV/LV TR2",
               "SKR1.Current Out To PH",
               "SKR1.Current Out To WTP",
               "SKR1.DIESEL 1 ACTIVE POWER",
               "SKR1.DIESEL 1 STATOR CURRENT",
               "SKR1.DIESEL 1 STATOR VOLTAGE",
               "SKR1.DIESEL 2 ACTIVE POWER",
               "SKR1.DIESEL 2 STATOR CURRENT",
              "SKR1.DIESEL 2 STATOR VOLTAGE",
               "SKR1.LOAD LIMITERPOSITION U 1",
               "SKR1.MDB Voltage Busbar A",
               "SKR1.MDB Voltage Busbar B",
               "SKR1.REACTIVE PWR UNIT 1",
               "SKR1.REACTIVE PWR UNIT 1 rev",
               "SKR1.REACTIVE POWER U1",
               "SKR1.ROTOR CURR UNIT 1",
              #  "SKR1.ROTOR CURR UNIT 1 rev",
               "SKR1.ROTOR VOLT UNIT 1",
               "SKR1.LO GUIDE BRG METAL 1 U1",
               "SKR1.LO GUIDE BRG METAL 2 U1",
               "SKR1.UP GUIDE BRG METAL 1 U1",
               "SKR1.UP GUIDE BRG METAL 2 U1",
               "SKR1.ROTOR VOLT UNIT 1 rev",
               "SKR1.STATOR CURR UNIT 1",
               "SKR1.STATOR VOLT UNIT 1",
               "SKR1.TAIL WATER PRESSURE",
               "SKR1.TURB SPEEDDROOP UNIT 1",
               "SKR1.TURB SPEED UNIT 1",
               "SKR1.TURBINE DISCHARGE",
               "SKR1.TURBINE SPEED DROP U1",
               "SKR1.Voltage Inc Fr 5MVA Traf",
               "SKR1.Voltage Out To As Pulau",
               "SKR1.Voltage Out To MV/LV TR1",
               "SKR1.Voltage Out To MV/LV TR2",
               "SKR1.WATER UPSTREAM PRESSURE",
               "SKR1.WICKET GATE POSITION",
               "SKR1.HOT AIR TEMPERATURE1 U1",
               "SKR1.HOT AIR TEMPERATURE2 U1",
               "SKR1.HOT AIR TEMPERATURE3 U1",
               "SKR1.HOT AIR TEMPERATURE4 U1",
               "SKR1.HOT AIR TEMPERATURE5 U1",
               "SKR1.HOT AIR TEMPERATURE6 U1",
               "DISCHARGE DEBIT UNIT 1",
               "SKR1.LO GUIDE BRGOIL TEMP U1",
               "SKR1.METAL TEMP 1 U1",
               "SKR1.OIL TEMP. U1",
               "SKR1.UP GD&TH BRGOIL TEMP U1",
               "SKR1.THRUST BRG METAL 1 U1",
               "SKR1.THRUST BRG METAL 2 U1",
               "SKR1.THRUST BRG METAL 3 U1",
               "SKR1.STATOR CORE TEMP1 U1",
               "SKR1.STATOR CORE TEMP2 U1",
               "SKR1.STATOR WIND TEMP1 U1",
               "SKR1.STATOR WIND TEMP2 U1",
               "SKR1.STATOR WIND TEMP3 U1",
               "SKR1.STATOR WIND TEMP4 U1",
               "SKR1.STATOR WIND TEMP5 U1",
               "SKR1.STATOR WIND TEMP6 U1",
               "SKR1.UPPER VIBRASI HORIZONTAL",
               "SKR1.UPPER VIBRASI VERTIKAL",
               "SKR1.UPPER VIBRASI AXIAL",
               "SKR1.LOWER VIBRASI HORIZONTAL",
               "SKR1.LOWER VIBRASI VERTIKAL",
               "SKR1.LOWER VIBRASI AXIAL",
               "SKR1.TURBIN VIBRASI HORIZONTAL",
               "SKR1.TURBIN VIBRASI VERTIKAL",
               "SKR1.TURBIN VIBRASI AXIAL"
               ]
TARGET_COLS = ["SKR1.LO GUIDE BRGOIL TEMP U1",
               "SKR1.METAL TEMP 1 U1",
               "SKR1.OIL TEMP. U1",
               "SKR1.UP GD&TH BRGOIL TEMP U1",
               "SKR1.THRUST BRG METAL 1 U1",
               "SKR1.THRUST BRG METAL 2 U1",
               "SKR1.THRUST BRG METAL 3 U1",
               "SKR1.STATOR CORE TEMP1 U1",
               "SKR1.STATOR CORE TEMP2 U1",
               "SKR1.STATOR WIND TEMP1 U1",
               "SKR1.STATOR WIND TEMP2 U1",
               "SKR1.STATOR WIND TEMP3 U1",
               "SKR1.STATOR WIND TEMP4 U1",
               "SKR1.STATOR WIND TEMP5 U1",
               "SKR1.STATOR WIND TEMP6 U1",
               "SKR1.UPPER VIBRASI HORIZONTAL",
               "SKR1.UPPER VIBRASI VERTIKAL",
               "SKR1.UPPER VIBRASI AXIAL",
               "SKR1.LOWER VIBRASI HORIZONTAL",
               "SKR1.LOWER VIBRASI VERTIKAL",
               "SKR1.LOWER VIBRASI AXIAL",
               "SKR1.TURBIN VIBRASI HORIZONTAL",
               "SKR1.TURBIN VIBRASI VERTIKAL",
               "SKR1.TURBIN VIBRASI AXIAL"]

async def run_unit1_lstm_final():
# --- 1. Load Model dan Scaler ---
    print("Loading model and scalers...")
    # Load model. `compile=False` mempercepat loading karena kita tidak akan training lagi.
    model = tf.keras.models.load_model(MODEL_PATH, compile=False)
    scaler_X = joblib.load(SCALER_X_PATH)
    scaler_y = joblib.load(SCALER_Y_PATH)
    print("Model and scalers loaded successfully.")

    # --- 2. Siapkan Data Input untuk Prediksi ---
    # Asumsikan Anda memiliki DataFrame `df_new` yang berisi data terbaru.
    # Untuk contoh ini, kita akan menggunakan 100 baris terakhir dari data training asli
    # sebagai input untuk memprediksi 25 periode ke depan.
    # GANTI BAGIAN INI DENGAN DATA ASLI ANDA
    df = pd.read_excel(DATA_PATH, index_col=0, parse_dates=True)
    df = df.sort_index()
    df.replace('I/O Timeout', np.nan, inplace=True)
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df = df.interpolate(method="time", limit_direction="both").ffill().bfill()

    # Ambil 100 baris data terakhir (sesuai TIMESTEPS)
    if len(df) < TIMESTEPS:
        raise ValueError(f"Data tidak cukup. Butuh minimal {TIMESTEPS} baris, tapi hanya ada {len(df)}.")

    last_window_df = df[INPUT_COLS].iloc[-TIMESTEPS:]
    print(f"Menggunakan data dari {last_window_df.index.min()} hingga {last_window_df.index.max()} untuk prediksi.")

    # --- 3. Normalisasi dan Reshape Input ---
    # Normalisasi data input MENGGUNAKAN SCALER_X YANG SUDAH DI-LOAD
    last_window_scaled = scaler_X.transform(last_window_df.values)

    # Reshape data agar sesuai dengan input model: (batch_size, timesteps, n_features)
    # Di sini batch_size = 1 karena kita hanya memprediksi satu sequence
    input_for_model = np.expand_dims(last_window_scaled, axis=0)
    print("Input shape for model:", input_for_model.shape) # Harusnya (1, 100, jumlah_input_cols)

    # --- 4. Lakukan Prediksi ---
    print("Making prediction...")
    prediction_scaled_flat = model.predict(input_for_model)

    # --- 5. Post-processing Hasil Prediksi ---
    # Hasil prediksi masih dalam bentuk flat (1, HORIZON * n_targets) dan ternormalisasi
    # Reshape hasil prediksi menjadi (HORIZON, n_targets)
    n_targets = len(TARGET_COLS)
    prediction_scaled = prediction_scaled_flat.reshape(HORIZON, n_targets)

    # Kembalikan hasil prediksi ke skala aslinya MENGGUNAKAN SCALER_Y
    prediction_original_scale = scaler_y.inverse_transform(prediction_scaled)

    # Buat DataFrame untuk hasil prediksi agar mudah dibaca
    last_timestamp = last_window_df.index[-1]
    # Asumsikan frekuensi data adalah 5 menit ("5T")
    forecast_timestamps = pd.date_range(start=last_timestamp, periods=HORIZON + 1, freq="5T")[1:]

    forecast_df = pd.DataFrame(prediction_original_scale, index=forecast_timestamps, columns=TARGET_COLS)

    print("\n--- Hasil Prediksi untuk 25 Periode ke Depan ---")
    print(forecast_df)

    # Simpan hasil prediksi ke file CSV atau Excel
    forecast_df.to_csv(os.path.join(OUTPUT_DIR, "new_forecast_results.csv"))
    print(f"\nHasil prediksi telah disimpan di {os.path.join(OUTPUT_DIR, 'new_forecast_results.csv')}")

    return {
        "status": "success",
        "message": "Prediksi selesai."
    }