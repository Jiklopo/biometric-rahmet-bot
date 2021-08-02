from sqlalchemy.orm import Session

from db import engine
from db.tables import Product, Order


def create_product(*, name: str, price=None) -> Product:
    with Session(engine) as session:
        product = Product(name=name, price=price)
        session.add(product)
        session.commit()
        session.refresh(instance=product)

    return product
