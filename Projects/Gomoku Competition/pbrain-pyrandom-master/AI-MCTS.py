# @Author: Shihan Ran
# @Date: 2018-06-06 16:43:00
# @Description: This is MCTS Gomoku AI. 
# @Email: rshcaroline@gmail.com
# @Software: VSCode
# @License: Copyright(C), Fudan University


import random
import pisqpipe as pp
from pisqpipe import DEBUG_EVAL, DEBUG

pp.infotext = 'name="AI-template", author="Shihan Ran", version="1.0", country="China"'

MAX_BOARD = 100
his_moves = []         # a list recording history moves
his_players = []       # a list recording history players
board = [[0 for i in range(MAX_BOARD)] for j in range(MAX_BOARD)]

def brain_init():
    """
    Initiate the board, the board size must be in set [5, MAX_BOARD].
    """
    if pp.width < 5 or pp.height < 5:
        pp.pipeOut("ERROR size of the board")
        return
    if pp.width > MAX_BOARD or pp.height > MAX_BOARD:
        pp.pipeOut("ERROR Maximal board size is {}".format(MAX_BOARD))
        return
    pp.pipeOut("OK")


def brain_restart():
    """
    Restart the game, set all squares to zero.
    """
    for x in range(pp.width):
        for y in range(pp.height):
            board[x][y] = 0
    pp.pipeOut("OK")


def isFree(x, y):
    """
    Return a bool value indicating if (x, y) square is free.
    """
    return x >= 0 and y >= 0 and x < pp.width and y < pp.height and board[x][y] == 0


def brain_update(x, y, player):
    """
    A function written by me.
    Update board, his_moves, his_players.
    """
    board[x][y] = player
    his_moves.append((x,y))
    his_players.append(player)


def brain_my(x, y):
    """
    I take a move.
    """
    if isFree(x,y):
        brain_update(x, y, 1)
    else:
        pp.pipeOut("ERROR my move [{},{}]".format(x, y))


def brain_opponents(x, y):
    """
    Opponents take a move.
    """
    if isFree(x,y):
        brain_update(x, y, 2)
    else:
        pp.pipeOut("ERROR opponents's move [{},{}]".format(x, y))


def brain_block(x, y):
    """
    I don't know what is block...???
    It seems irrelevant with us. Since it means square [x,y] belongs to a winning line (when info_continuous is 1).
    """
    if isFree(x,y):
        board[x][y] = 3
    else:
        pp.pipeOut("ERROR winning move [{},{}]".format(x, y))


def brain_takeback(x, y):
    """
    Take back a move. You cheat!
    :return 0: success, 1: not supported, 2: error
    """
    if x >= 0 and y >= 0 and x < pp.width and y < pp.height and board[x][y] != 0:
        board[x][y] = 0
        return 0
    return 2


def brain_random():
    """
    Randomly take a move.
    For Gomoku game, MCTS starts with a chess board and walk chess randomly until the end.
    """
    if pp.terminateAI:
        return
    i = 0
    while True:
        x = random.randint(0, pp.width)
        y = random.randint(0, pp.height)
        i += 1
        if pp.terminateAI:
            return
        if isFree(x,y):
            break
    if i > 1:
        pp.pipeOut("DEBUG {} coordinates didn't hit an empty field".format(i))
    pp.do_mymove(x, y)


class brain_MCTS(object):
    """
    AI player.
    """

    def __init__(self, time=pp.info_timeout_turn, max_actions=1000):
        # do some parameters initialize
        self.player = 1 if his_players[-1]==2 else 2      # if the last move is done by player2
        self.calculation_time = float(time/1000)          # unit: s    
        self.max_actions = max_actions                    # max simulations times
        self.confident = 1.96      
        self.equivalence = 10000                          # calc beta
        self.max_depth = 1

        # dicts for simulation recording
        self.plays = {}         # key:(player, move), value:visited times
        self.wins = {}          # key:(player, move), value:win times
        self.plays_rave = {}    # key:move, value:visited times
        self.wins_rave = {}     # key:move, value:{player: win times}


    def get_action(self):
        # import packages
        import copy
        import time

        # do some parameters initialize
        simulations = 0    
        begin = time.time()    # record time, we can't exceed the restricted time
        while time.time() - begin < self.calculation_time:
            board_copy = copy.deepcopy(board)    # simulation will change board's states
            his_moves_copy = copy.deepcopy(his_moves)
            his_players_copy = copy.deepcopy(his_players)
            self.run_simulation(board_copy, his_moves_copy, his_players_copy)
            simulations += 1

        action = self.select_one_move()
        return action


    def run_simulation(self, board_copy, his_moves_copy, his_players_copy):
        """
        MCTS main process
        """
        # import packages
        from random import choice, shuffle
        from math import log, sqrt
        import itertools

        # parameter initialize
        plays = self.plays
        wins = self.wins
        plays_rave = self.plays_rave
        wins_rave = self.wins_rave

        player = 1 if his_players[-1]==2 else 2
        availables = [(i, j) for i, j in itertools.product(range(pp.width), range(pp.height)) if board_copy[i][j]==0]
        visited_states = set()
        winner = -1
        expand = True

        # Simulation begin, we will go through max_actions times simulations
        for t in range(1, self.max_actions + 1):
            # Step1: Selection
            # If all moves have statistics info, choose one that have max UCB value
            if all(plays.get((player, move)) for move in availables):
                value, move = max(
                    ((1 - sqrt(self.equivalence / (3 * plays_rave[move] + self.equivalence))) * 
                    (wins[(player, move)] / plays[(player, move)]) +
                     sqrt(self.equivalence / (3 * plays_rave[move] + self.equivalence)) * 
                     (wins_rave[move][player] / plays_rave[move]) +
                     sqrt(self.confident * log(plays_rave[move]) / plays[(player, move)]), move)
                    for move in availables)    # UCT RAVE
            else:
                # a simple strategy
                # prefer to choose the nearer moves without statistics,
                # and then the farthers.
                # try to add statistics info to all moves quickly
                adjacents = []
                if len(availables) > 5:
                    adjacents = self.adjacent_moves(board_copy, player, plays)

                if len(adjacents):
                    move = choice(adjacents)
                else:
                    peripherals = []
                    for move in availables:
                        if not plays.get((player, move)):
                            peripherals.append(move)
                    move = choice(peripherals)

            board_copy[move[0]][move[1]] = player
            his_moves_copy.append((move[0],move[1]))
            his_players_copy.append(player)
            availables.remove((move[0],move[1]))

            # Step2: Expand
            # add only one new child node each time
            if expand and (player, move) not in plays:
                expand = False
                plays[(player, move)] = 0
                wins[(player, move)] = 0
                if move not in plays_rave:
                    plays_rave[move] = 0
                if move in wins_rave:
                    wins_rave[move][player] = 0
                else:
                    wins_rave[move] = {player: 0}
                if t > self.max_depth:
                    self.max_depth = t

            visited_states.add((player, move))

            is_full = not len(availables)
            win, winner = self.has_a_winner(board_copy)
            if is_full or win:
                break

            player = 1 if his_players_copy[-1]==2 else 2




    def select_one_move(self):
        pass


    def adjacent_moves(self, board, player, plays):
        pass
    

    def has_a_winner(self, board):
        pass



        
def brain_turn():
    """
    Choose your move and call do_mymove(x,y), 0 <= x < width, 0 <= y < height.
    Write your strategies here.
    """
    if not his_moves:      # the board is empty, place a move at center
        pp.do_mymove(pp.width/2 + 1, pp.height/2 + 1)
    
    if pp.terminateAI:     # the game is over
        return

    AI = brain_MCTS(time=pp.info_timeout_turn, max_actions=1000)
    pp.do_mymove(AI.get_action())


def brain_end():
    """
    Delete temporary files, free resources
    """
    pass


def brain_about():
    """
    Print copyright.
    """
    pp.pipeOut(pp.infotext)


if DEBUG_EVAL:
    # For debugging.
    import win32gui
    def brain_eval(x, y):
        # TODO check if it works as expected
        wnd = win32gui.GetForegroundWindow()
        dc = win32gui.GetDC(wnd)
        rc = win32gui.GetClientRect(wnd)
        c = str(board[x][y])
        win32gui.ExtTextOut(dc, rc[2]-15, 3, 0, None, c, ())
        win32gui.ReleaseDC(wnd, dc)


# overwrites information about a game
# The board has 20x20 squares
pp.width, pp.height = 20, 20
# 15 seconds per move, 90 seconds per match for maximum
# time for one turn in milliseconds
pp.info_timeout_turn = 15000
# total time for a game
pp.info_timeout_match = 90000
# 0: human opponent, 1: AI opponent, 2: tournament, 3: network tournament
pp.info_game_type = 1
# 0: five or more stones win, 1: exactly five stones win
pp.info_exact5 = 0
# 0: gomoku, 1: renju
pp.info_renju = 0

# overwrites functions in pisqpipe module
pp.brain_init = brain_init
pp.brain_restart = brain_restart
pp.brain_my = brain_my
pp.brain_opponents = brain_opponents
pp.brain_block = brain_block
pp.brain_takeback = brain_takeback
pp.brain_turn = brain_turn
pp.brain_end = brain_end
pp.brain_about = brain_about
if DEBUG_EVAL:
    pp.brain_eval = brain_eval


def main():
    pp.main()


if __name__ == "__main__":
    main()
