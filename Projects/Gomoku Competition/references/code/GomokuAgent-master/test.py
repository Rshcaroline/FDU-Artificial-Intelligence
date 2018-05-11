#!/usr/bin/env python2
# -- coding: utf-8 --
from app.gomoku_web import *
import argparse
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument("offensive_AI", help="offensive position agent script")
parser.add_argument("defensive_AI", help="defensive position agent script")
parser.add_argument("size", help="chess board size")
parser.add_argument("filepath", help="print filepath")
parser.add_argument("times", help="pay times")
parser.add_argument("silent", help="choose if to print board step by step")

args = parser.parse_args()
offensive_AI = args.offensive_AI
defensive_AI = args.defensive_AI
board_size = int(args.size)
filepath = args.filepath
times = int(args.times)
players = [offensive_AI, defensive_AI]
silent_mode = True if args.silent == 's' else False

if __name__ == '__main__':
    f = open(filepath, 'w')
    f.write(offensive_AI + " vs. " + defensive_AI + "\n")
    result = []
    for i in range(times):
        game = Gomoku_Web(board_size=board_size, players=players, silent_mode=silent_mode)
        tmp = []
        for player in players:
            if player.startswith('AI'):
                p = Player(player, ai_script=player, level=5)
            else:
                p = Player(player)
            tmp.append(p)
        game.players = tmp
        f.write("Round " + str(i + 1) + '\n')
        print "Round", i+1, "is playing..."
        center = ((board_size+1) / 2, (board_size+1) / 2)
        next_action, winner = game.web_play(center)
        while not winner:
            next_action, winner = game.web_play(next_action)
        game.print_board()
        print winner
        result.append(winner)
        f.write("winner: " + winner + '\n')
    result = np.array(result)
    for res in np.unique(result):
        print res, len(result[result==res])
        f.write(res + ' ' + str(len(result[result==res])) + '\n')
    f.close()
