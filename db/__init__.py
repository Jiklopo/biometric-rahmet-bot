import sqlalchemy
from os import getenv
from dotenv import load_dotenv

load_dotenv()

engine = sqlalchemy.create_engine(getenv('DATABASE_URL'), echo=True, future=True)
