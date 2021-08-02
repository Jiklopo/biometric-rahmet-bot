from sqlalchemy.orm import Session

from db.tables import OrderText


def get_order_texts(*, session: Session, user_id: int, order_id: int) -> list[OrderText]:
    texts = session.query(OrderText).filter(OrderText.user_id == user_id, OrderText.order_id == order_id).all()
    return texts
