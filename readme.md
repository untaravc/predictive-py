# Documentation

## Run Development Service
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

# WORKFLOW
- Run Schedule task maker
- Run Schedule record
- Run Schedule model
- Run Schedule upload to pivision

## Environment Set
- RUN_SCHEDULER="false" -> change to "true" to active schedule function