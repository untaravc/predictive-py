from dotenv import load_dotenv
import os

load_dotenv()

OSISOF_USER = os.getenv("OSISOF_USER")
OSISOF_PASSWORD = os.getenv("OSISOF_PASSWORD")
OSISOF_URL = os.getenv("OSISOF_URL")