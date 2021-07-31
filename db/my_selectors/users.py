from sqlalchemy.orm import Session

from db import engine
from db.tables import User, Order


def get_user(*, telegram_id) -> User:
    with Session(engine) as session:
        user = session.get(User, telegram_id)

    return user


def get_all_users_from_orders(*, order: Order) -> list[User]:
    with Session(engine) as session:
        session.add(order)
        users = [order.user]
        users += order.joined_users

    return users


def list_users() -> list[User]:
    with Session(engine) as session:
        users = session.query(User).all()

    return users
