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


# start of RT's code
import itertools
import re
from collections import Counter
whether_start = False

def opponent(player):
    return 3-player


def probable_position(board):
    """
    find all position that may be considered as the next action.
    exist (x,y) not free, such that |x-pos_x|<3, |y-pos_y|<3
    :param
        board: the current board state
    :return:
        position:  all position may be considered
    """
    probable_list = []
    for (pos_x, pos_y) in itertools.product(range(pp.width), range(pp.height)):
        if not isFree(pos_x, pos_y):
            continue
        for (i,j) in itertools.product(range(5), range(5)):
            x, y = pos_x - i, pos_y - j
            if x < 0 or x >= pp.width or y < 0 or y >= pp.height:  # out of the board
                continue
            if not isFree(x, y):  # a chess is in the region
                probable_list.append((pos_x, pos_y))
                break
    return probable_list  # prob_list may be empty


def renew_probable_position(action, probable_list):
    """
    renew the probable list
    :param
        action: the position AI or player put at
        probable_list: the list needed to be renewed
    :returns
        a new list
    """
    x, y = action[0], action[1]

    for (i, j) in itertools.product(range(5), range(5)):
        new_x = x - i
        new_y = y - j
        if (new_x, new_y) not in probable_list:
            probable_list.append((new_x, new_y))

    if (x, y) in probable_list:
        probable_list.remove((x, y))

    return probable_list


def extend_board(player, board):
    """
    add an edge for the board
    :param
        player: to extract whose feature (then the edge is 3-player)
        board:
    :return
        new_board: extended board
    """
    new_board = [[board[x-1][y-1] if 0 < x < pp.width + 2 and 0 < y < pp.height + 2 else 3-player \
                  for x in range(pp.width + 2)] for y in range(pp.height + 2)]
    return new_board


def is_special_class(array, color):
    """
    judge whether the several chess given in the list form a special class
    :param
        array: the board of gomoku
        color: the index of color, 1: black, 2: white
    :return:
        Counter: ({class: num of this class}, ...)
    """

    # add judgement here. Details in 'http://zjh776.iteye.com/blog/1979748'

    def _black_color(array):
        height, width = len(array), len(array[0])
        for i in range(height):
            for j in range(width):
                array[i][j] = (3 - array[i][j]) % 3
        return array

    if color == 2:
        list_str = _black_color(array)

    class_dict = {("WIN", (), ()): "11111",
                  ("H4", (0, 5), ()): "011110",
                  ("C4", (0), (5)): "011112",
                  ("C4", (5), (0)): "211110",
                  ("C4", (4), ()): r"^11110",
                  ("C4", (0), ()): r"01111$",
                  ("C4", (0, 2, 6), ()): "0101110",
                  ("C4", (0, 4, 6), ()): "0111010",
                  ("C4", (0, 3, 6), ()): "0110110",
                  ("H3", (0, 4), ()): "01110",
                  ("H3", (0, 2, 5), ()): "010110",
                  ("H3", (0, 3, 5), ()): "011010",
                  ("M3", (0, 1), (5)): "001112",
                  ("M3", (0, 1), ()): r"00111$",
                  ("M3", (4, 5), (0)): "211100",
                  ("M3", (4, 5), ()): r"^11100",
                  ("M3", (0, 2), (5)): "010112",
                  ("M3", (0, 2), ()): r"01011$",
                  ("M3", (3, 5), (0)): "211010",
                  ("M3", (3, 5), ()): r"^11010",
                  ("M3", (0, 3), (5)): "011012",
                  ("M3", (0, 3), ()): r"01101$",
                  ("M3", (2, 5), (0)): "210110",
                  ("M3", (2, 5), ()): r"^10110",
                  ("M3", (1, 2), ()): "10011",
                  ("M3", (2, 3), ()): "11001",
                  ("M3", (1, 3), ()): "10101",
                  ("M3", (1, 4), (0, 6)): "2011102",
                  ("M3", (1, 4), (6)): r"^011102",
                  ("M3", (1, 4), (0)): r"201110$",
                  ("H2", (0, 1, 4), ()): "00110",
                  ("H2", (0, 3, 4), ()): "01100",
                  ("H2", (0, 2, 4), ()): "01010",
                  ("H2", (0, 2, 3, 5), ()): "010010",
                  ("M2", (0, 1, 2), (5)): "000112",
                  ("M2", (0, 1, 2), ()): r"00011$",
                  ("M2", (3, 4, 5), (0)): "211000",
                  ("M2", (3, 4, 5), ()): r"^11000",
                  ("M2", (0, 1, 3), (5)): "001012",
                  ("M2", (0, 1, 3), ()): r"00101$",
                  ("M2", (2, 4, 5), (0)): "210100",
                  ("M2", (2, 4, 5), ()): r"^10100",
                  ("M2", (0, 2, 3), (5)): "010012",
                  ("M2", (0, 2, 3), ()): r"01001$",
                  ("M2", (2, 3, 5), (0)): "210010",
                  ("M2", (2, 3, 5), ()): r"^10010",
                  ("M2", (1, 2, 3), ()): "10001",
                  ("M2", (1, 3, 5), (0, 6)): "2010102",
                  ("M2", (1, 3, 5), (0)): r"201010$",
                  ("M2", (1, 3, 5), (6)): r"^010102",
                  ("M2", (1, 4, 5), (0, 6)): "2011002",
                  ("M2", (1, 4, 5), (6)): r"^011002",
                  ("M2", (1, 4, 5), (0)): r"201100^",
                  ("M2", (1, 2, 5), (0, 6)): "2001102",
                  ("M2", (1, 2, 5), (0)): r"200110$",
                  ("M2", (1, 2, 5), (6)): r"^001102",
                  ("S4", (), (0, 5)): "211112",
                  ("S4", (), (0)): r"21111$",
                  ("S4", (), (5)): r"^11112",
                  ("S3", (), (0, 4)): "21112",
                  ("S3", (), (0)): r"2111$",
                  ("S3", (), (4)): r"^1112",
                  ("S2", (), (0, 3)): "2112",
                  ("S2", (), (3)): r"^112",
                  ("S2", (), (0)): r"211$",
                  }

    height, width = len(array), len(array[0])
    class_counter = Counter()

    # scan by row
    for row_idx, row in enumerate(array):
        list_str = "".join(map(str, row))
        for key in class_dict:
            class_counter[key[0]] += len(re.findall(class_dict[key], list_str))

    # scan by col
    for col_idx in range(width):
        col = [a[col_idx] for a in array]
        list_str = "".join(map(str, col))
        for key in class_dict:
            class_counter[key[0]] += len(re.findall(class_dict[key], list_str))

    # scan by diag_1, from TL to BR
    for dist in range(-width + 1, height):
        row_ini, col_ini = (0, -dist) if dist < 0 else (dist, 0)
        diag = [array[i][j] for i in range(
            row_ini, height) for j in range(col_ini, width) if i - j == dist]
        list_str = "".join(map(str, diag))
        for key in class_dict:
            class_counter[key[0]] += len(re.findall(class_dict[key], list_str))

    # scan by diag_2, from BL to TR
    for dist in range(0, width + height - 1):
        row_ini, col_ini = (dist, 0) if dist < height else (
            height - 1, dist - height + 1)
        diag = [array[i][j] for i in range(
            row_ini, -1, -1) for j in range(col_ini, width) if i + j == dist]
        list_str = "".join(map(str, diag))
        for key in class_dict:
            class_counter[key[0]] += len(re.findall(class_dict[key], list_str))

    return class_counter


def class_to_score():
    """
    define the reward of some specific class of chess
    :return:
        score_map: a map from the special class(a string) to score(a real number)
    """
    score_map = {"WIN": 100000,
                 "H4": 10000,
                 "C4": 100,
                 "H3": 200,
                 "M3": 50,
                 "H2": 5,
                 "M2": 3,
                 "S4": -5,
                 "S3": -5,
                 "S2": -5
                 }
    return score_map


def board_evaluation(board):
    """
    evaluate the situation of the brain.
    :param
        board:
    :return:
        score: a real number, indicating how good the condition is
    """
    score = 0

    brain_board = extend_board(board=board, player=1)
    for a_class, num in is_special_class(brain_board, 1).items():
        score = score + class_to_score()[a_class] * num

    oppo_board = extend_board(board=board, player=2)
    for a_class, num in is_special_class(oppo_board, 2).items():
        score = score - class_to_score()[a_class] * num

    return score


def isEnd(board):
    """
    judge wheher the game has a winner, if we have one, show who he is
    :param
        board:
    :return
        is_end: a boolean
        winner: if not exist, return None, else return 1 or 2
    """
    num1 = is_special_class(board, 1)["WIN"]
    num2 = is_special_class(board, 2)["WIN"]

    if num1 == 0 and num2 == 0:
        return False, None
    elif num1 > 0:
        return True, 1
    else:
        return True, 2
# end of RT's code    


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
        self.plays_rave = {}    # key:move, value: visited times
        self.wins_rave = {}     # key:move, value: {player: win times}


    def get_action(self):
        # import packages
        import copy
        import time
        import itertools

        # do some parameters initialize
        simulations = 0    
        begin = time.time()    # record time, we can't exceed the restricted time
        while time.time() - begin < self.calculation_time/15:
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
        # import spackages
        from random import choice, shuffle
        from math import log, sqrt
        import itertools

        player = 1 if his_players_copy[-1]==2 else 2
        availables = [(i, j) for i, j in itertools.product(range(pp.width), range(pp.height)) if board_copy[i][j]==0]
        visited_states = set()
        winner = -1
        expand = True

        # Simulation begin, we will go through max_actions times simulations
        for t in range(1, self.max_actions + 1):
            # Step1: Selection
            # If all moves have statistics info, choose one that have max UCB value
            if all(self.plays.get((player, move)) for move in availables):
                value, move = max(
                    ((1 - sqrt(self.equivalence / (3 * self.plays_rave[move] + self.equivalence))) * 
                    (self.wins[(player, move)] / self.plays[(player, move)]) +
                    sqrt(self.equivalence / (3 * self.plays_rave[move] + self.equivalence)) * 
                    (self.wins_rave[move][player] / self.plays_rave[move]) +
                    sqrt(self.confident * log(self.plays_rave[move]) / self.plays[(player, move)]), move)
                    for move in availables)    # UCT RAVE
                # pp.pipeOut("Select Move at [{},{}] with value {}".format(move[0], move[1], value))
            else:
            # a simple strategy
            # prefer to choose the nearer moves without statistics,
            # and then the farthers.
            # try to add statistics info to all moves quickly
            # adjacents = []
                if len(availables) > 5:
                    adjacents = self.adjacent_moves(board_copy, player, self.plays, his_moves_copy)

                if len(adjacents):
                    # random select one move from adjacents
                    move = choice(adjacents)
                    # pp.pipeOut("Random select one move from adjacents at [{},{}]".format(move[0], move[1]))
                # else:
                #     peripherals = []
                #     for move in availables:
                #         if not self.plays.get((player, move)):
                #             peripherals.append(move)
                #     move = choice(peripherals)

            # add one move to the board
            board_copy[move[0]][move[1]] = player
            his_moves_copy.append((move[0],move[1]))
            his_players_copy.append(player)
            availables.remove((move[0],move[1]))

            # Step2: Expand
            # add only one new child node each time
            if expand and (player, move) not in self.plays:
                expand = False
                self.plays[(player, move)] = 0
                self.wins[(player, move)] = 0
                if move not in self.plays_rave:
                    self.plays_rave[move] = 0
                if move in self.wins_rave:
                    self.wins_rave[move][player] = 0
                else:
                    self.wins_rave[move] = {player: 0}
                if t > self.max_depth:
                    self.max_depth = t

            visited_states.add((player, move))

            is_full = not len(availables)
            win, winner = isEnd(board_copy)
            if is_full or win:
                break

            # update player
            player = 1 if his_players_copy[-1]==2 else 2
        
        # Step4: Back-propagation
        for player, move in visited_states:
            if (player, move) in self.plays:
                self.plays[(player, move)] += 1        # all visited moves
                if player == winner:
                    self.wins[(player, move)] += 1     # only winner's moves
            if move in self.plays_rave:
                self.plays_rave[move] += 1             # no matter which player
                if winner in self.wins_rave[move]:
                    self.wins_rave[move][winner] += 1  # each move and every player


    def select_one_move(self):
        import itertools
        availables = [(i, j) for i, j in itertools.product(range(pp.width), range(pp.height)) if board[i][j]==0]
        moves = {}
        for move in availables:
            moves[move] = 100*self.wins.get((self.player, move), 0)/self.plays.get((self.player, move), 1)
        comb = max(zip(moves.values(), moves.keys()))
        return comb[1]


    def adjacent_moves(self, board, player, plays, his_moves):
        """
        Adjacent moves without statistics info
        This function is right!
        """
        import itertools
        # ava = [(i, j) for i, j in itertools.product(range(pp.width), range(pp.height)) if board[i][j]==0]
        moved = his_moves
        # moved = [(i, j) for i, j in itertools.product(range(pp.width), range(pp.height)) if board[i][j]==player]
        # pp.pipeOut("moved {}".format(moved))

        adjacents = set()
        width = pp.width
        height = pp.height

        for (h, w) in moved:
            if h < width - 1:
                adjacents.add((h+1, w))  # right
            if h > 0:
                adjacents.add((h-1, w))  # left
            if w < height - 1:
                adjacents.add((h, w+1))  # upper
            if w > 0:
                adjacents.add((h, w-1))  # lower
            if w < width - 1 and h < height - 1:
                adjacents.add((h+1, w+1))  # upper right
            if h > 0 and w < height - 1:
                adjacents.add((h-1, w+1))  # upper left
            if h < width - 1 and w > 0:
                adjacents.add((h+1, w-1))  # lower right
            if w > 0 and h > 0:
                adjacents.add((h-1, w-1))  # lower left

        adjacents = list(set(adjacents) - set(moved))
        for move in adjacents:
            if plays.get((player, move)):
                adjacents.remove(move)
        return adjacents
    
        
def brain_turn():
    """
    Choose your move and call do_mymove(x,y), 0 <= x < width, 0 <= y < height.
    Write your strategies here.
    """
    if pp.terminateAI:     # the game is over
        return

    if not his_moves:      # the board is empty, place a move at center
        pp.do_mymove(int(pp.width//2), int(pp.height//2))

    # use MCTS to find a move
    AI = brain_MCTS(time=pp.info_timeout_turn, max_actions=50000)
    action = AI.get_action()
    pp.do_mymove(*action)


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
