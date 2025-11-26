from pydantic_settings import BaseSettings
import os
class Settings(BaseSettings):
    # Mengaktifkan fungsi scheduler
    RUN_SCHEDULER: str = "true"
    # Memisalkan saat ini adalah "2025-09-01 00:00:00". Fungsi akan mengambil record berdasarkan nilai ini kebelakang.
    # Isi "" bila akan menggunakan waktu sekarang
    TIME_PRETEND: str = ""
    BASE_PATH: str = ""

    # berapa hari kebelakang dalam pengambilan data record, sesuaikan dengan model input.
    RECORD_BACK_DATE: int=21

    # Berapa hari kebelakang yang akan diupload ke PI Vision
    UPLOAD_PREDICT_DAYS: int=7

    # Berapa task RECORD yang dikerjakan salam satu schedule. rekemdasi 5
    RECORD_PER_SESSION: int=4

    # Berapa task UPLOAD yang dikerjakan salam satu schedule. rekemdasi 1
    UPLOAD_PERSESION: int=1
    UPLOAD_MAX_PERSESION: int=4

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
    # INTERPOLATED_URL: str="https://pivision.plnindonesiapower.co.id/piwebapi/streams/"
    # INTERPOLATED_URL: str="https://piwebapi2.plnindonesiapower.co.id/piwebapi/streams/"
    INTERPOLATED_URL: str="https://piwebapi.plnindonesiapower.co.id/piwebapi/streams/"

    # Pengaturan OSISOF
    OSISOF_USER: str =""
    OSISOF_PASSWORD: str =""
    OSISOF_URL: str ="https://piwebapi.plnindonesiapower.co.id/piwebapi"
    # OSISOF_URL: str ="https://piwebapi2.plnindonesiapower.co.id/piwebapi"
    # OSISOF_URL: str ="https://piwebapi-pool.plnindonesiapower.co.id/piwebapi"
    # OSISOF_URL: str ="https://pivision.plnindonesiapower.co.id/piwebapi/"

    # Pengaturan Table
    TABLE_SENSORS: str = "ugm25_sensors"
    TABLE_RECORDS: str = "ugm25_records"
    TABLE_PREDICTIONS: str = "ugm25_predictions"
    TABLE_PRESKRIPTIONS: str = "ugm25_prescriptions"
    TABLE_TASKS: str = "ugm25_tasks"

    TIMESTEPS: int = 2016
    HORIZON: int = 2016
    PREPARE_DATA: int = 21 # Berapa hari kebelakang yang akan di gunakan untuk prediksi

    OUTPUT_DIR: str = ""
    MODEL_PATH: str = ""
    SCALER_X_PATH: str = ""
    SCALER_Y_PATH: str = ""

    VIBRATION_FOLDER_PATH: str = ""

    # Schedule Period
    CRON_CREATE_TASK_RECORD: str = "0 0 * * *" # Default: Pembuatan task perhari apa 00:00
    CRON_CREATE_TASK_PREDICT: str = "0 0 * * *" # Default: Pembuatan task perhari apa 00:00
    CRON_CREATE_TASK_UPLOAD: str = "0 0 * * *" # Default: Pembuatan task perhari apa 00:00
    
    CRON_EXECUTE_RECORD_API: str = "* * * * *" # Default per menit akan menjalankan task download sesuai RECORD_PER_SESSION
    CRON_EXECUTE_PREDICT: str = "0 0 * * *" # Default per jam akan menjalankan predict
    CRON_EXECUTE_UPLOAD: str = "*/10 * * * *" # Default per 10 menit akan menjalankan upload sesuai UPLOAD_PERSESION
    CRON_EXECUTE_UPLOAD_MAX: str = "* * * * *" # Default: Pembuatan task per menit

    class Config:
        env_file = ".env"

settings = Settings()
