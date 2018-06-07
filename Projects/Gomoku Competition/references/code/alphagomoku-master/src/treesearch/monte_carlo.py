import math
import random
from copy import deepcopy
from datetime import datetime, timedelta
from typing import List

from numpy.random import choice

from gomokuapp.board import BOARD_SIZE
from gomokuapp.board import Board, MoveStruct
from neuralnetwork.neural_network import setup_network, use_network, reset_default_graph


class Neural_Network:
	def __init__(self):
		self.training_input, self.heuristic, self.keep_prob, self.tf_output, self.sess = setup_network()

	def nn(self, board: Board, player) -> float:
		return use_network(board.get_board(), self.training_input, self.heuristic, self.keep_prob, self.tf_output,
		                   self.sess, player)

	'''
		This resets the tensorflow graph and keeps it running at 0.01 seconds per use.

		If this isn't called after at least every 200 calls the time per use for the nn will increase with each call.
	'''

	def clear_garbage_from_nn(self):
		reset_default_graph()
		self.training_input, self.heuristic, self.keep_prob, self.tf_output, self.sess = setup_network()


nodes_created = 0

class Node:
<<<<<<< HEAD
	DEFAULT_DEPTH = 0
	DEFAULT_BREADTH = 4
=======
	DEFAULT_DEPTH = 1
	DEFAULT_BREADTH = 1
>>>>>>> 8543d584518b4ed9d95ac3dfac1e6821a56a3e19
	DEFAULT_TIME_SECONDS = 5
	WIN_VALUE = 1

	"""
	Represents a move that can be made, how good that move is, and what moves can be made after it.
	"""

	def __init__(self, move: MoveStruct, board: Board, neural_network: Neural_Network, player_for_computer: int):
		global nodes_created
		nodes_created += 1
		self._explore_count = 1
		self.children = []
		self.x, self.y = move
		self._board = board
		self.neural_network = neural_network
		self.player = self.get_player_of_node()
		self.player_for_computer = player_for_computer

		# Value between -1 and 1, where 1 means we've won, and -1 means we've lost.
		self._default_value = self.WIN_VALUE if self.is_winning_move() else self.neural_network.nn(self._board, self.player)
		self._default_value = self.negate_score_for_opponent_node(self._default_value)
		self.value = self._default_value

	def is_winning_move(self) -> bool:
		return self._board.decide_winner()[0] is not 0

	def get_player_of_node(self) -> int:
		# - because the board will have the player which is about to move not the player for which this node belongs
		return -self._board.get_next_player()

	def get_move(self) -> MoveStruct:
		return self.x, self.y

	def explore(self):
		self._explore_count += 1
		player_to_move = self._board.get_next_player()
		played_moves = self._board.get_played_moves()
		moves = self.get_playable_moves(played_moves)
		# print("Exploring %r,%r: %r" % (self.x, self.y, moves))
		for x, y in moves:
			# print(x,y,self.player_to_move)
			assert self._board.move(x, y, player_to_move)
			child = self.create_child_node(x, y)
			self.children.append(child)
			reversed_move = self._board.reverse_move()
			assert reversed_move == (x, y, player_to_move), "%r vs %r" % (reversed_move, (x, y, player_to_move))
		# print(self.debug_nn_outputs)

		self.children = sorted(self.children, key=lambda child: child.value, reverse=True)

	def create_child_node(self, x: int, y: int) -> "Node":
		next_board = deepcopy(self._board)
		child = Node((x, y), next_board, self.neural_network, self.player_for_computer)
		return child

	def _monte_carlo_score(self, child: "Node") -> float:
		value = child.value
		node_count = child._explore_count
		total_count = sum(c._explore_count for c in self.children)
		score = value + (2 * math.log(total_count) / node_count) ** 0.5
		# print("Monte carlo score: (%r) (%r)" % (child, score))
		return score

	def _select_children(self, children: List["Node"]) -> List["Node"]:
		return sorted(children, key=self._monte_carlo_score, reverse=True)

	def get_play(self, depth: int = DEFAULT_DEPTH, breadth: int = DEFAULT_BREADTH, time_seconds: int = DEFAULT_TIME_SECONDS) -> "Node":
		global nodes_created
		start_time = datetime.utcnow()
		while (datetime.utcnow() - start_time) < timedelta(seconds=time_seconds):
			nodes_created = 0
			self.neural_network.clear_garbage_from_nn()
<<<<<<< HEAD
			child = self.select(depth, breadth)
		for kid in self.children:
			print(kid.value)
			print(kid.x)
			print(kid.y)
			print("-")
		print(child.value)
		print(child.x)
		print(child.y)
		# print(datetime.utcnow() - start_time)
		return child
=======
			self.select(depth, breadth)
			winning = sorted(self.children, key=lambda c:c.value)[-1]
			print("%r, Time: %ds, Nodes: %r" % (winning._board.get_last_move(), (datetime.utcnow() - start_time).seconds, nodes_created))
			print()
		print("Making move %r: %ds" % (winning._board.get_last_move(), (datetime.utcnow() - start_time).seconds))
		return winning
>>>>>>> 8543d584518b4ed9d95ac3dfac1e6821a56a3e19

	def select(self, depth: int = DEFAULT_DEPTH, breadth: int = DEFAULT_BREADTH) -> "Node":
		if len(self.children) == 0:
			depth -= 1
			self.explore()

		winning_node = self.check_for_winning_node()
		if winning_node is not None:
			return winning_node

		children_to_explore = self._select_children(self.children)[:breadth]
		if depth > 0:
			for child in children_to_explore:
				child.select(depth)

		self.add_child_scores_to_value()

<<<<<<< HEAD
		children_to_explore = sorted(children_to_explore, key=lambda child: child.get_value(), reverse=True)
		print("whores")
		print(self.x)
		print(self.y)
		print("[")
		for kid in children_to_explore:
			print(kid.value)
		print("]")
=======
		children_to_explore = sorted(children_to_explore, key=lambda child: child.value, reverse=True)
>>>>>>> 8543d584518b4ed9d95ac3dfac1e6821a56a3e19
		return children_to_explore[0] if children_to_explore else None

	def negate_score_for_opponent_node(self, v: int) -> int:
		if self.player != self.player_for_computer:
			return -v
		return v

	def add_child_scores_to_value(self):
<<<<<<< HEAD
		self.value = self.set_default_value()
		self.value = ((self.value * 0.5) + (sum(c.value for c in self.children) * 0.5)) / (len(self.children) + 1)
		self.negate_score_for_opponent_node()
=======
		self.value = (self._default_value + sum(c.value for c in self.children)) / (len(self.children) + 1)
		self.value = self.negate_score_for_opponent_node(self.value)
>>>>>>> 8543d584518b4ed9d95ac3dfac1e6821a56a3e19

	def check_for_winning_node(self) -> "Node":
		for child in self.children:
			if child.value == self.WIN_VALUE:
				return child

	def get_playable_moves(self, played_moves: list) -> list:
		print(played_moves)
		if len(played_moves) > 0:
			moves = self.get_adjacent_moves(played_moves)
		else:
			# Todo: Replace with a better selection method.
			# Computer goes first so try from 10 random moves. Will most likely want to change at some point
			moves = self.pick_from_random()
		return moves

	def get_adjacent_moves(self, played_moves: list) -> set:
		adjacent_moves = []
		for move in played_moves:
			x = move[0]
			y = move[1]
			go_up = (x, y - 1)
			go_up_right = (x - 1, y - 1)
			go_right = (x - 1, y)
			go_down_right = (x - 1, y + 1)
			go_down = (x, y + 1)
			go_down_left = (x + 1, y + 1)
			go_left = (x + 1, y)
			go_up_left = (x + 1, y - 1)
			adjacent_moves.extend(
				(go_up, go_up_right, go_right, go_down_right, go_down, go_down_left, go_left, go_up_left))
		adjacent_moves = filter(lambda move: move not in played_moves and self.valid_coordinate(move), adjacent_moves)
		adjacent_moves = set(adjacent_moves)
		return adjacent_moves

	def valid_coordinate(self, move: MoveStruct) -> bool:
		return all(map(lambda x: 0 <= x < BOARD_SIZE, move))

	def pick_from_random(self) -> list:
		random_moves = []
		for i in range(0, 10):
			x = random.randint(0, BOARD_SIZE - 1)
			y = random.randint(0, BOARD_SIZE - 1)
			random_moves.append((x, y))
		return random_moves

	def __str__(self):
		return (self.x, self.y).__str__()