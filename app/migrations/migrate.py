import psycopg2
import sys
import os
import glob

# Database connection settings
from dotenv import load_dotenv

load_dotenv()
import os
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

db_config = {
    "dbname": DB_NAME,
    "user": DB_USER,
    "password": DB_PASSWORD,
    "host": DB_HOST,
    "port": DB_PORT
}

def run_migration(direction):
    """
    Execute all migration files in the migrations folder for a given direction.
    direction: 'up' or 'down'
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    migration_path = os.path.join(base_dir, f"*.{direction}.sql")

    migration_files = sorted(glob.glob(migration_path))

    if not migration_files:
        print(f"⚠️ No migration files found for direction: {direction}")
        return

    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()

        for file_path in migration_files:
            with open(file_path, "r") as f:
                sql_commands = f.read()

            try:
                cursor.execute(sql_commands)
                conn.commit()
                print(f"✅ Applied {direction.upper()} migration: {os.path.basename(file_path)}")
            except Exception as e:
                conn.rollback()
                print(f"❌ Failed migration {file_path}: {e}")
                break

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python migrate.py <up|down>")
        sys.exit(1)

    direction = sys.argv[1].lower()
    if direction not in ("up", "down"):
        print("❌ Direction must be 'up' or 'down'")
        sys.exit(1)

    run_migration(direction)