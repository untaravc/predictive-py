from dotenv import load_dotenv
import os

load_dotenv()

DB_USER = os.getenv("ORACLE_DB_USER")
DB_PASSWORD = os.getenv("ORACLE_DB_PASSWORD")
CONNECT_STRING = os.getenv("ORACLE_CONNECT_STRING")
WALLET_LOCATION = os.getenv("ORACLE_WALLET_LOCATION")
WALLET_PASSWORD = os.getenv("ORACLE_WALLET_PASSWORD")
DB_HOST= os.getenv("ORACLE_DB_HOST")
DB_PORT= os.getenv("ORACLE_DB_PORT")
DB_SERVICE= os.getenv("ORACLE_DB_SERVICE")

TABLE_SENSORS = "ugm25_sensors"
TABLE_RECORDS = "ugm25_records"
TABLE_PREDICTIONS = "ugm25_predictions"
TABLE_PRESKRIPTIONS = "ugm25_prescriptions"
TABLE_TASKS = "ugm25_tasks"