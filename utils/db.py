import os
from dotenv import load_dotenv
import sqlalchemy as sa

load_dotenv()

def get_engine():
    dsn = (
        f"postgresql://{os.getenv('PGUSER')}:{os.getenv('PGPASSWORD')}"
        f"@{os.getenv('PGHOST')}:{os.getenv('PGPORT')}/{os.getenv('PGDATABASE')}"
    )
    return sa.create_engine(dsn)