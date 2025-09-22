import numpy as np, pandas as pd
from sklearn.preprocessing import StandardScaler
import os # Import the os module
from tensorflow import keras

DATA_PATH   = "/Users/macbookpro/Documents/Projects/Pse/code/storage/files/Unit3Sample.xlsx"
DATA_PATH   = "/Users/macbookpro/Documents/Projects/Pse/code/storage/trainer/unit3/unit3cetak.csv"
INPUT_COLS  = ["SKR3.ACTIVE PWR",
              "SKR3.ACTIVE PWR  UNIT 3",
              "SKR3.BUS BAR VOLTAGE U3",
              "SKR3.HOT AIR TEMPERATURE1 U3",
              "SKR3.HOT AIR TEMPERATURE2 U3",
              "SKR3.HOT AIR TEMPERATURE3 U3",
              "SKR3.HOT AIR TEMPERATURE4 U3",
              "SKR3.HOT AIR TEMPERATURE5 U3",
              "SKR3.HOT AIR TEMPERATURE6 U3",
              "SKR3.LOAD LIMITERPOSITION U 3",
              "SKR3.REACTIVE    PWR UNIT 3",
              "SKR3.ROTOR CURR  UNIT 3",
              "SKR3.ROTOR VOLT  UNIT 3",
              "SKR3.SPIRAL CASE PRESS UNIT 3",
              "SKR3.STATOR CURR UNIT 3",
              "SKR3.STATOR VOLT UNIT 3",
              "SKR3.TAIL WATER  PRESSURE U3",
              "SKR3.THRUST BRG  METAL 1 U3",
              "SKR3.THRUST BRG  METAL 2 U3",
            #   "SKR3.THRUST BRG  METAL 3 U3",
              "SKR3.TURB SPEED  DROOP UNIT 3",
              "SKR3.TURB SPEED  UNIT 3",
              "SKR3.TURBINE DISCHARGE U3",
              # "SKR3.U3 Set Point  Beban",
            #   "SKR3.U3 Set Point  Mvar",
            #   "SKR3.U3 Set Point  Trb Speed",
              "SKR3.UP GUIDE BRG METAL 1 U3",
              "SKR3.UP GUIDE BRG METAL 2 U3",
              "SKR3.WATER UPSTREAM PRESS U3",
              "SKR3.WICKET GATE POSITION U3",
              "SKR3.OIL TEMP. U3 MAIN TRAFO",
              "DISCHARGE\xa0DEBIT\xa0UNIT\xa03"
               ] #28
TARGET_COLS = ["SKR3.LO GUIDE BRG METAL 1 U3",
              "SKR3.LO GUIDE BRG METAL 2 U3",
              "SKR3.LO GUIDE BRGOIL TEMP U3",
              "SKR3.METAL TEMP 1 U3",
              "SKR3.METAL TEMP 2 U3",
              "SKR3.OIL TEMP. U3",
              "SKR3.STATOR CORE TEMP1 U3",
              "SKR3.STATOR CORE TEMP2 U3",
              "SKR3.STATOR WIND TEMP1 U3",
            #   "SKR3.STATOR WIND TEMP2 U3",
              "SKR3.STATOR WIND TEMP3 U3",
              "SKR3.STATOR WIND TEMP4 U3",
              "SKR3.STATOR WIND TEMP5 U3",
              "SKR3.STATOR WIND TEMP6 U3",
              "SKR3.UP GD&TH BRGOIL TEMP U3",
              "SKR3.UPPER VIBRASI HORIZONTAL",
              "SKR3.UPPER VIBRASI VERTIKAL",
              "SKR3.UPPER VIBRASI AXIAL",
              "SKR3.LOWER VIBRASI HORIZONTAL",
              "SKR3.LOWER VIBRASI VERTIKAL",
              "SKR3.LOWER VIBRASI AXIAL",
              "SKR3.TURBIN VIBRASI HORIZONTAL",
              "SKR3.TURBIN VIBRASI VERTIKAL",
              "SKR3.TURBIN VIBRASI AXIAL"
              ]

TIMESTEPS   = 30
HORIZON     = 6

async def run_unit3_lstm():
    data_dir = os.path.dirname(DATA_PATH)
    try:
        print(f"Listing contents of directory: {data_dir}")
    except FileNotFoundError:
        print(f"Directory not found: {data_dir}")

    # df = pd.read_excel(DATA_PATH, index_col=0, parse_dates=True)
    df = pd.read_csv(DATA_PATH, index_col=0, parse_dates=True)

    print(df)

    df = df.sort_index()
    # Replace 'I/O Timeout' with NaN
    df.replace('I/O Timeout', np.nan, inplace=True)
    df = df.where(df >= 0, np.nan)
    # df = df.where(df == 0, np.nan)
    # Convert all columns to numeric, coercing errors
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df = df.interpolate(method="time", limit_direction="both").ffill().bfill()

    # --- 1. Load & Pembersihan Awal ---
    # Pastikan DATA_PATH sudah didefinisikan, contoh: DATA_PATH = 'data_sensor.xlsx'
    # df = pd.read_excel(DATA_PATH, index_col=0, parse_dates=True)
    df = pd.read_csv(DATA_PATH, index_col=0, parse_dates=True)
    df = df.sort_index()

    # Mengganti nilai teks 'I/O Timeout' dengan NaN
    df.replace('I/O Timeout', np.nan, inplace=True)

    # Mengganti semua nilai negatif dengan NaN
    df = df.where(df >= 0, np.nan)
    # Mengonversi semua kolom menjadi tipe data numerik
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # --- 2. Logika Pengisian Data Hilang ---

    # Tentukan jumlah data minimal yang dibutuhkan untuk menggunakan EMA
    span_size = 5

    # Iterasi melalui setiap kolom untuk menerapkan logika pengisian
    for col in df.columns:
        # Hitung jumlah data valid (bukan NaN) pada kolom
        jumlah_data_valid = df[col].count()

        # Jika data valid cukup banyak, gunakan Exponential Moving Average (EMA)
        if jumlah_data_valid >= span_size:
            ema_values = df[col].ewm(span=span_size, min_periods=1, adjust=False).mean()
            df[col] = df[col].fillna(ema_values)

        # Jika data valid tidak cukup, gunakan interpolasi waktu
        else:
            df[col] = df[col].interpolate(method="time", limit_direction="both")

    # --- 3. Jaring Pengaman Final ---
    # Pastikan tidak ada nilai NaN yang tersisa sama sekali
    df = df.ffill().bfill()

    # --- Normalize (separate scalers for X and y) ---
    scaler_X = StandardScaler().fit(df[INPUT_COLS].values)
    scaler_y = StandardScaler().fit(df[TARGET_COLS].values)

    X_prd  = scaler_X.transform(df[INPUT_COLS].values)
    y_prd = scaler_y.transform(df[TARGET_COLS].values)

    Xte, yte_flat, yte_full = build_sequences_multistep(X_prd,  y_prd, TIMESTEPS, HORIZON)

    model_lstm = keras.models.load_model("storage/trainer/unit3/best_lstm.keras")

    n_targets = len(TARGET_COLS)

    next_flat = model_lstm.predict(Xte)[0]
    next_full_scaled = next_flat.reshape(HORIZON, n_targets)

    next_full = np.zeros_like(next_full_scaled, dtype=np.float64)
    for h in range(HORIZON):
        next_full[h, :] = scaler_y.inverse_transform(next_full_scaled[h, :].reshape(1, -1))[0]

    offset = pd.tseries.frequencies.to_offset("5min")
    timestamps = [df.index[-1] + offset*(h+1) for h in range(HORIZON)]
    forecast_df = pd.DataFrame(next_full, index=pd.Index(timestamps, name="timestamp"), columns=TARGET_COLS)

    return {
        "timestamps": forecast_df.index.tolist(),
        "columns": forecast_df.columns.tolist(),
        "values": forecast_df.values.tolist()
    }

def build_sequences_multistep(X, y, timesteps, horizon):
    n_samples = X.shape[0] - timesteps - horizon + 1
    n_features = X.shape[1]
    n_outputs = y.shape[1]
    X_seq = np.zeros((n_samples, timesteps, n_features), dtype=np.float32)
    y_seq_full = np.zeros((n_samples, horizon, n_outputs), dtype=np.float32)
    for i in range(n_samples):
        X_seq[i] = X[i:i+timesteps]
        y_seq_full[i] = y[i+timesteps:i+timesteps+horizon]
    y_seq_flat = y_seq_full.reshape(n_samples, horizon*n_outputs)
    return X_seq, y_seq_flat, y_seq_full