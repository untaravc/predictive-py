from fastapi import Request
from tensorflow import keras
import numpy as np

async def predict_earning(request: Request):
    model = keras.models.load_model("app/trainer/sample/linear_regression_age_earnings.h5", compile=False)
    scaler = np.load("app/trainer/sample/scaler.npz")
    age_mean, age_std = scaler["age_mean"], scaler["age_std"]
    earnings_mean, earnings_std = scaler["earnings_mean"], scaler["earnings_std"]

    ages_str = request.query_params.get("ages", "")
    
    # 2. Ubah string → list int
    ages = np.array([int(a) for a in ages_str.split(",") if a.strip()], dtype="float32")
    
    # 3. Reshape jadi (n,1)
    new_ages = ages.reshape(-1, 1)

    # 4. Normalisasi input
    new_ages_norm = (new_ages - age_mean) / age_std

    # 5. Prediksi (masih normalisasi)
    predictions_norm = model.predict(new_ages_norm)

    # 6. Balik ke skala asli
    predictions = predictions_norm * earnings_std + earnings_mean

    return {
        "success": True,
        "result": [float(p) for p in predictions.flatten()]
    }