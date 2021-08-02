from sqlalchemy.orm import Session

from db.tables import User
import phonenumbers


def create_user(*, session: Session, telegram_id: int, username=None, name=None, kaspi=None) -> User:
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


def update_user(*, session: Session, user: User, username=None, name=None, state=None, kaspi=None) -> User:
    session.add(user)
    user.username = username or user.username
    user.name = name or user.name
    user.state = state or user.state
    user.kaspi = beautify_kaspi(kaspi) or user.kaspi
    session.commit()
    session.refresh(instance=user)

    return user


def delete_user(*, session: Session, user: User):
    session.add(user)
    session.delete(user)
    session.commit()


def beautify_kaspi(kaspi: str):
    if kaspi:
        new_kaspi = ''
        if len(kaspi) == 16:
            for i in range(1, 5):
                new_kaspi += kaspi[(i - 1) * 4:i * 4] + ' '
            new_kaspi = new_kaspi.strip()

        elif len(kaspi) == 12:
            ph = phonenumbers.parse(kaspi, None)
            new_kaspi = phonenumbers.format_number(ph, phonenumbers.PhoneNumberFormat.NATIONAL)

        return new_kaspi
    return kaspi
