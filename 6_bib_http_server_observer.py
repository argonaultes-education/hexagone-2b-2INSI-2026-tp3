import json
from http.server import HTTPServer, BaseHTTPRequestHandler, HTTPStatus
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import MappedAsDataclass
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy import String, Float, Integer
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy import select
import requests

class Singleton(type):
    
    __instance = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls.__instance:
            cls.__instance[cls] = super().__call__(*args, **kwargs)
        return cls.__instance[cls]

class Base(MappedAsDataclass, DeclarativeBase):
    ...

#TODO
# client subscribed stored in a table :
# * address
# * port
# * protocol (http)

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


class GameBoard(Base):
    __tablename__ = 'gameboards'
    id: Mapped[int] = mapped_column(init=False, primary_key=True, autoincrement=True, )
    title: Mapped[str] = mapped_column(String(50))
    author: Mapped[str] = mapped_column(String(30))
    price: Mapped[float] = mapped_column(Float)
        
    def to_json(self):
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'price': self.price
        }


#add a new feature with the design pattern decorator
        
class GameLibrary(metaclass=Singleton):
    
    def __init__(self):
        self.__engine = create_engine('postgresql+psycopg2://postgres:password@localhost:5432/gameboard', echo=True)
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

    def create_new_gameboard(self, msg):
        title = msg['title']
        author = msg['author']
        price = msg['price']
        result = None
        with Session(self.__engine) as session:
            gameboard = GameBoard(author=author, title=title, price=price)
            session.add(gameboard)
            session.commit()
            result = gameboard.to_json()
        return result

    def delete_gameboard(self, msg):
        id_to_delete = msg['id_to_delete']
        session = Session(self.__engine)
        req = select(GameBoard).where(GameBoard.id == id_to_delete)
        gameboard_to_delete = session.scalar(req)
        session.delete(gameboard_to_delete)
        session.commit()
        return {'status': 'OK'}

    def list_gameboards(self):
        session = Session(self.__engine)
        statement = select(GameBoard)
        result = []
        for gameboard in session.scalars(statement):
            result.append(gameboard.to_json())
        return result
    
    # put into thread to avoid to wait
    def notify_subscribers(self):
        session = Session(self.__engine)
        statement = select(Subscriber)
        for subscriber in session.scalars(statement):
            target_address = subscriber.address
            target_port = subscriber.port
            requests.request(method="GET", url=f'http://{target_address}:{target_port}')

def notify_decorator(func, *args, **kwargs):
    def inner_func():
        func(*args, **kwargs)
        gl = GameLibrary()
        gl.notify_subscribers()
    return inner_func

class BibHttpHandler(BaseHTTPRequestHandler):
    
    #TODO: add a way to subscribe
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def set_header(self, result):
        result_json = json.dumps(result)
        enc = 'UTF-8'
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-type", "text/json; charset=%s" % enc)
        self.send_header("Content-Length", str(len(result_json)))
        self.end_headers()
        return result_json
    
    # list the created gameboards
    def do_GET(self):
        print(f'Path: {self.path}')
        print(f'Request: {self.requestline}')
        gl = GameLibrary()
        result = gl.list_gameboards()
        result_json = self.set_header(result)
        self.wfile.write(result_json.encode('utf-8'))
        
        
    # create a gameboard
    @notify_decorator
    def do_POST(self):
        path = self.path
        length = self.headers.get('Content-Length')
        msg = self.rfile.read(int(length))
        msg_obj = json.loads(msg)
        gl = GameLibrary()
        if path == '/subscribe':
            result = gl.subscribe(msg_obj)
        else:
            result = gl.create_new_gameboard(msg_obj)
        result_json = self.set_header(result)
        self.wfile.write(result_json.encode('utf-8'))
        
    # delete a gameboard
    @notify_decorator
    def do_DELETE(self):
        length = self.headers.get('Content-Length')
        msg = self.rfile.read(int(length))
        gl = GameLibrary()
        result = gl.delete_gameboard(json.loads(msg))
        result_json = self.set_header(result)
        self.wfile.write(result_json.encode('utf-8'))
    

def run(server_class=HTTPServer, handler_class=BibHttpHandler):
    server_address = ('127.0.0.1', 8000)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()
    
if __name__ == '__main__':
    run()