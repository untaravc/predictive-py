import sys
import os
import glob
import asyncpg
import asyncio

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
    "database": DB_NAME,
    "user": DB_USER,
    "password": DB_PASSWORD,
    "host": DB_HOST,
    "port": DB_PORT,
}

def run_migration(direction: str):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    migration_path = os.path.join(base_dir, f"*.{direction}.sql")
    migration_files = sorted(glob.glob(migration_path))

    if not migration_files:
        print(f"⚠️ No migration files found for direction: {direction}")
        return

    conn = None
    try:
        conn = await asyncpg.connect(**db_config)

        for file_path in migration_files:
            with open(file_path, "r") as f:
                sql_commands = f.read()

            try:
                with conn.transaction():
                    await conn.execute(sql_commands)
                print(f"✅ Applied {direction.upper()} migration: {os.path.basename(file_path)}")
            except Exception as e:
                print(f"❌ Failed migration {file_path}: {e}")
                break
    finally:
        if conn:
            await conn.close()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python migrate.py <up|down>")
        sys.exit(1)

    direction = sys.argv[1].lower()
    if direction not in ("up", "down"):
        print("❌ Direction must be 'up' or 'down'")
        sys.exit(1)

    asyncio.run(run_migration(direction))