from sqlalchemy.orm import Session

from db import engine
from db.tables import Order, Product


def create_order(*, user_id) -> Order:
    with Session(engine) as session:
        order = Order(user_id=user_id)
        session.add(order)
        session.commit()
        session.refresh(instance=order)

    return order


def add_order_product(*, order: Order, product: Product) -> Order:
    with Session(engine) as session:
        session.add(product)
        session.add(order)
        order.products.append(product)
        session.commit()
        session.refresh(instance=order)
        session.refresh(instance=product)

    return order


def finish_order(*, order: Order) -> Order:
    with Session(engine) as session:
        session.add(order)
        order.is_finished = True
        session.commit()
        session.refresh(instance=order)

    return order


def append_text_to_order(*, order: Order, text: str) -> Order:
    with Session(engine) as session:
        session.add(order)
        order.text += text
        session.commit()
        session.refresh(instance=order)

    return order
