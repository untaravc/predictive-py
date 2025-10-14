import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):

# Pengaturan Aplikasi

# Nama prefix sensor aktif
    SENSOR_NAME_QUERY: str = "SKR1%"
    SENSOR_NAME_QUERY_STAR: str = "SKR1*"
    PREDICT_UNIT: int = 1
    SENSOR_NAME_QUERY_VIBRATION: str = "SKR1%"

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

    RUN_SCHEDULER: str = "true"

    ORACLE_DB_USER: str =""
    ORACLE_DB_PASSWORD: str =""
    ORACLE_DB_HOST: str =""
    ORACLE_DB_PORT: str =""
    ORACLE_DB_SERVICE: str=""

    BASIC_AUTH_USERNAME: str =""
    BASIC_AUTH_PASSWORD: str =""
    DATA_SERVER_WEB_ID: str =""
    SAMPLE_WEB_ID: str =""
    URL_POINT_SEARCH: str =""
    URL_STREAM_INTERPOLATED : str =""

    OSISOF_USER: str =""
    OSISOF_PASSWORD: str =""
    OSISOF_URL: str =""

    TABLE_SENSORS: str = "ugm25_sensors"
    TABLE_RECORDS: str = "ugm25_records"
    TABLE_PREDICTIONS: str = "ugm25_predictions"
    TABLE_PRESKRIPTIONS: str = "ugm25_prescriptions"
    TABLE_TASKS: str = "ugm25_tasks"
    class Config:
        env_file = ".env"

settings = Settings()
