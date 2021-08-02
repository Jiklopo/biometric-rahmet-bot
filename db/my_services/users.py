from sqlalchemy.orm import Session

from db import engine
from db.tables import User


def create_user(*, telegram_id: int, username=None, name=None, kaspi=None) -> User:
    with Session(engine) as session:
        user = User(
            telegram_id=telegram_id,
            username=username,
            name=name,
            kaspi=kaspi
        )
        session.add(user)
        session.commit()
        session.refresh(instance=user)

    return user


def update_user(*, user: User, username=None, name=None, state=None, kaspi=None) -> User:
    with Session(engine) as session:
        session.add(user)
        user.username = username or user.username
        user.name = name or user.name
        user.state = state or user.state
        user.kaspi = kaspi or user.kaspi
        session.commit()
        session.refresh(instance=user)

    return user
