# @Time    : 28/05/2018 2:37 PM
# @Author  : Shihan Ran
# @File    : AI-template.py
# @Software: PyCharm
# @license : Copyright(C), Fudan University
# @Contact : rshcaroline@gmail.com
# @Desc    : This is a template for Gomoku.


import random
import pisqpipe as pp
from collections import Counter
import re

pp.infotext = 'name="AI-template", author="Shihan Ran", version="1.0", country="China"'

MAX_BOARD = 100
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


def brain_my(x, y):
    """
    I take a move.
    """
    if isFree(x,y):
        board[x][y] = 1
    else:
        pp.pipeOut("ERROR my move [{},{}]".format(x, y))


def brain_opponents(x, y):
    """
    Opponents take a move.
    """
    if isFree(x,y):
        board[x][y] = 2
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


def brain_turn():
    """
    Choose your move and call do_mymove(x,y), 0 <= x < width, 0 <= y < height.
    Write your strategies here. Randomly take a move.
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

# start of my code
import itertools


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
    scale = 1
    for (pos_x, pos_y) in itertools.product(range(pp.width), range(pp.height)):
        if not board[pos_x][pos_y] == 0:
            continue
        for (i,j) in itertools.product(range(2 * scale + 1), range(2 * scale + 1)):
            x, y = pos_x + i - scale, pos_y + j - scale
            if x < 0 or x >= pp.width or y < 0 or y >= pp.height:  # out of the board
                continue
            if not board[x][y] == 0:  # a chess is in the region
                probable_list.append((pos_x, pos_y))
                break
    if probable_list == []:
        return None
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
    scale = 1

    for (i, j) in itertools.product(range(2 * scale + 1), range(2 * scale + 1)):
        new_x = x + i - scale
        new_y = y + j - scale
        if (new_x, new_y) not in probable_list:
            probable_list.append((new_x, new_y))

    if (x, y) in probable_list:
        probable_list.remove((x, y))

    return probable_list


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
    score_map = {"WIN": 200000,
                 "H4": 10000,
                 "C4": 1000,
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

    for a_class, num in is_special_class(board, 1).items():
        score = score + class_to_score()[a_class] * num
    for a_class, num in is_special_class(board, 2).items():
        if a_class in ['H4', 'C4', 'WIN']:
            score = score - 10 * class_to_score()[a_class] * num
        else:
            score = score - class_to_score()[a_class] * num

    return score

def point_evaluation(board, pos):
    """
    to assess a point
    ":param
        board:
        pos: (x, y)
    :return:  real number = pbrain_add - opponent_add
    """
    # TODO:


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

# end of my code

