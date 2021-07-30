from sqlalchemy import Column, String, ForeignKey, Table, Integer, Float, DateTime, Boolean
from sqlalchemy.orm import registry, relationship
from datetime import datetime

from db import engine

mapper_registry = registry()
Base = mapper_registry.generate_base()

order_product_association = Table(
    'orders_product',
    mapper_registry.metadata,
    Column('order_id', ForeignKey('orders.id'), primary_key=True),
    Column('product_id', ForeignKey('products.id'), primary_key=True)
)


class User(Base):
    __tablename__ = 'telegram_users'

    telegram_id = Column(String(32), primary_key=True)
    name = Column(
        String,
        default=''
    )
    # Maybe phone number or card number
    kaspi = Column(
        String(16),
        default=''
    )
    state = Column(String(10))
    orders = relationship('Order', back_populates='user')

    def __repr__(self):
        return f'User<{self.telegram_id}>(name={self.name} kaspi={self.kaspi} state={self.state})'


class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True, autoincrement=True)

    is_finished = Column(Boolean, default=False)

    user_id = Column(String, ForeignKey('telegram_users.telegram_id'))
    user = relationship(
        'User',
        back_populates='orders'
    )

    products = relationship(
        'Product',
        secondary=order_product_association
    )

    messages = relationship(
        'OrderMessage',
        back_populates='order'
    )

    def __repr__(self):
        return f'Order<{self.id}>(products={self.products} is_finished={self.is_finished} user_id={self.user_id}'


class OrderMessage(Base):
    __tablename__ = 'order_messages'

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    chat_id = Column(
        String,
        ForeignKey('telegram_users.telegram_id')
    )

    order_id = Column(
        Integer,
        ForeignKey('orders.id')
    )
    order = relationship(
        'Order',
        back_populates='messages'
    )

    message_id = Column(String(64))

    def __repr__(self):
        return f'OrderMessage<{self.id}>(order_id={self.order_id} chat_id={self.chat_id} message_id={self.message_id})'


class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True)
    price = Column(Float, nullable=True)
    updated_at = Column(DateTime, onupdate=datetime.now, default=datetime.now)
    added_by = Column(String, ForeignKey('telegram_users.telegram_id'))
    orders = relationship(
        'Order',
        secondary=order_product_association,
        back_populates='products'
    )

    def __repr__(self):
        return f'Product<{self.id}>(name={self.name} price={self.price})'


def create_tables():
    mapper_registry.metadata.create_all(engine)


if __name__ == '__main__':
    create_tables()
