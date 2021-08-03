from sqlalchemy.orm import Session

from db.tables import User, Order


def get_user(*, session: Session, telegram_id: int) -> User:
    user = session.get(User, telegram_id)
    return user


def get_all_users_from_orders(*, session: Session, order: Order) -> list[User]:
    session.add(order)
    users = [order.user]
    users += order.joined_users
    return users


def list_users(session: Session) -> list[User]:
    users = session.query(User).all()
    return users
