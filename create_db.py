import psycopg2
from urllib.parse import urlparse, urlunparse
from config import Config

parsed = urlparse(Config.SQLALCHEMY_DATABASE_URI)
db_name = parsed.path.lstrip("/")

# Connect to the default 'postgres' db, keeping SSL params intact
postgres_uri = urlunparse(parsed._replace(path="/postgres"))

conn = psycopg2.connect(postgres_uri)
conn.autocommit = True
cur = conn.cursor()
cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
if not cur.fetchone():
    cur.execute(f'CREATE DATABASE "{db_name}"')
    print(f"Database '{db_name}' created.")
else:
    print(f"Database '{db_name}' already exists.")
conn.close()
