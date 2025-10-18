import oracledb
from app.configs.base_conf import settings

_pool = None  # global pool instance

def init_pool():
    global _pool
    dsn = f"{settings.ORACLE_DB_HOST}:{settings.ORACLE_DB_PORT}/{settings.ORACLE_DB_SERVICE}"

    _pool = oracledb.create_pool(
        user=settings.ORACLE_DB_USER,
        password=settings.ORACLE_DB_PASSWORD,
        dsn=dsn,
        min=1,
        max=5,
        increment=1
    )

    return _pool

def get_connection():
    if _pool is None:
        init_pool()
    return _pool.acquire()

# ---------- Generic query helpers ----------
def fetch_all(query, params=None):
    # Run a SELECT and return all rows as list of dicts (with field names)
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params or {})
            columns = [col[0] for col in cur.description]  # extract column names
            rows = cur.fetchall()
            return [dict(zip(columns, row)) for row in rows]


def fetch_one(query, params=None):
    # Run a SELECT and return one row as a dict (with field names)
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params or {})
            row = cur.fetchone()
            if row is None:
                return None
            columns = [col[0] for col in cur.description]
            return dict(zip(columns, row))

def execute_query(query, params=None):
	
	try:
		with get_connection() as conn:
			with conn.cursor() as cur:
				cur.execute(query, params or {})
				
				if query.strip().lower().startswith("select"):
					result = cur.fetchall()
					return result

				conn.commit()
				return cur.rowcount
	except Exception as e:
		print("❌ Error executing query")
		print(e)
		raise

# ---------- Quick test ----------
def test_connection():
	print("Testing connection...")
	try:
		result = fetch_all("SELECT * FROM " + settings.TABLE_SENSORS)
		if result:
			print(f"Database Connected successfully!")
			if len(result) > 0:
				print(f"Total data sensors : {len(result)}") 
		else:
			print("No data found")
			
	except oracledb.Error as e:
		print(f"Could not connect to the database - Error occurred: {str(e)}")
		print("DB Service: ",settings.ORACLE_DB_SERVICE)
