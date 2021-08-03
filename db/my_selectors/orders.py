from sqlalchemy.orm import Session

from db import engine
from db.tables import Order


def get_order(*, session: Session, order_id: int) -> Order:
    order = session.get(Order, order_id)
    return order


def get_user_orders(*, session: Session, user_id: int) -> list[Order]:
    orders = session.query(Order).filter(Order.user_id == user_id).all()
    return orders


def get_active_user_order(*, session: Session, user_id: int) -> Order:
    orders = session.query(Order).filter(Order.user_id == user_id, Order.is_finished == False).all()
    order = None
    if orders:
        order = orders.pop()

    return order


def get_group_order(*, session: Session, group_id: int) -> Order:
    orders = session.query(Order).filter(Order.chat_id == group_id, Order.is_finished == False).all()
    order = None
    if orders:
        order = orders.pop()

    return order
