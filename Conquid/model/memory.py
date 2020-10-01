from model.state import *

class History:
    """
    Represents the entire history of moves and board states in a game
    To obtain a list of Boards in a game, call
        <history>.board__history()
    To obtain a list of Moves in game, call
        <history>.move__history()

    ***Remember, if a board is the (i)th state in the board history,
    then the last move done is the (i-1)th action in the move history
    """
    def __init__(self, rows, cols, bases):
        self.rows = rows
        self.cols = cols
        self.bases = bases
        self.moves = []

    def store(self, move):
        self.moves.append(move.__dict__)

    def move_history(self):
        return [Move(**mv) for mv in self.moves]

    def board_history(self):
        # starting state
        board = Board(self.rows, self.cols, self.bases)
        # update boards with moves to generate list
        boards = [board.copy()]
        for mv in self.moves:
            Move(**mv).execute(board)
            boards.append(board.copy())
        return boards

class Cache:
    """
    Stores the current Board state and current player.
    For a move to be executed, entered into history, and the turn to change, the following calls must be made:

    1.  <cache>.receive(<move>) must be provided with a move to execute.
        It is possible for the move to be invalid, in which case it will be rejected and
        an InvalidMove exception will be raised from the method.

    2.  Once a valid move is entered, it may be undone by calling <cache>.undo()
        If ones wishes to confirm the move and begin the next turn, call <cache>.confirm()
        If the confirmed move is a valid conquest, confirm method will return a value of True
        to indicate the game is won by the current player

    The BoardView class must have a method with signature
        BoardView.set_view(self, <board>)
    thru which it receives updated boards to be displayed

    The BoardView class must also have a method with signature
        BoardView.set_player(self, <player>, win=False)
    thru which it receives the current player whose turn it is and whether they won yet.
    """
    def __init__(self, history: History, controller: 'Controller'):
        self.hist = history
        self.controller = controller
        self.current_player = 1
        self.nstate = 0
        self.latest = history.board_history()[0]
        self.save = self.latest.copy()
        self.move = None

    def play_back(self):
        if self.nstate > 0:
            self.nstate -= 1
            self.current_player = 3 - self.current_player
        self.boardview.set_view(self.boards[self.nstate])
        self.boardview.set_player(self.current_player)

    def play_forward(self):
        if self.nstate < len(self.boards)-1:
            self.nstate += 1
            self.current_player = 3 - self.current_player
        self.boardview.set_view(self.boards[self.nstate])
        self.boardview.set_player(self.current_player)
        if self.nstate == len(self.boards)-1:
            self.boardview.set_player(3 - self.current_player, win=True)

    def receive(self, move: Move):
        if not self.move:
            move.execute(self.latest, validate=True)
            self.boardview.set_view(self.latest)
            self.move = move

    def undo(self):
        self.latest = self.save.copy()
        self.boardview.set_view(self.latest)
        self.move = None

    def confirm(self):
        if self.move:
            self.save = self.latest.copy()
            self.hist.store(self.move)
            self.nstate += 1
            self.current_player = 3 - self.current_player
            if self.move.type == 'Q':
                self.controller.game_won()
                self.boards = self.hist.board_history()
                self.play_forward()
            else:
                self.boardview.set_player(self.current_player)
            self.move = None
