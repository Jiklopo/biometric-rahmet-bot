from sqlalchemy.orm import Session

from db.tables import Product


def create_product(*, session: Session, name: str, price=None) -> Product:
    product = Product(name=name, price=price)
    session.add(product)
    session.commit()
    session.refresh(instance=product)

    return product
