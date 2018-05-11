# -*- coding:utf-8 -*-

def strategy(state):
    """ Information provided to you:
    state = (board, last_move, playing, board_size)
    board = (x_stones, o_stones)
    stones is a set contains positions of one player's stones. e.g.
        x_stones = {(8,8), (8,9), (8,10), (8,11)}
    playing = 0|1, the current player's index

    Your strategy will return a position code for the next stone, e.g. (8,7)
    """
    board, last_move, playing, board_size = state
    x, y = last_move
    return (x + 1, y + 1)

def finish():
    pass
