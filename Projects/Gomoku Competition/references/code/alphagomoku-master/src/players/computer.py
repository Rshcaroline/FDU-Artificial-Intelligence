"""
Contains the logic required to run the bot against a board, and make a move.
"""
from copy import deepcopy

from gomokuapp.board import Board, MoveStruct
from players.player import INT_PLAYER_1, INT_PLAYER_2
from treesearch import monte_carlo as mc
from treesearch.monte_carlo import Neural_Network

# Change to True to produce heatmap PDFs
GEN_GRAPH = False

if GEN_GRAPH:
	from graph_main import use_graph_gen

class Computer:
	def __init__(self):
		self.neural_network = Neural_Network()
		self.node = None
		self.player_int = 0

	def make_move(self, brd: Board) -> MoveStruct:
		if self.is_new_game():
			self.set_player_number_for_computer(brd)
			self.create_node(brd)
		else:
			last_move = brd.get_last_move()
			assert last_move is not None, "Expected to have received a move but was None"
			node_found = self.update_node_to_child(last_move)
			if not node_found:
				self.create_node(brd, last_move)

		if GEN_GRAPH:
			use_graph_gen(self.node._board, self.neural_network)

		self.node = self.node.get_play()
		x, y = self.node.get_move()

		return x, y

	def is_new_game(self) -> bool:
		return self.node is None

	def create_node(self, brd: Board, move: MoveStruct = (None, None)):
		board = deepcopy(brd)
		self.node = mc.Node(move, board, self.neural_network, self.player_int)

	def set_player_number_for_computer(self, board: Board):
		if board.get_last_move() is None:
			self.player_int = INT_PLAYER_1
		else:
			self.player_int = INT_PLAYER_2

	def update_node_to_child(self, last_move: MoveStruct) -> bool:
		for child in self.node.children:
			if child.get_move() == last_move:
				self.node = child
				return True
		return False
