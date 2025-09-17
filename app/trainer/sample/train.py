import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, losses
import matplotlib.pyplot as plt

# 1. Generate synthetic dataset
np.random.seed(42)  # for reproducibility
ages = np.random.randint(20, 60, 100)   # ages between 20 and 60
print("ages", ages)
earnings = ages * 1000 + np.random.normal(0, 5000, 100)  # linear + noise
print("earnings", earnings)

ages = ages.astype("float32").reshape(-1, 1)
earnings = earnings.astype("float32").reshape(-1, 1)

# Normalize (important for stable training)
age_mean, age_std = ages.mean(), ages.std()
earnings_mean, earnings_std = earnings.mean(), earnings.std()

ages_norm = (ages - age_mean) / age_std
earnings_norm = (earnings - earnings_mean) / earnings_std

# 2. Build linear regression model
model = keras.Sequential([
    layers.Dense(1, input_shape=(1,))
])

model.compile(optimizer=keras.optimizers.SGD(learning_rate=0.01),
              loss=losses.MeanSquaredError())

# 3. Train
history = model.fit(ages_norm, earnings_norm, epochs=200, verbose=0)

# 4. Plot training fit
predicted_norm = model.predict(ages_norm)
predicted = predicted_norm * earnings_std + earnings_mean  # unnormalize

# plt.scatter(ages, earnings, label="Actual data")
# plt.plot(ages, predicted, color="red", label="Regression line")
# plt.xlabel("Age")
# plt.ylabel("Earnings")
# plt.legend()
# plt.show()

# 5. Save the model + normalization params
model.save("linear_regression_age_earnings.h5", include_optimizer=False)

# # Save normalization params separately
np.savez("scaler.npz",
         age_mean=age_mean, age_std=age_std,
         earnings_mean=earnings_mean, earnings_std=earnings_std)