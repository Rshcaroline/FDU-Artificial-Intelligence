# -*- coding:utf-8 -*-


# ---point table---
# // tuple is empty
# Blank, tupleScoreTable[0] = 7;
# // tuple contains a black chess
# B, tupleScoreTable[1] = 35;
# // tuple contains two black chesses
# BB, tupleScoreTable[2] = 800;
# // tuple contains three black chesses
# BBB, tupleScoreTable[3] = 15000;
# // tuple contains four black chesses
# BBBB, tupleScoreTable[4] = 800000;
# // tuple contains a white chess
# W, tupleScoreTable[5] = 15;
# // tuple contains two white chesses
# WW, tupleScoreTable[6] = 400;
# // tuple contains three white chesses
# WWW, tupleScoreTable[7] = 1800;
# // tuple contains four white chesses
# WWWW, tupleScoreTable[8] = 100000;
# // tuple does not exist
# Virtual, tupleScoreTable[9] = 0;
# // tuple contains at least one black and at least one white
# Polluted, tupleScoreTable[10] = 0
import numpy as np
from random import choice

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
    row = board_size
    col = board_size
    # create a table to record the board state
    # 1: occupied by self
    # -1: occupied by opponent
    # 0: available
    table = np.zeros([row, col])
    for i in range(row):
        for j in range(col):
            if playing == 1:
                if (i+1, j+1) in board[0]:
                    table[i, j] = -1
                elif (i+1, j+1) in board[1]:
                    table[i, j] = 1
            else:
                if (i+1, j+1) in board[0]:
                    table[i, j] = 1
                elif (i+1, j+1) in board[1]:
                    table[i, j] = -1

    def score(fiveTuple):
        if len(fiveTuple) != 5:
            print "ERROR"
            return None
        if 1 in fiveTuple and -1 in fiveTuple:
            return 0
        elif sum(fiveTuple) == 0:
            return 7
        elif sum(fiveTuple) == -1:
            return -35
        elif sum(fiveTuple) == -2:
            return -800
        elif sum(fiveTuple) == -3:
            return -15000
        elif sum(fiveTuple) == -4:
            return -800000
        elif sum(fiveTuple) == -5:
            return -10000000
        elif sum(fiveTuple) == 5:
            return 10000000
        elif sum(fiveTuple) == 1:
            return 15
        elif sum(fiveTuple) == 2:
            return 400
        elif sum(fiveTuple) == 3:
            return 1800
        elif sum(fiveTuple) == 4:
            return 100000


    def heuristic(table):
        sumScore = 0
        for i in range(row):
            for j in range(col):
                if j+4 < col:
                    sumScore += score(tuple(table[i, j:j+5]))
                if i+4 < row:
                    sumScore += score(tuple(table[i:i+5, j]))
                if i+4 < row and j+4 < col:
                    fivetuple = []
                    for k in range(5):
                        fivetuple.append(table[i+k, j+k])
                    sumScore += score(tuple(fivetuple))
                if i+4 < row and j-4 >= 0:
                    fivetuple = []
                    for k in range(5):
                        fivetuple.append(table[i+k, j-k])
                    sumScore += score(tuple(fivetuple))
        return sumScore
    
    def randomChoose(scoretable):
        maxValue = max(scoretable.items(), key=lambda x: x[1])[1]
        positions=[]
        for item in scoretable.items():
            if item[1]==maxValue:
                positions.append(item[0])
        return choice(positions)
    
    if len(board[0]) == 0 and len(board[1]) == 0:
        return (board_size/2 + 1, board_size/2 + 1)
    else:
        scoreTable = {}
        for i in range(row):
            for j in range(col):
                if table[i, j] == 0:
                    table[i, j] = 1
                    scoreTable[(i, j)] = heuristic(table)
                    table[i, j] = 0
        self_position = randomChoose(scoreTable)
        return (self_position[0]+1, self_position[1]+1)

def finish():
    pass
