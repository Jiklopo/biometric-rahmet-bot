import sqlalchemy
from os import getenv
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = getenv('DATABASE_URL')

if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres', 'postgresql+psycopg2')

engine = sqlalchemy.create_engine(DATABASE_URL, echo=True, future=True)
