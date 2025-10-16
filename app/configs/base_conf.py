from pydantic_settings import BaseSettings
import os
class Settings(BaseSettings):
    # Memisalkan saat ini adalah "2025-09-01 00:00:00". Fungsi akan mengambil record berdasarkan nilai ini kebelakang.
    # Kosongkan bila akan menggunakan waktu sekarang
    TIME_PRETEND: str = ""

    # berapa hari kebelakang dalam pengambilan data record, sesuaikan dengan model input.
    RECORD_BACK_DATE: int=7 

    # Berapa hari kebelakang yang akan diupload ke PI Vision
    UPLOAD_PREDICT_DAYS: int=7

    # Berapa task RECORD yang dikerjakan salam satu schedule. rekemdasi 5
    RECORD_PER_SESSION: int=8

    # Berapa task UPLOAD yang dikerjakan salam satu schedule. rekemdasi 2
    UPLOAD_PERSESION: int=1

    # Nama prefix sensor aktif
    SENSOR_NAME_QUERY: str = "SKR1%"
    SENSOR_NAME_QUERY_STAR: str = "SKR1*"
    PREDICT_UNIT: int = 1
    SENSOR_NAME_QUERY_VIBRATION: str = "SKR1.Generator%"

    # Flow
    # 1. Create Task
    # 1.a Membuat task untuk pemanggilan API Record tiap sensor

    # Berapa periode pemanggilan api dilakukan (dalam menit). 
    # Misalkan setiap 12 jam sekali maka dimasukan nilai 60 * 12. 
    # Dilakukan tiap jam maka dimasukan nilai 60
    RECORD_TIME_PERIOD: int = 720
    PREDICT_TIME_PERIOD: int = 720
    UPLOAD_TIME_PERIOD: int = 720

    # 1.b Membuat task untuk menjalankan model predict
    # 1.c Membuat task untuk menjalankan upload data prediksi ke PI Vision
    # 2. Execute Task
    # 2.a Memanggil API Record tiap sensor
    # 2.b Menjalankan model predict
    # 2.c Menjalankan upload data prediksi ke PI Vision

    # Mengaktifkan fungsi scheduler
    RUN_SCHEDULER: str = "true"

    # Pengaturan Database
    ORACLE_DB_USER: str =""
    ORACLE_DB_PASSWORD: str =""
    ORACLE_DB_HOST: str =""
    ORACLE_DB_PORT: str =""
    ORACLE_DB_SERVICE: str=""

    # Pengaturan PI Vision
    BASIC_AUTH_USERNAME: str =""
    BASIC_AUTH_PASSWORD: str =""
    DATA_SERVER_WEB_ID: str =""
    SAMPLE_WEB_ID: str =""
    URL_POINT_SEARCH: str =""
    URL_STREAM_INTERPOLATED : str =""
    INTERPOLATED_URL: str="https://pivision.plnindonesiapower.co.id/piwebapi/streams/"

    # Pengaturan OSISOF
    OSISOF_USER: str =""
    OSISOF_PASSWORD: str =""
    OSISOF_URL: str =""

    # Pengaturan Table
    TABLE_SENSORS: str = "ugm25_sensors"
    TABLE_RECORDS: str = "ugm25_records"
    TABLE_PREDICTIONS: str = "ugm25_predictions"
    TABLE_PRESKRIPTIONS: str = "ugm25_prescriptions"
    TABLE_TASKS: str = "ugm25_tasks"

    OUTPUT_DIR: str = "/Users/macbookpro/Documents/Projects/Pse/code/storage/unit1/v1"
    MODEL_NAME : str = "final_lstm_model.keras"
    SCALER_X_PATH_NAME: str = "scaler_X.save"
    SCALER_Y_PATH_NAME: str = "scaler_y.save"
    DATA_PATH_NAME: str = "Dataset.xlsx"
    TIMESTEPS: int = 2016
    HORIZON: int = 2016
    PREPARE_DATA: int = 7 # Berapa hari kebelakang yang akan di gunakan untuk prediksi

    MODEL_PATH: str = os.path.join(OUTPUT_DIR, MODEL_NAME)
    SCALER_X_PATH: str = os.path.join(OUTPUT_DIR, SCALER_X_PATH_NAME)
    SCALER_Y_PATH: str = os.path.join(OUTPUT_DIR, SCALER_Y_PATH_NAME)
    DATA_PATH: str = os.path.join(OUTPUT_DIR, DATA_PATH_NAME)


    class Config:
        env_file = ".env"

settings = Settings()
