import socketserver
import json
from dataclasses import dataclass, field

#https://docs.python.org/3/library/sqlite3.html
#1 point bonus pour tous ceux qui parviennet à implémenter la persistance de données via SQLite

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

    def list_gameboards(self, msg):
        return list(map(lambda x: x.to_json(), self.gameboards))
           

class BibHandler(socketserver.BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        # self.request is the TCP socket connected to the client
        pieces = [b'']
        total = 0
        while b'\n' not in pieces[-1] and total < 10_000:
            pieces.append(self.request.recv(2000))
            total += len(pieces[-1])
        self.data = b''.join(pieces)
        print(f"Received from {self.client_address[0]}:")
        msg_str = self.data.decode("utf-8")
        print(f"Msg received: {msg_str}")
        msg = json.loads(msg_str)

        gl = GameLibrary()
        actions = {
            'h': lambda : print('Help'),
            'c': gl.create_new_gameboard,
            'd': gl.delete_gameboard,
            'l': gl.list_gameboards
        }
        input_action = msg['action']
        result = actions[input_action](msg)


        # just send back the same data, but upper-cased
        self.request.sendall(json.dumps(result).encode('utf-8')) #FIXME
        # after we return, the socket will be closed.

if __name__ == "__main__":
    HOST, PORT = "localhost", 9999

    # Create the server, binding to localhost on port 9999
    with socketserver.TCPServer((HOST, PORT), BibHandler) as server:
        # Activate the server; this will keep running until you
        # interrupt the program with Ctrl-C
        server.serve_forever()