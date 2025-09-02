import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error
from tensorflow.keras import layers, callbacks, models
from tensorflow.keras.optimizers import Adam
from sklearn.metrics import r2_score
from tensorflow.keras import layers, models, regularizers
import sys

# ---------------- Config ----------------
DATA_PATH   = "files/Unit1Sample.xlsx"
INPUT_COLS  = ["SKR1.24VDC VOLTAGE BUSBAR A",
               "SKR1.24VDC VOLTAGE BUSBAR B",
               "SKR1.ACTIVE POWER U1",
               "SKR1.ACTIVE PWR",
               "SKR1.BUSBAR VOLTAGE",
              #  "SKR1.Current Inc To Trafo1",
               "SKR1.Current Inc To Trafo2",
              # "SKR1.Current Incoming From 5M",
              #  "SKR1.Current Out To As Pulau",
              #  "SKR1.Current Out To MV/LV TR1",
              #  "SKR1.Current Out To MV/LV TR2",
               "SKR1.Current Out To PH",
              #  "SKR1.Current Out To WTP",
              #  "SKR1.DIESEL 1 ACTIVE POWER",
            #    "SKR1.DIESEL 1 STATOR CURRENT",
               "SKR1.DIESEL 1 STATOR VOLTAGE",
              #  "SKR1.DIESEL 2 ACTIVE POWER",
            #    "SKR1.DIESEL 2 STATOR CURRENT",
              "SKR1.DIESEL 2 STATOR VOLTAGE",
               "SKR1.LOAD LIMITERPOSITION U 1",
               "SKR1.MDB Voltage Busbar A",
              #  "SKR1.MDB Voltage Busbar B",
              #  "SKR1.REACTIVE PWR UNIT 1",
               "SKR1.REACTIVE PWR UNIT 1 rev",
            #    "SKR1.REACTIVE POWER U1",
               "SKR1.ROTOR CURR UNIT 1",
              #  "SKR1.ROTOR CURR UNIT 1 rev",
              #  "SKR1.ROTOR VOLT UNIT 1",
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
              #  "SKR1.TURBINE SPEED DROP U1",
               "SKR1.Voltage Inc Fr 5MVA Traf",
              #  "SKR1.Voltage Out To As Pulau",
              #  "SKR1.Voltage Out To MV/LV TR1",
              #  "SKR1.Voltage Out To MV/LV TR2",
               "SKR1.WATER UPSTREAM PRESSURE",
               "SKR1.WICKET GATE POSITION",
               "SKR1.HOT AIR TEMPERATURE1 U1",
               "SKR1.HOT AIR TEMPERATURE2 U1",
               "SKR1.HOT AIR TEMPERATURE3 U1",
               "SKR1.HOT AIR TEMPERATURE4 U1",
               "SKR1.HOT AIR TEMPERATURE5 U1",
               "SKR1.HOT AIR TEMPERATURE6 U1",
               "DISCHARGE DEBIT UNIT 1"
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
               "SKR1.STATOR WIND TEMP6 U1"]
              #  "SKR1.UPPER VIBRASI HORIZONTAL",
              #  "SKR1.UPPER VIBRASI VERTIKAL",
              #  "SKR1.UPPER VIBRASI AXIAL",
              #  "SKR1.LOWER VIBRASI HORIZONTAL",
              #  "SKR1.LOWER VIBRASI VERTIKAL",
              #  "SKR1.LOWER VIBRASI AXIAL",
              #  "SKR1.TURBIN VIBRASI HORIZONTAL",
              #  "SKR1.TURBIN VIBRASI VERTIKAL",
              #  "SKR1.TURBIN VIBRASI AXIAL"]
TIMESTEPS   = 30            # berapa langkah untuk predict?
HORIZON     = 5           # predict berapa periode?
TEST_FRAC   = 0.15
VAL_FRAC    = 0.15
EPOCHS      = 10
BATCH_SIZE  = 128
LSTM_UNITS  = 128
DROPOUT     = 0.4
L2_REG      = 0.01 # Added L2 regularization parameter
# ----------------------------------------

# --- Load & INLINE Cleaning ---
df = pd.read_excel(DATA_PATH, index_col=0, parse_dates=True)
df = df.sort_index()
# Replace 'I/O Timeout' with NaN
df.replace('I/O Timeout', np.nan, inplace=True)
# Convert all columns to numeric, coercing errors
for col in df.columns:
    df[col] = pd.to_numeric(df[col], errors='coerce')
df = df.interpolate(method="time", limit_direction="both").ffill().bfill()

# --- Split by time ---
N = len(df)
n_test = int(np.floor(TEST_FRAC * N))
n_trainval = N - n_test
n_val = int(np.floor(VAL_FRAC * n_trainval))
n_train = n_trainval - n_val

df_train = df.iloc[:n_train]
df_val   = df.iloc[n_train:n_trainval]
df_test  = df.iloc[n_trainval:]


# --- Normalize (separate scalers for X and y) ---
scaler_X = StandardScaler().fit(df_train[INPUT_COLS].values)
scaler_y = StandardScaler().fit(df_train[TARGET_COLS].values)

print(scaler_y)
sys.exit()

X_train = scaler_X.transform(df_train[INPUT_COLS].values)
y_train = scaler_y.transform(df_train[TARGET_COLS].values)
X_val   = scaler_X.transform(df_val[INPUT_COLS].values)
y_val   = scaler_y.transform(df_val[TARGET_COLS].values)
X_test  = scaler_X.transform(df_test[INPUT_COLS].values)
y_test  = scaler_y.transform(df_test[TARGET_COLS].values)



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

Xtr, ytr_flat, ytr_full = build_sequences_multistep(X_train, y_train, TIMESTEPS, HORIZON)
Xva, yva_flat, yva_full = build_sequences_multistep(X_val,   y_val,   TIMESTEPS, HORIZON)
Xte, yte_flat, yte_full = build_sequences_multistep(X_test,  y_test,  TIMESTEPS, HORIZON)

# Model
n_targets = len(TARGET_COLS)
out_dim = HORIZON * n_targets
inputs = layers.Input(shape=(TIMESTEPS, Xtr.shape[2]))

# LSTM pertama dengan L2 Regularization
x = layers.LSTM(LSTM_UNITS, return_sequences=True, kernel_regularizer=regularizers.l2(L2_REG))(inputs)
x = layers.Dropout(DROPOUT)(x)

# LSTM kedua dengan L2 Regularization
x = layers.LSTM(LSTM_UNITS, return_sequences=False, kernel_regularizer=regularizers.l2(L2_REG))(x)
x = layers.Dropout(DROPOUT)(x)

# Dense layer dengan L2 Regularization
x = layers.Dense(128, activation="relu", kernel_regularizer=regularizers.l2(L2_REG))(x)
# Output layer biasanya tidak perlu regularizer
outputs = layers.Dense(out_dim)(x)

model = models.Model(inputs, outputs)
opt = Adam(learning_rate=5e-5)

model.compile(
    optimizer=opt,
    loss="mse")

cb = [
    callbacks.EarlyStopping(monitor="val_loss", patience=10, restore_best_weights=True),
    callbacks.ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=4, min_lr=1e-5),
    callbacks.ModelCheckpoint("best_lstm.keras", monitor="val_loss", save_best_only=True),
]

hist = model.fit(
    Xtr, ytr_flat,
    validation_data=(Xva, yva_flat),
    epochs=EPOCHS,
    batch_size=BATCH_SIZE,
    verbose=1,
    callbacks=cb
)

#Training curves
plt.figure()
plt.plot(hist.history.get("loss", []), label="loss")
plt.plot(hist.history.get("val_loss", []), label="val_loss")
plt.xlabel("Epoch")
plt.ylabel("Loss")
plt.title("Training Curves")
plt.legend()
plt.tight_layout()
plt.show()

#Evaluate on TEST (inverse transform to original scale)
y_pred_flat = model.predict(Xte)
y_pred_full_scaled = y_pred_flat.reshape(-1, HORIZON, n_targets)
y_true_full_scaled = yte_full  # (samples, H, n_targets)

def inverse_full(scaled_full):
    S, H, T = scaled_full.shape
    inv = np.zeros_like(scaled_full, dtype=np.float64)
    for h in range(H):
        inv[:, h, :] = scaler_y.inverse_transform(scaled_full[:, h, :])
    return inv

y_pred_full = inverse_full(y_pred_full_scaled)
y_true_full = inverse_full(y_true_full_scaled)

#Metrics per-horizon untuk semua target
metrics_by_horizon = {}

for h in range(HORIZON):
    h_key = f"H+{h+1}"
    metrics_by_horizon[h_key] = {}
    yt_h = y_true_full[:, h, :]   # (S, n_targets)
    yp_h = y_pred_full[:, h, :]   # (S, n_targets)

    # agregat lintas target
    mae_all  = float(np.mean(np.abs(yt_h - yp_h)))
    rmse_all = float(np.sqrt(np.mean((yt_h - yp_h)**2)))
    mape_all = float(np.mean(np.abs((yt_h - yp_h) / np.maximum(np.abs(yt_h), 1e-8))) * 100)
    r2_all   = float(r2_score(yt_h, yp_h, multioutput='uniform_average'))

    metrics_by_horizon[h_key]["__ALL__"] = {
        "MAE": mae_all, "RMSE": rmse_all, "MAPE%": mape_all, "R2": r2_all
    }

    # per target
    for j, col in enumerate(TARGET_COLS):
        y_t = yt_h[:, j]
        y_p = yp_h[:, j]
        mae  = float(np.mean(np.abs(y_t - y_p)))
        rmse = float(np.sqrt(np.mean((y_t - y_p)**2)))
        mape = float(np.mean(np.abs((y_t - y_p) / np.maximum(np.abs(y_t), 1e-8))) * 100)
        r2   = float(r2_score(y_t, y_p)) if np.var(y_t) > 0 else float('nan')
        metrics_by_horizon[h_key][col] = {"MAE": mae, "RMSE": rmse, "MAPE%": mape, "R2": r2}

# ====== METRIK PER-TARGET, DI-AGREGASI MELINTAS SEMUA HORIZON ======
# y_true_full, y_pred_full shape: (S, H, T) -> ratakan H
S, H, T = y_true_full.shape
yt_all = y_true_full.reshape(S*H, T)   # (S*H, T)
yp_all = y_pred_full.reshape(S*H, T)   # (S*H, T)

per_target_metrics = []
for j, col in enumerate(TARGET_COLS):
    y_t = yt_all[:, j]
    y_p = yp_all[:, j]
    mae  = float(np.mean(np.abs(y_t - y_p)))
    rmse = float(np.sqrt(np.mean((y_t - y_p)**2)))
    mape = float(np.mean(np.abs((y_t - y_p) / np.maximum(np.abs(y_t), 1e-8))) * 100)
    r2   = float(r2_score(y_t, y_p)) if np.var(y_t) > 0 else float('nan')
    per_target_metrics.append({"Target": col, "MAE": mae, "RMSE": rmse, "MAPE%": mape, "R2": r2})

per_target_df = pd.DataFrame(per_target_metrics).set_index("Target").sort_index()

# print("\nMetrik per-target DI SEMUA HORIZON (dibulatkan 3 desimal):")
# print(per_target_df.round(3))

#Cetak ringkas
print("\nPer-horizon metrics (ALL targets, ringkas):")
for h_key in metrics_by_horizon:
    agg = metrics_by_horizon[h_key]["__ALL__"]
    print(f"{h_key}: MAE={agg['MAE']:.3f}  RMSE={agg['RMSE']:.3f}  MAPE%={agg['MAPE%']:.2f}  R2={agg['R2']:.3f}")

#Comparison plots: Train & Test
def series_from_windows(y_full, index_base, start_idx):
    S, H, T = y_full.shape
    idx = index_base[start_idx:start_idx+S]
    series = {}
    for j, col in enumerate(TARGET_COLS):
        series[col] = (idx, y_full[:, 0, j])
    return series

# TRAIN series
train_index = df_train.index
train_series_true = series_from_windows(inverse_full(ytr_full), train_index, TIMESTEPS)
train_series_pred = series_from_windows(inverse_full(model.predict(Xtr).reshape(-1, HORIZON, n_targets)),
                                        train_index, TIMESTEPS)

# TEST series
test_index = df_test.index
test_series_true = series_from_windows(y_true_full, test_index, TIMESTEPS)
test_series_pred = series_from_windows(y_pred_full, test_index, TIMESTEPS)


# --- Forecast the next periods ---
X_all = scaler_X.transform(df[INPUT_COLS].values)
last_window = X_all[-TIMESTEPS:]
next_flat = model.predict(last_window[np.newaxis, ...])[0]
next_full_scaled = next_flat.reshape(HORIZON, n_targets)

next_full = np.zeros_like(next_full_scaled, dtype=np.float64)
for h in range(HORIZON):
    next_full[h, :] = scaler_y.inverse_transform(next_full_scaled[h, :].reshape(1, -1))[0]

# Build next timestamps

offset = pd.tseries.frequencies.to_offset("5T")  # 5 minutes fixed
timestamps = [df.index[-1] + offset*(h+1) for h in range(HORIZON)]
forecast_df = pd.DataFrame(next_full, index=pd.Index(timestamps, name="timestamp"), columns=TARGET_COLS)
print(f"\nForecast for the next {HORIZON} periods (original scale):")
print(forecast_df)


timestamps = [df.index[-1] + offset*(h+1) for h in range(HORIZON)]
forecast_df = pd.DataFrame(next_full, index=pd.Index(timestamps, name="timestamp"), columns=TARGET_COLS)
print("\nForecast :")
print(forecast_df)

