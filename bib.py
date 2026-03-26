from dataclasses import dataclass, field

class Singleton(type):
    
    __instance = None
    
    def __call__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__call__(*args, **kwargs)
        return cls.__instance

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
        
@dataclass
class GameLibrary:
    gameboards: set[GameBoard] = field(default_factory=set)

    def create_new_gameboard(self):
        title = input('Title: ')
        author = input('Author: ')
        price = float(input('Price: '))
        self.gameboards.add(GameBoard(title, author, price))

    def delete_gameboard(self):
        id_to_delete = int(input('Id to delete: '))
        self.gameboards = set(filter(lambda gameboard: id_to_delete != gameboard.id, self.gameboards))

    def list_gameboards(self):
        print(self.gameboards)
        
if __name__ == '__main__':
    
    #TODO: ask user action and do it
    gl = GameLibrary()
    actions = {
        'h': lambda : print('Help'),
        'c': gl.create_new_gameboard,
        'd': gl.delete_gameboard,
        'l': gl.list_gameboards
    }
    while True:
        input_action = input('Action: ')
        actions[input_action]()
        