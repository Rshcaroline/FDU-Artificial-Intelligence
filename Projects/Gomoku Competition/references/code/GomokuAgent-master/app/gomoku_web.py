#/usr/bin/env python
import gomoku

class Gomoku_Web(gomoku.Gomoku):
    """ Gomoku Game Rules:
    Two players alternatively put their stone on the board. First one got five in a row wins.
    """
    def __init__(self, board_size=15, players=None, silent_mode=False, winning_num=5):
        self.reset()
        self.board_size = board_size
        self.fastmode = None
        self.playing = None
        self.silent_mode = silent_mode
        if players:
            self.players = [Player(player_name) for player_name in players]
        else:
            self.players = []
        self.last_move = None
        self.first_center = None
        self.winning_num = winning_num

    def reset(self):
        self.board = (set(),set())
        self.i_turn = 0
        self.hist_moves = []
        self.winning_stones = set()

    def web_play(self, action):
        """ Controling the game play by the web function call"""
        self.playing = self.i_turn % 2
        current_player = self.players[self.playing]
        if action == (0, 0):
            print("Player %s admit defeat!" % current_player.name)
        self.last_move = action
        if self.place_stone() is False:
            return
        self.hist_moves.append(self.last_move) # for undo
        winner = self.check_winner()
        if not self.silent_mode:
            self.print_board()
        if winner is not None:
            print("##########    %s is the WINNER!    #########" % current_player.name)
            return None, winner
        self.i_turn += 1
        if self.i_turn == self.board_size ** 2:
            print("This game is a Draw!")
            return None, "Draw"

        next_action = self.check_next_ai()
        return next_action, winner

    def check_next_ai(self):
        """ check if the next move is AI """
        self.playing = self.i_turn % 2
        current_player = self.players[self.playing]
        if current_player.is_ai:
            action = current_player.strategy(self.state)
            return action
        return None

    def undo(self):
        """ Undo opponent's last move and my last move """
        if len(self.hist_moves) == 0: return
        opponent = int(not self.playing)
        opponent_last_move = self.hist_moves.pop()
        self.board[opponent].remove(opponent_last_move)
        if len(self.hist_moves) == 0: return
        my_last_move = self.hist_moves.pop()
        self.board[self.playing].remove(my_last_move)
        print("Undo!")
        if not self.silent_mode:
            self.print_board()


class Player(gomoku.Player):
    def __init__(self, name, ai_script=None, level=None):
        self.name = name
        # search for the strategy file
        if ai_script is not None:
            print('Loading AI script %s'%ai_script)
            p = __import__(ai_script)
            try:
                self.strategy = p.strategy
            except:
                raise RuntimeError("Function strategy(state) is not found in %s"%ai_script)
            try:
                self.finish = p.finish
            except:
                pass
            self.is_ai = True
            if level:
                p.estimate_level = level
        else:
            self.is_ai = False
