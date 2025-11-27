from datetime import datetime
import os
from app.configs.base_conf import settings
import string
import random

def write_log(logname: str, content: str, key: str = None, mode: str = "INFO"):
    if settings.APP_MODE == "DEV":
        print(content)
        return
    
    if key == None:
        key = gen_key(6)
    
    # ensure log directory exists
    if not os.path.exists("logs"):
        os.makedirs("logs")

    # create filename based on logname + today's date
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"{logname}_{date_str}.log"

    filepath = os.path.join("logs", filename)

    # timestamp for each log entry
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # write log
    with open(filepath, "a") as f:
        f.write(f"[{timestamp}] {mode} - {key}: {content}\n")

def gen_key(length = 6):
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))
