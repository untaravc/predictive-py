from fastapi import Request
from tensorflow import keras
import numpy as np

async def home():
    return {
        "success": True,
        "result": {
            "title": "Predictive Prescriptive PLN Indonesia Power - UGM 2025.",
            "version": "0.1",
            "last_update": "2025-10-10",
            "features": [
                "Prediksi 2 Minggu",
            ]
        },
    }