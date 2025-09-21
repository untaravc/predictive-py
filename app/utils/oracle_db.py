import oracledb
from app.configs.oracle_conf import DB_USER, DB_PASSWORD, CONNECT_STRING, WALLET_LOCATION, WALLET_PASSWORD, TABLE_SENSORS

_pool = None  # global pool instance

def init_pool():
	global _pool
	if _pool is None:
		_pool = oracledb.create_pool(
			config_dir=WALLET_LOCATION,
			user=DB_USER,
			password=DB_PASSWORD,
			dsn=CONNECT_STRING,
			wallet_location=WALLET_LOCATION,
			wallet_password=WALLET_PASSWORD
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
	# Run INSERT/UPDATE/DELETE and commit
	with get_connection() as conn:
		with conn.cursor() as cur:
			cur.execute(query, params or {})
			conn.commit()
			return cur.rowcount

# ---------- Quick test ----------
def test_connection():
	print("Testing connection...")
	try:
		result = fetch_one("SELECT * FROM " + TABLE_SENSORS)
		if result:
			print(f"Connected successfully! Query result: {result[0]}")
		else: 
			print("No data found")
			
	except oracledb.Error as e:
		print(f"Could not connect to the database - Error occurred: {str(e)}")
