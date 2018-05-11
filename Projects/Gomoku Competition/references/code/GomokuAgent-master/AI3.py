# -*- coding:utf-8 -*-

import copy
import time
from random import choice, shuffle
from math import log, sqrt

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
    x_stones, o_stones = board
    if last_move == None:
        return (board_size/2 + 1, board_size/2 + 1)

    board_init = Board(width=board_size, height=board_size, n_in_row=4)
    board_init.init_board()

    for x,y in x_stones:
        location = [x-1,y-1]
        board_init.update(1, location)
    for x,y in o_stones:
        location = [x-1, y-1]
        board_init.update(2, location)
    print board_init.availables
    print board_init.states

    ai = MCTS(board_init, [2, 1], n_in_row = 4, time = 10, max_actions = 3000)
    x,y = ai.get_action()
#    print ("AI move: %d, %d"%(x+1,y+1))
    return (x+1,y+1)


# def get_action(board, play_turn, availables, calculation_time = 5):
#     if len(availables) == 1:
#         return availables[0]
#     plays = {}
#     wins = {}
#     simulations = 0
#     begin = time.time()
#     while time.time() - begin < calculation_time:
#         board_copy = copy.deepcopy(board)
#         play_turn_copy = copy.deepcopy(play_turn)
#         run_simulation(board_copy, play_turn_copy)
#         move = select_one_move()
#
#
# def run_simulation(board, availables, play_turn):
#     plays = {}
#     wins = {}
#     visited_states = set()
#     winner = -1
#     expand = True
#
#     max_actions = 1000
#     for t in range(1, max_actions + 1):

class Board(object):
    """
    board for game
    """

    def __init__(self, **kwargs):
        self.width = int(kwargs.get('width', 7))
        self.height = int(kwargs.get('height', 7))
        self.states = {}  # board states, key:(player, move), value: piece type
        self.n_in_row = int(kwargs.get('n_in_row', 5))  # need how many pieces in a row to win

    def init_board(self):
        # if self.width < self.n_in_row or self.height < self.n_in_row:
        #     raise Exception('board width and height can not less than %d' % self.n_in_row)

        self.availables = list(range(self.width * self.height))  # available moves

        for m in self.availables:
            self.states[m] = -1

    def move_to_location(self, move):
        """
        3*3 board's moves like:
        6 7 8
        3 4 5
        0 1 2
        and move 5's location is (1,2)
        """
        h = move // self.width
        w = move % self.width
        return [h, w]

    def location_to_move(self, location):
        # if (len(location) != 2):
        #     return -1
        h = location[0]
        w = location[1]
        move = h * self.width + w
        if (move not in range(self.width * self.height)):
            return -1
        return move

    def update(self, player, location):
        move = self.location_to_move(location)
        self.states[move] = player
        self.availables.remove(move)


class MCTS(object):
    """
    AI player, UCT RAVE
    """

    def __init__(self, board, play_turn, n_in_row=4, time=5, max_actions=1000):
        self.board = board
        self.play_turn = play_turn
        self.calculation_time = float(time)
        self.max_actions = max_actions
        self.n_in_row = n_in_row

        self.player = play_turn[0]  # AI is first at now
        self.confident = 1.96
        self.equivalence = 10000  # calc beta
        self.max_depth = 1

    def get_action(self):
        if len(self.board.availables) == 1:
            return self.board.availables[0]

        self.plays = {}  # key:(player, move), value:visited times
        self.wins = {}  # key:(player, move), value:win times
        self.plays_rave = {}  # key:move, value:visited times
        self.wins_rave = {}  # key:move, value:{player: win times}
        simulations = 0
        begin = time.time()
        while time.time() - begin < self.calculation_time:
            board_copy = copy.deepcopy(self.board)  # simulation will change board's states,
            play_turn_copy = copy.deepcopy(self.play_turn)  # and play turn
            self.run_simulation(board_copy, play_turn_copy)
            simulations += 1
        print(simulations)

        move = self.select_one_move()
        location = self.board.move_to_location(move)
        return location

    def run_simulation(self, board, play_turn):
        """
        MCTS main process
        """

        plays = self.plays
        wins = self.wins
        plays_rave = self.plays_rave
        wins_rave = self.wins_rave
        availables = board.availables

        player = self.get_player(play_turn)
        visited_states = set()
        winner = -1
        expand = True
        # Simulation
        for t in range(1, self.max_actions + 1):
            # Selection
            # if all moves have statistics info, choose one that have max UCB value
            if all(plays.get((player, move)) for move in availables):
                value, move = max(
                    ((1 - sqrt(self.equivalence / (3 * plays_rave[move] + self.equivalence))) * (
                    wins[(player, move)] / plays[(player, move)]) +
                     sqrt(self.equivalence / (3 * plays_rave[move] + self.equivalence)) * (
                     wins_rave[move][player] / plays_rave[move]) +
                     sqrt(self.confident * log(plays_rave[move]) / plays[(player, move)]), move)
                    for move in availables)  # UCT RAVE
            else:
                # a simple strategy
                # prefer to choose the nearer moves without statistics,
                # and then the farthers.
                # try ro add statistics info to all moves quickly
                adjacents = []
                if len(availables) > self.n_in_row:
                    adjacents = self.adjacent_moves(board, player, plays)

                if len(adjacents):
                    move = choice(adjacents)
                else:
                    peripherals = []
                    for move in availables:
                        if not plays.get((player, move)):
                            peripherals.append(move)
                    move = choice(peripherals)
            h = move // board.width
            w = move % board.width
            location = [h, w]
            board.update(player, location)

            # Expand
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
            win, winner = self.has_a_winner(board)
            if is_full or win:
                break

            player = self.get_player(play_turn)

        # Back-propagation
        for player, move in visited_states:
            if (player, move) in plays:
                plays[(player, move)] += 1  # all visited moves
                if player == winner:
                    wins[(player, move)] += 1  # only winner's moves
            if move in plays_rave:
                plays_rave[move] += 1  # no matter which player
                if winner in wins_rave[move]:
                    wins_rave[move][winner] += 1  # each move and every player

    def get_player(self, players):
        p = players.pop(0)
        players.append(p)
        return p

    def select_one_move(self):
#        percent_wins, move = max(
#            (self.wins.get((self.player, move), 0) /
#             self.plays.get((self.player, move), 1),
#             move)
#            for move in self.board.availables)
        moves = {}
        for move in self.board.availables:
#            print('%f %d' % (100*self.wins.get((self.player, move), 0)/self.plays.get((self.player, move), 1), move))
            moves[move] = 100*self.wins.get((self.player, move), 0)/self.plays.get((self.player, move), 1)
        comb = max(zip(moves.values(), moves.keys()))
        move = comb[1]
        print(move)
                                                                        

        # Display the statistics for each possible play,
        # first is MC value, second is AMAF value
        for x in sorted(
                ((100 * self.wins.get((self.player, move), 0) /
                      self.plays.get((self.player, move), 1),
                  100 * self.wins_rave.get(move, {}).get(self.player, 0) /
                      self.plays_rave.get(move, 1),
                  self.wins.get((self.player, move), 0),
                  self.plays.get((self.player, move), 0),
                  self.wins_rave.get(move, {}).get(self.player, 0),
                  self.plays_rave.get(move, 1),
                  self.board.move_to_location(move))
                 for move in self.board.availables),
                reverse=True):
            print('{6}: {0:.2f}%--{1:.2f}% ({2} / {3})--({4} / {5})'.format(*x))
        print(move)
        return move

    def adjacent_moves(self, board, player, plays):
        """
        adjacent moves without statistics info
        """
        moved = list(set(range(board.width * board.height)) - set(board.availables))
        adjacents = set()
        width = board.width
        height = board.height

        for m in moved:
            h = m // width
            w = m % width
            if w < width - 1:
                adjacents.add(m + 1)  # right
            if w > 0:
                adjacents.add(m - 1)  # left
            if h < height - 1:
                adjacents.add(m + width)  # upper
            if h > 0:
                adjacents.add(m - width)  # lower
            if w < width - 1 and h < height - 1:
                adjacents.add(m + width + 1)  # upper right
            if w > 0 and h < height - 1:
                adjacents.add(m + width - 1)  # upper left
            if w < width - 1 and h > 0:
                adjacents.add(m - width + 1)  # lower right
            if w > 0 and h > 0:
                adjacents.add(m - width - 1)  # lower left

        adjacents = list(set(adjacents) - set(moved))
        for move in adjacents:
            if plays.get((player, move)):
                adjacents.remove(move)
        return adjacents

    def has_a_winner(self, board):
        moved = list(set(range(board.width * board.height)) - set(board.availables))
        if (len(moved) < self.n_in_row + 2):
            return False, -1

        width = board.width
        height = board.height
        states = board.states
        n = self.n_in_row
        for m in moved:
            h = m // width
            w = m % width
            player = states[m]

            if (w in range(width - n + 1) and
                        len(set(states[i] for i in range(m, m + n))) == 1):
                return True, player

            if (h in range(height - n + 1) and
                        len(set(states[i] for i in range(m, m + n * width, width))) == 1):
                return True, player

            if (w in range(width - n + 1) and h in range(height - n + 1) and
                        len(set(states[i] for i in range(m, m + n * (width + 1), width + 1))) == 1):
                return True, player

            if (w in range(n - 1, width) and h in range(height - n + 1) and
                        len(set(states[i] for i in range(m, m + n * (width - 1), width - 1))) == 1):
                return True, player

        return False, -1

    def __str__(self):
        return "AI"

# class Game(object):
#     """
#     game server
#     """
#
#     def __init__(self, board, **kwargs):
#         self.board = board
#         self.player = [1, 2]  # player1 and player2
#         self.n_in_row = int(kwargs.get('n_in_row', 5))
#         self.time = float(kwargs.get('time', 5))
#         self.max_actions = int(kwargs.get('max_actions', 1000))
#
#     def start(self):
#         p1, p2 = self.init_player()
#         self.board.init_board()
#
#         ai = MCTS(self.board, [p1, p2], self.n_in_row, self.time, self.max_actions)
#         human = Human(self.board, p2)
#         players = {}
#         players[p1] = ai
#         players[p2] = human
#         turn = [p1, p2]
#         shuffle(turn)
#         self.graphic(self.board, human, ai)
#         while (1):
#             p = turn.pop(0)
#             turn.append(p)
#             player_in_turn = players[p]
#             move = player_in_turn.get_action()
#             self.board.update(p, move)
#             self.graphic(self.board, human, ai)
#             end, winner = self.game_end(ai)
#             if end:
#                 if winner != -1:
#                     print("Game end. Winner is", players[winner])
#                 break
#
#     def init_player(self):
#         plist = list(range(len(self.player)))
#         index1 = choice(plist)
#         plist.remove(index1)
#         index2 = choice(plist)
#
#         return self.player[index1], self.player[index2]
#
#     def game_end(self, ai):
#         win, winner = ai.has_a_winner(self.board)
#         if win:
#             return True, winner
#         elif not len(self.board.availables):
#             print("Game end. Tie")
#             return True, -1
#         return False, -1


def finish():
    pass
