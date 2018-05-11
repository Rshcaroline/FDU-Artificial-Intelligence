from flask import render_template, request, jsonify
from app import app
import gomoku_web

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/_start', methods=['GET'])
def start():
    game.reset()
    p1 = request.args.get('p1', 'You', type=str)
    p2 = request.args.get('p2', 'AI1', type=str)
    lv = request.args.get('lv', 5, type=int)
    game.players = []
    for player_name in [p1,p2]:
        if player_name.startswith('AI'):
            p = gomoku_web.Player(player_name,ai_script=player_name,level=lv)
        else:
            p = gomoku_web.Player(player_name)
        game.players.append(p)
    game.print_board()
    return 'Success'

@app.route('/_player_set', methods=['GET'])
def player_set():
    position = request.args.get('position','')
    stone = tuple(int(i) for i in position.split(','))
    action = (stone[0]+1, stone[1]+1) # we start from 1 in the game engine
    next_action, winner = game.web_play(action)
    if isinstance(next_action, tuple):
        stone = (next_action[0]-1, next_action[1]-1)
    else:
        stone = None
    return jsonify(next_move=stone, winner=winner)

@app.route('/_reset', methods=['GET'])
def reset():
    game.reset()
    return 'Success'

@app.route('/_undo', methods=['GET'])
def undo():
    game.undo()
    return 'Success'

game = gomoku_web.Gomoku_Web(board_size=15)
