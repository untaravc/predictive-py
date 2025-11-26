from datetime import datetime
import os

def write_log(logname: str, content: str, log_dir: str = "logs"):
    # ensure log directory exists
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # create filename based on logname + today's date
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"{logname}_{date_str}.log"

    filepath = os.path.join(log_dir, filename)

    # timestamp for each log entry
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # write log
    with open(filepath, "a") as f:
        f.write(f"[{timestamp}] {content}\n")
