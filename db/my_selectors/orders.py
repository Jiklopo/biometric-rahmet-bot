from sqlalchemy.orm import Session

from db import engine
from db.tables import Order


def get_order(*, order_id) -> Order:
    with Session(engine) as session:
        order = session.get(Order, order_id)

    return order


def get_user_orders(*, user_id) -> list[Order]:
    with Session(engine) as session:
        orders = session.query(Order).filter(Order.user_id == user_id).all()

    return orders


def get_active_user_order(*, user_id) -> Order:
    with Session(engine) as session:
        orders = session.query(Order).filter(Order.user_id == user_id, Order.is_finished == False).all()
        order = orders.pop()

    return order
