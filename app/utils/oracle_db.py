import oracledb
from app.configs.oracle_conf import DB_USER, DB_PASSWORD, CONNECT_STRING, WALLET_LOCATION, WALLET_PASSWORD

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
	"""Run a SELECT and return all rows"""
	with get_connection() as conn:
		with conn.cursor() as cur:
			cur.execute(query, params or {})
			return cur.fetchall()

def fetch_one(query, params=None):
	"""Run a SELECT and return one row"""
	with get_connection() as conn:
		with conn.cursor() as cur:
			cur.execute(query, params or {})
			return cur.fetchone()

def execute_query(query, params=None):
	"""Run INSERT/UPDATE/DELETE and commit"""
	with get_connection() as conn:
		with conn.cursor() as cur:
			cur.execute(query, params or {})
			conn.commit()
			return cur.rowcount  # number of affected rows

# ---------- Quick test ----------
def test_connection():
	print("Testing connection...")
	try:
		result = fetch_one("SELECT * FROM PI_POINTS")
		if result:
			print(f"Connected successfully! Query result: {result[0]}")
		else: 
			print("No data found")
			
	except oracledb.Error as e:
		print(f"Could not connect to the database - Error occurred: {str(e)}")
