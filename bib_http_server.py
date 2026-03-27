import json
from dataclasses import dataclass, field
from http.server import HTTPServer, BaseHTTPRequestHandler, SimpleHTTPRequestHandler, HTTPStatus


class Singleton(type):
    
    __instance = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls.__instance:
            cls.__instance[cls] = super().__call__(*args, **kwargs)
        return cls.__instance[cls]

class GameBoardSequence(metaclass=Singleton):
    def __init__(self):
        self.__next_id = 0
    
    @property
    def next_id(self):
        self.__next_id += 1
        return self.__next_id

@dataclass(unsafe_hash=True)
class GameBoard:
    id: int = field(init=False)
    title: str
    author: str
    price: float
    
    def __post_init__(self):
        self.id = GameBoardSequence().next_id
        
    def to_json(self):
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'price': self.price
        }
        
@dataclass
class GameLibrary(metaclass=Singleton):
    gameboards: set[GameBoard] = field(default_factory=set)       

    def create_new_gameboard(self, msg):
        title = msg['title']
        author = msg['author']
        price = msg['price']
        gameboard = GameBoard(author=author, title=title, price=price)
        self.gameboards.add(gameboard)
        return gameboard.to_json()

    def delete_gameboard(self, msg):
        id_to_delete = msg['id_to_delete']
        self.gameboards = set(filter(lambda gameboard: id_to_delete != gameboard.id, self.gameboards))
        return {'status': 'OK'}

    def list_gameboards(self):
        return list(map(lambda x: x.to_json(), self.gameboards))



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