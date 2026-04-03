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
import grpc
from gameboard_pb2 import SubscribeResponse, NotifyResponse
from gameboard_pb2_grpc import SubscribeServiceServicer
import gameboard_pb2_grpc
from concurrent import futures

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
            'id': self.id,
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

class NotificationLibrary(SubscribeServiceServicer):
    
    def __init__(self):
        self.__engine = create_engine('postgresql+psycopg2://postgres:password@localhost:5432/notification', pool_size=10, echo=True)
        Base.metadata.create_all(self.__engine)
        
    def Subscribe(self, request, context):
        client_address = request.ip #ClientSubscriber
        client_port = request.port #ClientSubscriber
        result = None
        with Session(self.__engine) as session:
            subscriber = Subscriber(address=client_address, port=client_port)
            session.add(subscriber)
            session.commit()
            result = subscriber.to_json()
        return SubscribeResponse(
            id=result['id'], ip=result['address'], port=result['port'])

    def Notify(self, request, context):
        session = Session(self.__engine)
        event = request.event #EventNotification
        statement = select(Subscriber)
        for subscriber in session.scalars(statement):
            target_address = subscriber.address
            target_port = subscriber.port
            try:
                requests.request(method="POST", url=f'http://{target_address}:{target_port}', json={'event': event})
                time.sleep(2)
            finally:
                print('notification sent')
        return NotifyResponse(status='OK')

def run():
    port = "50051"
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    gameboard_pb2_grpc.add_SubscribeServiceServicer_to_server(NotificationLibrary(), server)
    server.add_insecure_port("[::]:" + port)
    server.start()
    print("Server started, listening on " + port)
    server.wait_for_termination()
    
if __name__ == '__main__':
    run()