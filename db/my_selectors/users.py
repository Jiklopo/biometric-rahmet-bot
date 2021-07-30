from sqlalchemy.orm import Session

from db import engine
from db.tables import User


def get_user(*, telegram_id) -> User:
    with Session(engine) as session:
        user = session.get(User, telegram_id)

    return user


def list_users() -> list[User]:
    with Session(engine) as session:
        users = session.query(User).all()

    return users
