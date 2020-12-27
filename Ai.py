import engine
import random
import utils

def evaluate_board(gs, color):
	pieceValues = {
		"p": 100,
		"N": 320,
		"B": 330,
		"R": 500,
		"Q": 900,
		"K": 20000
	}

	value = 0
	for row in range(len(gs.board)):
		for col in range(len(gs.board)):
			if gs.board[row][col] != "--":
				value += pieceValues[gs.board[row][col][1]] * (1 if gs.board[row][col][0] == color else -1)
	return value

def min_max_search(depth, gs, playerColor, alpha = -10**16, beta = 10**16, isMaximizingPlayer=True):
	if depth == 0:
		pieceValue = evaluate_board(gs, playerColor)
		positionalValue = utils.position_evaluation(gs)
		value = pieceValue + positionalValue
		return value, None
	bestMove = None
	moves = gs.get_all_valid_moves()
	random.shuffle(moves)

	bestMoveValue = (-10**16 if isMaximizingPlayer else 10**16)
	for move in moves:
		gs.make_move(move)
		value = min_max_search(depth - 1, gs, playerColor, alpha, beta, not isMaximizingPlayer)[0]

		if isMaximizingPlayer:
			if value > bestMoveValue:
				bestMoveValue = value
				bestMove = move
			alpha = max(alpha, value)
		else:
			if value < bestMoveValue:
				bestMoveValue = value
				bestMove = move
			beta = min(beta, value)
		gs.undo_move()

		if beta <= alpha:
			break

	return bestMoveValue, bestMove 