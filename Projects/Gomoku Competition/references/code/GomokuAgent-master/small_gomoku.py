#!/usr/bin/env python2
# -- coding: utf-8 --
from app.gomoku_web import *
players = ['YOU', 'AI0']
game = Gomoku_Web(board_size=7, winning_num=4)
tmp = []
for player in players:
    if player.startswith('AI'):
        p = Player(player, ai_script=player, level=5)
    else:
        p = Player(player)
    tmp.append(p)
game.players = tmp

center = ((game.board_size+1) / 2, (game.board_size+1) / 2)
next_action, winner = game.web_play(center)
while not winner:
    if game.players[game.playing].is_ai:
        next_action, winner = game.web_play(next_action)
    else:
        stone = raw_input("Enter your stone like '4 5'...")
        stone = map(lambda x: int(x), stone.split(' '))
        next_action, winner = game.web_play(tuple(stone))
print winner
