"""
Tic Tac Toe Player
"""
import copy
import math

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    # TODO
    '''
    parameters: board state
    return: player turn (X or O)

    initial game state: X is first move

    any return value is acceptable if a terminal board is provided as input
    '''
    elements = []
    for r in board:
        [elements.append(c) for c in r]
    
    x_count = elements.count(X)
    o_count = elements.count(O)
    value = X if ((x_count <= o_count) or (board == initial_state())) else O
    return value


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    # TODO
    '''
    return: set of all possible actions that can be taken on a given board
    
    - each action should be represented as a tuple (i,j)
    - possible moves are any cells on the board that do not already have an X or an O in them
    
    any return value is acceptable if a terminal board is provided as input
    '''
    actions_list = []
    for i, r in enumerate(board): 
        for j, c in enumerate(r):
            if c == EMPTY: 
                actions_list.append((i,j))
    
    return actions_list



def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    # TODO
    '''
    parameters: board, action
    return: new board state without modifying the original board

    - raise exception for invalid action
    - returned board state should be the board that would result from taking the original input board, 
    and letting the player whose turn it is make their move at the cell indicated by the input action
    - the original board should be left unmodified, since minimax will ultimately require considering many 
    different board states during its computation. simply updating a cell in board itself is not a correct 
    implementation of the result function (make a deep copy of the board first before making any changes)
    '''

    x_coord, y_coord = action

    prev_board = copy.deepcopy(board)
    player_turn = player(board)

    prev_board[x_coord][y_coord] = player_turn

    return prev_board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    # TODO
    '''
    parameters: board 
    return: winner if any (return X if winner is X and O if the opposite)

    winning condition: 3 in a row, horiz, vert, diag
    at most 1 winner 
    return None if tie 
    '''
    cases = []
    col = []
    
    for i, row in enumerate(board):
        # check columns
        cl = []
        [cl.append(r[i]) for r in board]
        col.append(cl)
    
    # check diagonal

    diag_1 = [r[j] for j, r in enumerate(board)]
    diag_2 = [r[len(board) - j - 1] for j, r in enumerate(board)]


    [cases.append(row) for row in board]
    [cases.append(c) for c in col]
    cases.append(diag_1)
    cases.append(diag_2)

    for case in cases: 

        c = list(set(case))
        if len(c) == 1 and None not in c:
            # winner found 
            winner = X if X in c else O
            return winner 
        
    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    # TODO
    '''
    parameters: board
    return: bool if game is over

    return True if game is over (win or draw)
    return False if game is still in progress 

    terminal: 3 in a row, or no empty
    '''
    
    if winner(board) is not None:
        # Cases where there is a winner
        return True 
    else:
        for r in board:
            if None in r:
                # Game still in progress
                return False
            
        # Tie
        return True



def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    # TODO
    '''
    parameters: board
    return: 1 if X won the game, -1 if O, 0 if draw
    will only be called on a board if terminal(board) is True
    '''

    return 1 if winner(board) == X else -1 if winner(board) == O else 0
  
def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    # TODO
    '''
    parameters: board
    return: optimal move

    return tuple (i, j) that is one of the allowable actions on the board
    return any if moves are equally optimal

    return None if board is terminal

    LECTURE NOTES:
    given states, the max player picks action a in actions that produces highest 
    min-value(results(s,a))

    and vice versa
    '''
    ai_player = player(board)
    v, a = max_value(board) if ai_player == X else min_value(board)

    return a

'''
For all functions that accept board as input, you may assume that it is a valid board (list that contains 3 rows each with 3 values)
do not modify function declarations
'''

### ADDITIONAL HELPER FUNCTIONS ###
def max_value(board):
    '''
    state = board
    LECTURE NOTES
    v = - inf
    if terminal(state):
        return utility(state)

    for action in actions(state):
        v = max(v, min-value(result(state, action)))
        return v
    '''
    v = float('-inf')

    if terminal(board):
        return utility(board), None

    for action in actions(board):
        ret, n = min_value(result(board, action))
        if ret > v: 
            v = ret 
            a = action 
            if v == 1:
                # terminal state, X has won
                return v, a
        
    return v, a

def min_value(board):
    '''
    state = board
    LECTURE NOTES
    v = infinity
    if terminal(state):
        return utility(state)

    for action in actions(state):
        v = min(v, max-value(result(state, action)))
        return v
    '''
    v = float('inf')
    if terminal(board):
        return utility(board), None

    for action in actions(board):
        ret, n = max_value(result(board, action))
        if ret < v:
            v = ret 
            a = action
            if v == -1:
                # terminal state, O has won 
                return v, a

    return v, a 
