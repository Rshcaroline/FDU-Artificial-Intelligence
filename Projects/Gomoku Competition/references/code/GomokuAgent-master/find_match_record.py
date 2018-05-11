# -- coding: utf-8 --
import numpy as np
import random
import os

basedir = os.path.abspath(os.path.dirname(__file__))
record = np.load(os.path.join(basedir, 'game_record', 'records.npy'))
record = map(lambda x: x.strip(), record)

def change_format(game_record):
    return game_record.split(';')

record = map(change_format, record)
record = np.array(record)

alphabet = 'abcdefghijklmno'
alpha_dic = dict(zip(alphabet, np.arange(1, 15)))

def match_record(record, stone_num, board):
    try:
        stones = record[:stone_num]
        white = [stones[i] for i in range(stone_num) if i % 2 == 1]
        black = [stones[i] for i in range(stone_num) if i % 2 == 0]
        white = map(lambda x: x[2:-1], white)
        black = map(lambda x: x[2:-1], black)
        white = set([(alpha_dic[i[0]], alpha_dic[i[1]]) for i in white])
        black = set([(alpha_dic[i[0]], alpha_dic[i[1]]) for i in black])
        record_board = (black, white)
        if board == record_board:
            return True
        else:
            return False
    except:
        return False

state = ((set([(8, 8)]), set([(9, 9)])), (8, 8), 2, 15)

def find_match_record(state):
    """ Information provided to you:
    state = (board, last_move, playing, board_size)
    board = (x_stones, o_stones)
    stones is a set contains positions of one player's stones. e.g.
        x_stones = {(8,8), (8,9), (8,10), (8,11)}
    playing = 0|1, the current player's index
    This strategy will search 5570 games and return a matched next step, e.g. (8,7)
    """
    board, last_move, playing, board_size = state
    x, y = last_move
    turns = len(board[0]) + len(board[1])
    match_game = record[map(lambda x: match_record(x, turns, board), record)]
    if len(match_game):
        print len(match_game), 'game matched!'
        select_game = random.choice(match_game)
        next_place = select_game[turns]
        x, y = alpha_dic[next_place[2]], alpha_dic[next_place[3]]
        return (x, y)
    else:
        print 'No game matched!'
        return None

print find_match_record(state)
