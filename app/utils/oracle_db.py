import oracledb
from app.configs.base_conf import settings

_pool = None  # global pool instance

def init_pool():
    global _pool
    # oracledb.defaults.thin = True
    # oracledb.init_oracle_client()
    # print(settings)
    # if _pool is None:
    #     # dsn = f"//{settings.ORACLE_DB_HOST}:{settings.ORACLE_DB_PORT}/{settings.ORACLE_DB_SERVICE}"  # classic EZConnect syntax
    dsn = f"{settings.ORACLE_DB_HOST}:{settings.ORACLE_DB_PORT}/{settings.ORACLE_DB_SERVICE}"
        # dsn = oracledb.makedsn(settings.ORACLE_DB_HOST, settings.ORACLE_DB_PORT, service_name=settings.ORACLE_DB_SERVICE)

    _pool = oracledb.create_pool(
        user=settings.ORACLE_DB_USER,
        password=settings.ORACLE_DB_PASSWORD,
        dsn=dsn,
        # min=1,
        # max=5,
        # increment=1
    )

    # _pool = oracledb.connect(
    #     user=settings.ORACLE_DB_USER,
    #     password=settings.ORACLE_DB_PASSWORD,
    #     dsn=dsn  # contoh: "192.168.1.10:1521/ORCLPDB1"
    # )

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
