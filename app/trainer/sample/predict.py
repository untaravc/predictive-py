import numpy as np
from tensorflow import keras

# 1. Load model and scaler
model = keras.models.load_model("linear_regression_age_earnings.h5", compile=False)
scaler = np.load("scaler.npz")

age_mean, age_std = scaler["age_mean"], scaler["age_std"]
earnings_mean, earnings_std = scaler["earnings_mean"], scaler["earnings_std"]

# 2. Predict for new ages
new_ages = np.array([[25], [30]], dtype="float32")

# Normalize inputs
new_ages_norm = (new_ages - age_mean) / age_std

# Predict (in normalized space)
predictions_norm = model.predict(new_ages_norm)

# # Unnormalize predictions
# predictions = predictions_norm * earnings_std + earnings_mean

# # 3. Show results
# for age, earning in zip(new_ages.flatten(), predictions.flatten()):
#     print(f"Age {age:.0f} → Predicted earning: ${earning:,.2f}")