
from dotenv import load_dotenv
import os

print("Run ind_power_conf.py")

load_dotenv()
DATA_SERVER_WEB_ID = os.getenv("DATA_SERVER_WEB_ID")
URL_POINT_SEARCH= os.getenv("URL_POINT_SEARCH")
URL_STREAM_INTERPOLATED= os.getenv("URL_STREAM_INTERPOLATED")