from sqlalchemy.orm import Session

from db import engine
from db.tables import Product


def get_product(*, product_id) -> Product:
    with Session(engine) as session:
        product = session.get(Product, product_id)

    return product
