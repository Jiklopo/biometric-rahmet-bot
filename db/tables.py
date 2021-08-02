from sqlalchemy import Column, String, ForeignKey, Table, Integer, BigInteger, Float, DateTime, Boolean
from sqlalchemy.orm import registry, relationship
from datetime import datetime

from db import engine
from db.states import UserStates

mapper_registry = registry()
Base = mapper_registry.generate_base()

order_product_association = Table(
    'orders_products',
    mapper_registry.metadata,
    Column('order_id', ForeignKey('orders.id'), primary_key=True),
    Column('product_id', ForeignKey('products.id'), primary_key=True)
)

user_order_association = Table(
    'users_orders',
    mapper_registry.metadata,
    Column('user_id', ForeignKey('telegram_users.telegram_id'), primary_key=True),
    Column('order_id', ForeignKey('orders.id'), primary_key=True)
)


class User(Base):
    __tablename__ = 'telegram_users'

    telegram_id = Column(BigInteger, primary_key=True)
    username = Column(String(32), default='')
    name = Column(String, default='')
    # Maybe phone number or card number
    kaspi = Column(String(16), default='')
    state = Column(String(10), default=UserStates.CREATED.value)
    orders = relationship('Order', back_populates='user')

    def __repr__(self):
        return f'User<{self.telegram_id}>(name={self.name} kaspi={self.kaspi} state={self.state})'


class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True, autoincrement=True)

    text = Column(String, default='')

    is_finished = Column(Boolean, default=False)
    chat_id = Column(BigInteger, default='')
    message_id = Column(BigInteger, default='')

    user_id = Column(BigInteger, ForeignKey('telegram_users.telegram_id'))
    user = relationship('User', back_populates='orders')

    joined_users = relationship('User', secondary=user_order_association)

    products = relationship('Product', secondary=order_product_association)

    def __repr__(self):
        return f'Order<{self.id}>(products={self.products} is_finished={self.is_finished} author_id={self.user_id}'


class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True)
    price = Column(Float, default=0)
    updated_at = Column(DateTime, onupdate=datetime.now, default=datetime.now)
    updated_by = Column(BigInteger, ForeignKey('telegram_users.telegram_id'))
    orders = relationship('Order', secondary=order_product_association, back_populates='products')

    def __repr__(self):
        return f'Product<{self.id}>(name={self.name} price={self.price})'


def create_tables():
    mapper_registry.metadata.create_all(engine)


if __name__ == '__main__':
    create_tables()
