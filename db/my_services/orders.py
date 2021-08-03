from sqlalchemy.orm import Session

from db.states import UserStates
from db.tables import Order, User, OrderText


def create_order(*, session: Session,  user_id: int, chat_id: int, message_id: int) -> Order:
    order = Order(user_id=user_id, chat_id=chat_id, message_id=message_id)
    session.add(order)
    session.commit()
    session.refresh(instance=order)

    return order


# def add_order_product(*, session: Session,  order: Order, product: Product) -> Order:
#     session.add(product)
#     session.add(order)
#     order.products.append(product)
#     session.commit()
#     session.refresh(instance=order)
#     session.refresh(instance=product)
#
#     return order


def finish_order(*, session: Session,  order: Order) -> Order:
    session.add(order)

    order.is_finished = True

    order.user.state = UserStates.REGISTERED.value
    for u in order.joined_users:
        u.state = UserStates.REGISTERED.value

    session.commit()
    session.refresh(instance=order)

    return order


def append_text_to_order(*, session: Session, order: Order, updated_by: User, text: str) -> Order:
    session.add(order)
    session.add(updated_by)

    if updated_by.telegram_id == order.user.telegram_id or updated_by in order.joined_users:
        order_text = OrderText(
            user_id=updated_by.telegram_id,
            order_id=order.id,
            text=text
        )
        session.add(order_text)

    session.commit()
    session.refresh(instance=order)
    print('1' * 100)
    print(order.texts)

    return order


def add_joined_user(*, session: Session, order: Order, user: User) -> Order:
    session.add(order)
    session.add(user)

    if user.telegram_id != order.user_id and user not in order.joined_users:
        order.joined_users.append(user)

    session.commit()
    session.refresh(instance=order)

    return order
