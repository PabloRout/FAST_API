import databases
import sqlalchemy
from config import config

metadata = sqlalchemy.MetaData()

engine = sqlalchemy.create_engine(
    config.DATABASE_URL, connect_args={}
)