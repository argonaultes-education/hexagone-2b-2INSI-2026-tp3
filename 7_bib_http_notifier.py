from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import MappedAsDataclass
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy import String, Integer
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy import select
import requests
import time

class Singleton(type):
    
    __instance = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls.__instance:
            cls.__instance[cls] = super().__call__(*args, **kwargs)
        return cls.__instance[cls]

class Base(MappedAsDataclass, DeclarativeBase):
    ...


class Subscriber(Base):
    __tablename__ = 'subscribers'
    id: Mapped[int] = mapped_column(init=False, primary_key=True, autoincrement=True)
    address: Mapped[str] = mapped_column(String(15))
    port: Mapped[int] = mapped_column(Integer)
    #TODO constraint to check port > 0
    
    def to_json(self):
        return {
            'address': self.address,
            'port': self.port
        }


# def notify_decorator(func):
#     def inner_func(*inner_args, **inner_kwargs):
#         result = func(*inner_args, **inner_kwargs)
        
#         gl = GameLibrary()
#         gl.notify_subscribers(func.__name__)
#         return result
#     return inner_func

class NotificationLibrary(metaclass=Singleton):
    
    def __init__(self):
        self.__engine = create_engine('postgresql+psycopg2://postgres:password@localhost:5432/gameboard', pool_size=10, echo=True)
        Base.metadata.create_all(self.__engine)
        
    def subscribe(self, msg):
        client_address = msg['address']
        client_port = msg['port']
        result = None
        with Session(self.__engine) as session:
            subscriber = Subscriber(address=client_address, port=client_port)
            session.add(subscriber)
            session.commit()
            result = subscriber.to_json()
        return result

    def notify_subscribers(self, event):
        session = Session(self.__engine)
        statement = select(Subscriber)
        for subscriber in session.scalars(statement):
            target_address = subscriber.address
            target_port = subscriber.port
            try:
                requests.request(method="POST", url=f'http://{target_address}:{target_port}', json={'event': event})
                time.sleep(30)
            finally:
                print('notification sent')

def run():
    #TODO grpc server init
    ...

    
if __name__ == '__main__':
    run()