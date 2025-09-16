from dotenv import load_dotenv
import os

print("Run oracle_conf.py")
load_dotenv()
DB_USER = os.getenv("ORACLE_DB_USER")
DB_PASSWORD = os.getenv("ORACLE_DB_PASSWORD")
CONNECT_STRING = os.getenv("ORACLE_CONNECT_STRING")
WALLET_LOCATION = os.getenv("ORACLE_WALLET_LOCATION")
WALLET_PASSWORD = os.getenv("ORACLE_WALLET_PASSWORD")