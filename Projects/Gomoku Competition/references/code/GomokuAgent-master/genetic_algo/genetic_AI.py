# -*- coding:utf-8 -*-
import numpy as np
from random import choice

def strategy(state, score):
    # score is a global variable
    # score is a 28-dimension array
    # initial: [1000000, 20000, 6100, 6000, 1100, 1000, 300, 290, 290, 290, 100, 10, 3, 1,
    #           1000000, 100000, 65000, 65000, 5500, 5000, 200, 200, 200, 200, 90, 9, 4, 1]
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
    # 2: occupied by opponent
    # 0: available
    table = np.zeros([row, col])
    for i in range(row):
        for j in range(col):
            if playing == 1:
                if (i+1, j+1) in board[0]:
                    table[i, j] = 2
                elif (i+1, j+1) in board[1]:
                    table[i, j] = 1
            else:
                if (i+1, j+1) in board[0]:
                    table[i, j] = 1
                elif (i+1, j+1) in board[1]:
                    table[i, j] = 2
    # 获取该点4个方向的棋型
    def getstring(point):
        x = point[0]
        y = point[1]
        # vertical
        getLine1 = ''
        for k in range(max(x - 4, 0), min(x + 5, 15)):
            getLine1 += str(int(table[k, y]))
        if x-4<0: getLine1 = '*'+getLine1
        if x+4>14: getLine1 = getLine1+'*'
        # horizonal
        getLine2 = ''
        for k in range(max(y - 4, 0), min(y + 5, 15)):
            getLine2 += str(int(table[x, k]))
        if y-4<0: getLine2 = '*'+getLine2
        if y+4>14: getLine2 = getLine2+'*'
        # Oblique 45
        getLine3 = ''
        bx = max(0, x - 4)
        by = max(0, y - 4)
        ux = min(14, x + 4)
        uy = min(14, y + 4)
        for k in range(max(bx - x, by - y), min(ux - x, uy - y)+1):
            getLine3 += str(int(table[x + k, y + k]))
        if x-4<0 or y-4<0: getLine3 = '*'+getLine3
        if x+4>14 or y+4>14: getLine3 = getLine3+'*'
        # Oblique 135
        getLine4 = ''
        for k in range(max(bx - x, y - uy), min(ux - x, y - by)+1):
            getLine4 += str(int(table[x + k, y - k]))
        if x-4<0 or y+4>14: getLine4 = '*'+getLine4
        if x+4>14 or y-4<0: getLine4 = getLine4+'*'

        return [getLine1, getLine2, getLine3, getLine4]

    # 判断我方棋型
    def judgeType1(getline):
        if '11111' in getline:
            return 'win5'
        if '011110' in getline:
            return 'alive4'
        if '211110' in getline or '011112' in getline\
                or '*11110' in getline or '01111*' in getline:
            return 'lian-rush4'
        if '11101' in getline or '10111' in getline\
                or '11011' in getline:
            return 'tiao-rush4'
        if '001110' in getline or '011100' in getline:
            return 'lian-alive3'
        if '011010' in getline or '010110' in getline:
            return 'tiao-alive3'
        if '211100' in getline or '001112' in getline\
                or '*11100' in getline or '00111*' in getline:
            return 'lian-sleep3'
        if '211010' in getline or '010112' in getline\
                or '*11010' in getline or '01011*' in getline\
                or '210110' in getline or '011012' in getline\
                or '*10110' in getline or '01101*' in getline:
            return 'tiao-sleep3'
        if '11001' in getline or '10011' in getline\
                or '10101' in getline:
            return 'te-sleep3'
        if '2011102' in getline or '*011102' in getline\
                or '201110*' in getline or '*01110*' in getline:
            return 'jia-alive3'
        if '001100' in getline or '011000' in getline\
                or '000110' in getline or '001010' in getline\
                or '010100' in getline or '010010' in getline:
            return 'alive2'
        if '211000' in getline or '000112' in getline\
                or '*11000' in getline or '00011*' in getline\
                or '210100' in getline or '001012' in getline\
                or '*10100' in getline or '00101*' in getline\
                or '210010' in getline or '010012' in getline\
                or '*10010' in getline or '01001*' in getline\
                or '10001' in getline or '2010102' in getline\
                or '*01010*' in getline or '201010*' in getline\
                or '*010102' in getline or '2011002' in getline\
                or '2001102' in getline or '*011002' in getline\
                or '200110*' in getline or '201100*' in getline\
                or '*001102' in getline:
            return 'sleep2'
        if '010' in getline:
            return 'alive1'
        else:
            return 'nothreat'

    # 判断对方棋型
    def judgeType2(getline):
        if '22222' in getline:
            return 'win5'
        if '022220' in getline:
            return 'alive4'
        if '122220' in getline or '022221' in getline\
                or '*22220' in getline or '02222*' in getline:
            return 'lian-rush4'
        if '22202' in getline or '20222' in getline\
                or '22022' in getline:
            return 'tiao-rush4'
        if '002220' in getline or '022200' in getline:
            return 'lian-alive3'
        if '022020' in getline or '020220' in getline:
            return 'tiao-alive3'
        if '122200' in getline or '002221' in getline\
                or '*22200' in getline or '00222*' in getline:
            return 'lian-sleep3'
        if '122020' in getline or '020221' in getline\
                or '*22020' in getline or '02022*' in getline\
                or '120220' in getline or '022021' in getline\
                or '*20220' in getline or '02202*' in getline:
            return 'tiao-sleep3'
        if '22002' in getline or '20022' in getline\
                or '20202' in getline:
            return 'te-sleep3'
        if '1022201' in getline or '*022201' in getline\
                or '102220*' in getline or '*02220*' in getline:
            return 'jia-alive3'
        if '002200' in getline or '022000' in getline\
                or '000220' in getline or '002020' in getline\
                or '020200' in getline or '020020' in getline:
            return 'alive2'
        if '122000' in getline or '000221' in getline\
                or '*22000' in getline or '00022*' in getline\
                or '120200' in getline or '002021' in getline\
                or '*20200' in getline or '00202*' in getline\
                or '120020' in getline or '020021' in getline\
                or '*20020' in getline or '02002*' in getline\
                or '20002' in getline or '1020201' in getline\
                or '*02020*' in getline or '102020*' in getline\
                or '*020201' in getline or '1022001' in getline\
                or '1002201' in getline or '*022001' in getline\
                or '100220*' in getline or '102200*' in getline\
                or '*002201' in getline:
            return 'sleep2'
        if '020' in getline:
            return 'alive1'
        else:
            return 'nothreat'

    # 计算我方形势分数
    def evaluate_self(table):
        row, col = table.shape
        myscore = 0
        for i in range(row):
            for j in range(col):
                if table[i, j] == 1:
                    point = (i, j)
                    myType={'win5':0, 'alive4':0, 'lian-rush4':0, 'tiao-rush4':0, 'lian-alive3':0, 'tiao-alive3':0,\
                            'lian-sleep3':0, 'tiao-sleep3':0, 'te-sleep3':0, 'jia-alive3':0,\
                            'alive2':0, 'sleep2':0, 'alive1':0, 'nothreat':0}
                    lines = getstring(point)
                    for item0 in lines:
                        tmp1 = judgeType1(item0)
                        myType[tmp1] += 1
                    # my score
                    myscore += score[0]*myType['win5']+score[1]*myType['alive4']+ \
                               score[2]*myType['lian-rush4']+score[3]*myType['tiao-rush4']+ \
                               score[4]*myType['lian-alive3']+score[5]*myType['tiao-alive3']+ \
                               score[6]*myType['lian-sleep3']+score[7]*myType['tiao-sleep3']+\
                               score[8]*myType['te-sleep3']+score[9]*myType['jia-alive3']+\
                               score[10]*myType['alive2']+score[11]*myType['sleep2']+\
                               score[12]*myType['alive1']+score[13]*myType['nothreat']
        return myscore

    # 计算敌方的形势分数
    def evaluate_op(table):
        row, col = table.shape
        opscore = 0
        for i in range(row):
            for j in range(col):
                if table[i, j] == 2:
                    point = (i, j)
                    opType = {'win5':0, 'alive4':0, 'lian-rush4':0, 'tiao-rush4':0, 'lian-alive3':0, 'tiao-alive3':0,\
                            'lian-sleep3':0, 'tiao-sleep3':0, 'te-sleep3':0, 'jia-alive3':0,\
                            'alive2':0, 'sleep2':0, 'alive1':0, 'nothreat':0}
                    lines = getstring(point)
                    for item0 in lines:
                        tmp2 = judgeType2(item0)
                        opType[tmp2] += 1
                    # opponent score
                    opscore += score[14]*opType['win5']+score[15]*opType['alive4']+ \
                               score[16]*opType['lian-rush4']+score[17]*opType['tiao-rush4']+ \
                               score[18]*opType['lian-alive3']+score[19]*opType['tiao-alive3']+ \
                               score[20]*opType['lian-sleep3']+score[21]*opType['tiao-sleep3']+\
                               score[22]*opType['te-sleep3']+score[23]*opType['jia-alive3']+\
                               score[24]*opType['alive2']+score[25]*opType['sleep2']+\
                               score[26]*opType['alive1']+score[27]*opType['nothreat']
        return opscore


    #随机返回一个score最大的位置
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
        # 获得局部搜索区域的下标
        sumBoard = board[0] | board[1]
        xmax = min(max(sumBoard, key=lambda x: x[0])[0] + 2, 15)
        ymax = min(max(sumBoard, key=lambda x: x[1])[1] + 2, 15)
        xmin = max(min(sumBoard, key=lambda x: x[0])[0] - 3, 0)
        ymin = max(min(sumBoard, key=lambda x: x[1])[1] - 3, 0)

        scoretable={}
        for i in range(xmin, xmax):
            for j in range(ymin, ymax):
                if table[i, j] == 0:
                    #old = evaluate_self(table)-defend*evaluate_op(table)
                    table[i, j] = 1
                    scoretable[(i, j)] = evaluate_self(table)-evaluate_op(table)
                    table[i, j] = 0
        self_position = randomChoose(scoretable)
        return (self_position[0]+1, self_position[1]+1)

