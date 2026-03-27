import json
from http.server import HTTPServer, BaseHTTPRequestHandler, HTTPStatus
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import MappedAsDataclass
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy import String, Float
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy import select

class Singleton(type):
    
    __instance = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls.__instance:
            cls.__instance[cls] = super().__call__(*args, **kwargs)
        return cls.__instance[cls]

class Base(MappedAsDataclass, DeclarativeBase):
    ...


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
        
class GameLibrary(metaclass=Singleton):
    
    def __init__(self):
        self.__engine = create_engine('postgresql+psycopg2://postgres:password@localhost:5432/gameboard', echo=True)
        Base.metadata.create_all(self.__engine)

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



class BibHttpHandler(BaseHTTPRequestHandler):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    # list the created gameboards
    def do_GET(self):
        gl = GameLibrary()
        result = gl.list_gameboards()
        result_json = json.dumps(result)
        enc = 'UTF-8'
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-type", "text/json; charset=%s" % enc)
        self.send_header("Content-Length", str(len(result_json)))
        self.end_headers()
        self.wfile.write(result_json.encode('utf-8'))
        
        
    # create a gameboard
    def do_POST(self):
        length = self.headers.get('Content-Length')
        msg = self.rfile.read(int(length))
        gl = GameLibrary()
        result_json = gl.create_new_gameboard(json.loads(msg))
        result = json.dumps(result_json)
        self.send_response(HTTPStatus.OK)
        enc = 'UTF-8'
        self.send_header("Content-type", "text/json; charset=%s" % enc)
        self.send_header("Content-Length", str(len(result)))
        self.end_headers()        
        self.wfile.write(result.encode(enc))
        
    # delete a gameboard
    def do_DELETE(self):
        length = self.headers.get('Content-Length')
        msg = self.rfile.read(int(length))
        gl = GameLibrary()
        result_json = gl.delete_gameboard(json.loads(msg))
        result = json.dumps(result_json)
        self.send_response(HTTPStatus.OK)
        enc = 'UTF-8'
        self.send_header("Content-type", "text/json; charset=%s" % enc)
        self.send_header("Content-Length", str(len(result)))
        self.end_headers()        
        self.wfile.write(result.encode(enc))
    

def run(server_class=HTTPServer, handler_class=BibHttpHandler):
    server_address = ('127.0.0.1', 8000)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()
    
if __name__ == '__main__':
    run()