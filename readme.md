# Documentation

### create .venv
    python3 -m venv .venv

### activate .venv
    source venv/bin/activate

### Check if venv is active
    which python3

### Run development mode
    fastapi dev main.py
    uvicorn app.main:app --reload

### Run DB Migrations MySQL
    chmod +x app/migrations/table_migrations.py
    ./table_migrations.py

### Update requirements.txt
    pip freeze > requirements.txt
    pip install -r requirements.txt

#### Migration V2
    python app/migrations/migrate.py up
    python app/migrations/migrate.py down 

# Feature
- db connection
- table migration
- api service

## upcoming
- data polling
- runing model
- graph show
- cron