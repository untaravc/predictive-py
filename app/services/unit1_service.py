from tensorflow import keras
import numpy as np
import numpy as np, pandas as pd
from tensorflow.keras import mixed_precision
from sklearn.preprocessing import StandardScaler
import os
from app.statics.unit1_io import unit1_in, unit1_out
from app.utils.oracle_db import execute_query
from app.archives.oracle_conf import TABLE_SENSORS

# ---------------- Config ----------------
DATA_PATH = "/Users/macbookpro/Documents/Projects/Pse/code/storage/trainer/unit1/Unit1SampleInput.xlsx"
OUTPUT_DIR = "/Users/macbookpro/Documents/Projects/Pse/code/storage/trainer/unit1"
os.makedirs(OUTPUT_DIR, exist_ok=True)

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
TIMESTEPS   = 100            # berapa langkah untuk predict?
HORIZON     = 25          # predict berapa periode?
TEST_FRAC   = 0.15
VAL_FRAC    = 0.15
EPOCHS      = 20
BATCH_SIZE  = 256
LSTM_UNITS  = 256
DROPOUT     = 0.4
L2_REG      = 0.05 # Added L2 regularization parameter
MODE        = "full"  # "full" or "sampled" (1% data for quick testing)
N_SPLITS    = 10  # Number of splits for sequential training
history_list = []
# ----------------------------------------

async def run_unit1_lstm():
    mixed_precision.set_global_policy('mixed_float16')
    model_lstm = keras.models.load_model('/Users/macbookpro/Documents/Projects/Pse/code/storage/trainer/unit1/best_lstm.keras')
    
    # --- Load & INLINE Cleaning ---
    df = pd.read_excel(DATA_PATH, index_col=0, parse_dates=True)
    df = df.sort_index()
    # Replace 'I/O Timeout' with NaN
    df.replace('I/O Timeout', np.nan, inplace=True)
    # df = df.where(df >= 0, np.nan)
    # Convert all columns to numeric, coercing errors
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df = df.interpolate(method="time", limit_direction="both").ffill().bfill()

    # --- Split by time ---
    N = len(df)
    n_test = int(np.floor(TEST_FRAC * N))
    n_trainval = N - n_test
    n_val = int(np.floor(VAL_FRAC * n_trainval))

    # return df.columns.tolist()

    # --- Normalize (separate scalers for X and y) ---
    scaler_X = StandardScaler().fit(df[INPUT_COLS].values)
    scaler_y = StandardScaler().fit(df[TARGET_COLS].values)

    X_test  = scaler_X.transform(df[INPUT_COLS].values)
    y_test  = scaler_y.transform(df[TARGET_COLS].values)

    n_targets = len(TARGET_COLS)

    Xte, yte_flat, yte_full = select_sequence_builder(X_test, y_test, TIMESTEPS, HORIZON, 0, min(100, X_test.shape[0]-TIMESTEPS-HORIZON+1), mode=MODE)
    if Xte is not None and yte_full is not None:
        print("Predicting on test data...")
        y_pred_flat = model_lstm.predict(Xte, batch_size=BATCH_SIZE)
        y_pred_full_scaled = y_pred_flat.reshape(-1, HORIZON, n_targets)
        y_true_full_scaled = yte_full

        # --- Inverse transform ---
        y_pred_full = scaler_y.inverse_transform(y_pred_full_scaled)
        y_true_full = scaler_y.inverse_transform(y_true_full_scaled)
        return y_pred_full, y_true_full
    else:
        return None

def select_sequence_builder(X, y, timesteps, horizon, start_idx, end_idx, mode="full"):
    """Pilih builder sequence: 'full' untuk seluruh data, 'sampled' untuk 1% data."""
    if mode == "sampled":
        return build_sequences_multistep_sampled(X, y, timesteps, horizon, start_idx, end_idx, sample_frac=0.01)
    else:
        return build_sequences_multistep_chunked(X, y, timesteps, horizon, start_idx, end_idx)
    
def build_sequences_multistep_sampled(X, y, timesteps, horizon, start_idx, end_idx, sample_frac=0.01):
    """Ambil hanya 1% data untuk sequence, untuk testing cepat."""
    max_possible = X.shape[0] - timesteps - horizon + 1
    start_idx = max(0, start_idx)
    end_idx = min(end_idx, max_possible)
    n_samples = end_idx - start_idx
    if n_samples <= 0:
        return None, None, None
    sample_size = max(1, int(n_samples * sample_frac))
    indices = np.linspace(start_idx, end_idx-1, sample_size, dtype=int)
    n_features = X.shape[1]
    n_outputs = y.shape[1]
    X_seq = np.zeros((sample_size, timesteps, n_features), dtype=np.float32)
    y_seq_full = np.zeros((sample_size, horizon, n_outputs), dtype=np.float32)
    for i, seq_start in enumerate(indices):
        X_seq[i] = X[seq_start:seq_start+timesteps]
        y_seq_full[i] = y[seq_start+timesteps:seq_start+timesteps+horizon]
    y_seq_flat = y_seq_full.reshape(sample_size, horizon*n_outputs)
    return X_seq, y_seq_flat, y_seq_full

def build_sequences_multistep_chunked(X, y, timesteps, horizon, start_idx, end_idx):
    max_possible = X.shape[0] - timesteps - horizon + 1
    start_idx = max(0, start_idx)
    end_idx = min(end_idx, max_possible)
    n_samples = end_idx - start_idx
    if n_samples <= 0:
        return None, None, None
    n_features = X.shape[1]
    n_outputs = y.shape[1]
    X_seq = np.zeros((n_samples, timesteps, n_features), dtype=np.float32)
    y_seq_full = np.zeros((n_samples, horizon, n_outputs), dtype=np.float32)
    for i in range(n_samples):
        seq_start = start_idx + i
        X_seq[i] = X[seq_start:seq_start+timesteps]
        y_seq_full[i] = y[seq_start+timesteps:seq_start+timesteps+horizon]
    y_seq_flat = y_seq_full.reshape(n_samples, horizon*n_outputs)
    return X_seq, y_seq_flat, y_seq_full
