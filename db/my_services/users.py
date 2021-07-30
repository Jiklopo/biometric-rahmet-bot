from sqlalchemy.orm import Session

from db import engine
from db.tables import User


def create_user(*, telegram_id, name='', kaspi='') -> User:
    with Session(engine) as session:
        user = User(
            telegram_id=telegram_id,
            name=name,
            kaspi=kaspi,
            state='UNNAMED'
        )
        session.add(user)
        session.commit()
        user = session.get(User, telegram_id)

    return user


def name_user(*, user: User, name: str) -> User:
    with Session(engine) as session:
        user.name = name
        session.add(user)
        session.commit()
        user = session.get(User, user.telegram_id)

    return user


def update_user_state(*, user: User, state: str) -> User:
    with Session(engine) as session:
        user.state = state
        session.add(user)
        session.commit()
        user = session.get(User, user.telegram_id)

    return user
