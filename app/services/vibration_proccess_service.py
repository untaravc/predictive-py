import pathlib
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from scipy.interpolate import UnivariateSpline
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
from sklearn.metrics import (
    r2_score, 
    mean_absolute_error, 
    root_mean_squared_error, 
    mean_absolute_percentage_error)

from app.utils.oracle_db import execute_query, fetch_all
# from app.configs.oracle_conf import TABLE_SENSORS, TABLE_RECORDS
from app.services.generator_service import build_merge_query
from app.configs.base_conf import settings

def process_excel(df):
    # Fungsi ini untuk mencari folder Preprocessing Data
    base = pathlib.Path(__file__).parent
    base_dir = base.parent.parent / "storage" / "vibration1"
    # Siapkan list untuk menampung objek Column
    features = []

    # Sortir kolom
    for column in df.columns.to_list():
        if column != "Timestamp":
            timestamp = df["Timestamp"].to_numpy()

            values = df[column].to_numpy()

            feature = Column(column, values, timestamp)
            features.append(feature)


    # Buat dictionary untuk menampung hasil prediksi
    interpolation_dict = {}
    regression_dict = {}

    # Buat array untuk menyimpan performa model
    poly_results = []

    # Proses kolom yang sudah disortir
    for feature in features:
        interpolated_values = None
        regression_values = None

        # Bersihkan nilai NaN 
        clean_values = clean_data(feature.values, feature.values)

        # Simpan nilai waktu dari data-data yang bukan NaN
        clean_times = clean_data(feature.values, feature.times)

        # Bersihkan nama kolom
        title = f"{feature.name}"

        # Buat lokasi penyimpanan untuk grafik

        # Interpolasi 
        interpolated_values = feature.PiecewisePolynomial(clean_times, clean_values, feature.times)

        # Regresi
        regression_values, result = feature.PolynomialRegression(feature.times, interpolated_values, feature.times)

        # Simpan performa model
        poly_results.append(result)

        # Pisahkan data dengan timestamp yang berbeda
        timestamp_key = tuple(feature.timestamp)
        if timestamp_key not in interpolation_dict:
            interpolation_dict[timestamp_key] = {"Timestamp" : timestamp_key}

        interpolation_dict[timestamp_key][title] = interpolated_values

        timestamp_key = tuple(feature.timestamp)
        if timestamp_key not in regression_dict:
            regression_dict[timestamp_key] = {"Timestamp" : timestamp_key}

        regression_dict[timestamp_key][title] = regression_values

    # pd.DataFrame(poly_results).to_excel(os.path.join(tuning_result_dir, "Poly Results.xlsx"), index=False)
    flattened_data = []
    for timestamp_key, data_dict in regression_dict.items():
        df = pd.DataFrame(data_dict)

        # Ensure timestamp column is string
        # Convert to datetime first (in case it's string or Excel format)
        df["Timestamp"] = pd.to_datetime(df["Timestamp"])

        # Format to Oracle-style: 2025-07-01T00:00:00Z
        df["Timestamp"] = df["Timestamp"].dt.strftime("%Y-%m-%dT%H:%M:%S")

        # Melt to long format
        long_df = df.melt(id_vars=["Timestamp"], var_name="Name", value_name="Value")

    # Convert to list of dicts
    flattened_data.extend(long_df.to_dict(orient="records"))
    
    sensors = fetch_all("SELECT * FROM "+ settings.TABLE_SENSORS +" WHERE NAME like +'" + settings.SENSOR_NAME_QUERY_VIBRATION + "' AND IS_ACTIVE = 1 AND ID < 1000")
    for sensor in sensors:
        filtered = [item for item in flattened_data if item["Name"] == sensor["NAME"]]
        for i, chunk in enumerate(chunk_list(filtered, 500), start=1):
            print(f"Processing batch {i} ({len(chunk)} records)")
            query, params = build_merge_query(settings.TABLE_RECORDS, sensor["ID"], chunk)
            execute_query(query, params)

    return len(sensors)

## Functions ======
def chunk_list(data, size):
    for i in range(0, len(data), size):
        yield data[i:i + size]

def clean_data(masking_list, masked_list):
    valid_mask = ~np.isnan(masking_list)
    return masked_list[valid_mask]

class Column() :
    def __init__(self,name, values, timestamp):
        self.name = name
        self.values = values
        self.timestamp = timestamp
        self.times = np.arange(0, (len(self.timestamp)) * 5, 5)

    # Fungsi ini untuk interpolasi data
    @staticmethod
    def PiecewisePolynomial(x_fit, y_fit, x_predict) :
        model = UnivariateSpline(x_fit, y_fit, s=0, k=1)

        y_predict = model(x_predict)

        return y_predict
    
    
    # Fungsi ini untuk regresi pada data yang sedikit
    def PolynomialRegression(self, x_fit, y_fit, x_predict):

        # Tentukan orde polinomial yang ingin dicoba
        degrees = np.arange(0, 53)

        # Buat scaler 
        x_scaler = StandardScaler()
        y_scaler = StandardScaler()
       
        # Normalisasi data
        x_fit_scaled = x_scaler.fit_transform(x_fit.reshape(-1, 1))
        y_fit_scaled = y_scaler.fit_transform(np.log1p(y_fit).reshape(-1, 1)).flatten()

        # Siapkan dictionary untuk menampung parameter terbaik
        result = {

                    "Column" : f"{self.name}",
                    "Polynomial Degree" : None,
                    "R2 Score" : None,
                    "MAE Score" : None,
                    "RMSE Score" : None,
                    "MAPE Score" : None

                }
        
        # Atur skor terbaik pada nilai 0 terlebih dahulu
        best_score = 0

        # Proses semua orde yang ingin dicoba
        for degree in degrees:
            poly = PolynomialFeatures(degree=degree)
            X_poly = poly.fit_transform(x_fit_scaled)

            model = LinearRegression()
            model.fit(X_poly, y_fit_scaled)

            y_test = model.predict(X_poly)
            y_test = np.expm1(y_scaler.inverse_transform(y_test.reshape(-1, 1)).flatten())

            # Evaluasi model
            r2 = r2_score(y_fit, y_test)
            mae = mean_absolute_error(y_fit, y_test)
            rmse = root_mean_squared_error(y_fit, y_test)
            mape = mean_absolute_percentage_error(y_fit, y_test)

            # print(f"\t--> Polynomial Degree : {degree}; R2 Score : {r2}")

            # Ganti model lama dengan model terbaru, jika skor r2 meningkat
            if r2 >= best_score:
                result["Polynomial Degree"] = degree
                result["R2 Score"] = r2
                result["MAE Score"] = mae
                result["RMSE Score"] = rmse
                result["MAPE Score"] = mape

                best_score = r2

        
        # Setelah dapat orde terbaik lakukan prediksi
        poly = PolynomialFeatures(degree=result["Polynomial Degree"])
        X_poly = poly.fit_transform(x_fit_scaled)

        model = LinearRegression()
        model.fit(X_poly, y_fit_scaled)

        x_predict_scaled = x_scaler.transform(x_predict.reshape(-1, 1))
        X_poly_new = poly.transform(x_predict_scaled)

        y_predicted = model.predict(X_poly_new)
        y_predicted = np.expm1(y_scaler.inverse_transform(y_predicted.reshape(-1, 1)).flatten())

        return y_predicted, result