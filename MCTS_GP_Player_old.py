from Player import Player, RandomPlayer

from random import random, randint
from statistics import mean
from copy import deepcopy

import random


import time
import numpy as np
import os
import pandas as pd

class MCTS_GP_Player(Player):
    
    # Player 1 selects the optimal UCT move 
    # Player 2 selects the worst move from Player 1's position
    
    def __init__(self, iterations = 500, timeLimit = 3, isTimeLimited = False, c_param = 9, logs=True):
        super().__init__()
        self.iterations = iterations
        self.timeLimit = timeLimit
        self.isTimeLimited = isTimeLimited
        self.c_param = c_param
        self.name = 'GP_MCTS'
        self.fullName = f'MCTS (Time Limit = {self.timeLimit})' if self.isTimeLimited else  f'MCTS (Iterations = {self.iterations})'
        self.family = "MCTS"
        self.logs = logs
        if self.logs:
            self.cols = ['Name','Simulations','Turn','TimeTaken']
            self.file = self.CreateFile()
        
        
    def ClonePlayer(self):
        Clone = MCTS_GP_Player(self.iterations, self.timeLimit, self.isTimeLimited)
        return Clone
    
    
    def chooseAction(self, state):
        """
        Choose actions using UCT function
        """
        return self.MCTS_Search(state, self.iterations, self.timeLimit, self.isTimeLimited)
    
    
    def MCTS_Search(self, root_state, iterations, timeLimit, isTimeLimited):
        """
        Conduct a UCT search for itermax iterations starting from rootstate.
        Return the best move from the rootstate.
        Assumes 2 alternating players (player 1 starts), with games results in the range [0, 1]
        """
        # Player 1 = 1, Player 2 = 2 (Player 2 wants to the game to be a loss)
        playerSymbol = root_state.playerSymbol
        
        # state the Root Node
        root_node = Node(state = root_state)
        #startTime = time.time()
        
        if self.isTimeLimited:
            self.MCTS_TimeLimit(root_node, root_state)
        else:
            self.MCTS_IterationLimit(root_node, root_state)
                
        # return the node with the highest number of wins from the view of the current player
        if playerSymbol == 1:
            bestMove = sorted(root_node.child, key = lambda c: c.Q)[-1].Move
        else:
            bestMove = sorted(root_node.child, key = lambda c: c.Q)[0].Move
        
        
        return bestMove.move
    
    
    
    def MCTS_IterationLimit(self, root_node, root_state):
        
        startTime = time.time()
        
        isFirstSelected = True
        
        for i in range(self.iterations):
    
            node = root_node
            state = root_state.CloneState()
    
            # Select
            while node.untried_moves == [] and node.child != []:  # node is fully expanded
                GP_tree = False
                if isFirstSelected:
                    # GP search
                    if root_state.Turn >= 40:
                        node.SetGPTree(self.c_param)
                        isFirstSelected = False
                node = node.Search(self.c_param, GP_tree)
                state.move(node.Move.move)
                
            # Expand
            if node.untried_moves != [] and (not state.isGameOver):  # if we can expand, i.e. state/node is non-terminal
                move_random = random.choice(node.untried_moves)
                state.move(move_random.move)
                node = node.AddChild(move = move_random, state = state, isGameOver = state.isGameOver)
                
            # Rollout
            # play random moves until the game reaches a terminal state
            # shuffle deck
            state.shuffle()
            while not state.isGameOver:
                m = state.getRandomMove()
                state.move(m.move)
             
            # Backpropogate
            result = state.checkWinner()
            while node != None:  # backpropogate from the expected node and work back until reaches root_node
                node.UpdateNode(result, self.c_param)
                node = node.parent
                
        # latest time
        endTime = time.time()
     
        # append info to csv
        if self.logs:
            data = {'Name': self.name,'Simulations':self.iterations,'Turn':int((root_state.Turn+1)/2), 'TimeTaken':endTime - startTime}
            self.UpdateFile(data)
    
    
    
            
            
##############################################################################
##############################################################################
##############################################################################


#C_PARAM = 2

class Node:
    """
    The Search Tree is built of Nodes
    A node in the search tree
    """
    
    def __init__(self, Move = None, parent = None, state = None, isGameOver = False):
        self.Move = Move  # the move that got us to this node - "None" for the root
        self.parent = parent  # parent node of this node - "None" for the root node
        self.child = []  # list of child nodes
        self.state = state
        self.untried_moves = state.availableMoves()
        self.playerSymbol = state.playerSymbol
        # keep track of visits/wins/losses
        self.visits = 0
        self.wins = 0
        self.losses = 0
        self.draws = 0
        self.Q = 0
        # UCT score
        self.UCT_high = 0
        self.UCT_low = 0
        # GP search decision
        self.GP_Tree = None
        
    
    def __repr__(self):
        visits = 1 if self.visits == 0 else self.visits
        String = "["
        String += f'Move:{str(self.Move.move)}, Wins:{round(self.wins,1)},'
        String += f' Losses:{self.losses}, Draws:{self.draws}, Q:{round(self.Q,3)},'
        String += f' Wins/Visits:{round(self.wins,1)}/{self.visits} ({round(self.wins/visits,3)}),'
        String += f' UCT_high:{round(self.UCT_high, 3)}, UCT_low:{round(self.UCT_low, 3)},'
        String += f' Remaining Moves:{len(self.untried_moves)}'
        String += "]"
        
        return String
    
    def AddChild(self, move, state, isGameOver):
        """
        Add new child node for this move remove m from list of untried_moves.
        Return the added child node.
        """
        node = Node(Move = move, state = state, isGameOver = isGameOver, parent = self)
        self.untried_moves.remove(move)  # this move is now not available
        self.child.append(node)
        return node
    
    
    def UpdateNode(self, result, c_param):
        """
        Update result and number of visits of node
        """
        self.visits += 1
        self.wins += (result > 0)
        self.losses += (result < 0)
        self.draws += (result == 0)
        self.Q = self.Q + (result - self.Q)/self.visits
        
        for c in self.child:
            c.UCT_high = c.Q + np.sqrt(c_param * np.log(self.visits) / c.visits)
            c.UCT_low = c.Q - np.sqrt(c_param * np.log(self.visits) / c.visits)
        
    
    def SwitchNode(self, move, state):
        """
        Switch node to new state
        """
        # if node has children
        for i in self.child:
            if i.Move == move:
                return i
        
        # if node has no children
        return self.AddChild(move, state)
    
    
    def SetGPTree(self, c_param):
        # get optimal GP_tree          
        self.GP_Tree = GP_Search(self, c_param)
                
    
    def Search(self, c_param, GP_Tree):
        """
        For the first half of the game use the UCB1 formula.
        Else, use GP to find an alternative to UCT 
        """
        
        if GP_Tree:
            
            # values needed from each node
            nodeValues = [[c.Q, c.visits, self.visits, c_param] for c in self.child]
            
            if self.playerSymbol == 1:
                # select the child node that returns the highest value from the calculation
                return self.child[np.argmax([self.GP_Tree.compute_tree(values) for values in nodeValues])]
            else:
                # select the child node that returns the highest value from the calculation
                return self.child[np.argmin([self.GP_Tree.compute_tree(values) for values in nodeValues])]
            
            
        else:
            if self.playerSymbol == 1:
                #  look for maximum output
                choice_weights = [c.Q + np.sqrt(c_param * np.log(self.visits) / c.visits) for c in self.child]
                return self.child[np.argmax(choice_weights)]
            else: 
                #  look for minimum output
                choice_weights = [c.Q - np.sqrt(c_param * np.log(self.visits) / c.visits) for c in self.child]
                return self.child[np.argmin(choice_weights)]



        
############################################################################################################################################################################################################################
############################################################################################################################################################################################################################
############################################################################################################################################################################################################################
############################################################################################################################################################################################################################



POP_SIZE        = 30   # population size
MIN_DEPTH       = 2    # minimal initial random tree depth
MAX_DEPTH       = 7    # maximal initial random tree depth
GENERATIONS     = 10   # maximal number of generations to run evolution
TOURNAMENT_SIZE = 2    # size of tournament for tournament selection
XO_RATE         = 0.7  # crossover rate 
PROB_MUTATION   = 0.01 # per-node mutation probability 

def add(x, y): return x + y
def sub(x, y): return x - y
def mul(x, y): return x * y
def div(x, y): 
    if (abs(y) <= 0.001):
        return x
    else:
        return x/y

def log(x): 
    if x < 1: x = 1
    return np.log(abs(x))

FUNCTIONS = [log, add, sub, mul, div]  # FUNCTIONS[0] = log
TERMINALS = ['Q', 'n', 'N', 'c', 1, 0, -1] 




class GPTree:
    """
        Genetic Programming tree
        values = [Q,n,N,c], from node
    """
    def __init__(self, data = None, left = None, right = None, depth = None, parent = None):
        self.data  = data
        self.left  = left
        self.right = right
        self.parent = parent


    def node_label(self): # string label
        if (self.data in FUNCTIONS):
            return self.data.__name__
        else: 
            return str(self.data)

    
    def print_tree(self, prefix = ""): # textual printout
        print("%s%s" % (prefix, self.node_label()))        
        if self.left:  self.left.print_tree (prefix + "   ")
        if self.right: self.right.print_tree(prefix + "   ")


    def compute_tree(self, values): 
        Q = values[0]
        n = values[1]
        N = values[2]
        c = values[3]
        if self.data == FUNCTIONS[0]:
            return self.data(self.left.compute_tree(values))
        if (self.data in FUNCTIONS): 
            return self.data(self.left.compute_tree(values), self.right.compute_tree(values))
        elif self.data == 'Q': return Q
        elif self.data == 'n': return n
        elif self.data == 'N': return N
        elif self.data == 'c': return c
        else: return self.data
            
        
    def random_tree(self, grow, max_depth, depth = 0): # create random tree using either grow or full method
        if depth < MIN_DEPTH or (depth < max_depth and not grow): 
            self.data = FUNCTIONS[randint(0, len(FUNCTIONS)-1)]
        elif depth >= max_depth:   
            self.data = TERMINALS[randint(0, len(TERMINALS)-1)]
        else: # intermediate depth, grow
            if random.random() > 0.5: 
                self.data = TERMINALS[randint(0, len(TERMINALS)-1)]
            else:
                self.data = FUNCTIONS[randint(0, len(FUNCTIONS)-1)]
        if self.data in FUNCTIONS:
            if self.data == FUNCTIONS[0]:
                self.left = GPTree()          
                self.left.random_tree(grow, max_depth, depth = depth + 1) 
            else:
                self.left = GPTree()          
                self.left.random_tree(grow, max_depth, depth = depth + 1)            
                self.right = GPTree()
                self.right.random_tree(grow, max_depth, depth = depth + 1)


    def mutation(self):
        if random.random() < PROB_MUTATION: # mutate at this node
            self.random_tree(grow = True, max_depth = 2)
        elif self.left: self.left.mutation()
        elif self.right: self.right.mutation() 


    def size(self): # tree size in nodes
        if self.data in TERMINALS: return 1
        l = self.left.size()  if self.left  else 0
        r = self.right.size() if self.right else 0
        return 1 + l + r


    def build_subtree(self): # count is list in order to pass "by reference"
        t = GPTree()
        t.data = self.data
        if self.left:  t.left  = self.left.build_subtree()
        if self.right: t.right = self.right.build_subtree()
        return t
                        
    
    def scan_tree(self, count, second): # note: count is list, so it's passed "by reference"
        count[0] -= 1            
        if count[0] <= 1: 
            if not second: # return subtree rooted here
                return self.build_subtree()
            else: # glue subtree here
                self.data  = second.data
                self.left  = second.left
                self.right = second.right
        else:  
            ret = None              
            if self.left  and count[0] > 1: ret = self.left.scan_tree(count, second)  
            if self.right and count[0] > 1: ret = self.right.scan_tree(count, second)  
            return ret

    def crossover(self, other): # xo 2 trees at random nodes
        if random.random() < XO_RATE:
            second = other.scan_tree([randint(1, other.size())], None) # 2nd random subtree
            self.scan_tree([randint(1, self.size())], second) # 2nd subtree "glued" inside 1st tree
            
        

            

##############################################################################################



#############################################################################################


def init_population(): # ramped half-and-half
    pop = []
    for md in range(3, MAX_DEPTH + 1):
        for i in range(int(POP_SIZE/10)):
            t = GPTree()
            t.random_tree(grow = True, max_depth = md) # grow
            pop.append(t) 
        for i in range(int(POP_SIZE/10)):
            t = GPTree()
            t.random_tree(grow = False, max_depth = md) # full
            pop.append(t) 
    return pop
    



def fitness(individualTree, nodeValues, childNodes, state, i):
    # copy the state
    stateCopy = state.CloneState()
    
    isPlayer1 = (stateCopy.playerSymbol == 1)
    
    # select the child node that returns the highest value from the calculation
    v = [individualTree.compute_tree(values) for values in nodeValues]
    node = childNodes[np.argmax(v)] if isPlayer1 else childNodes[np.argmin(v)] 
    
    # play the move of this child node
    stateCopy.move(node.Move.move)
    
    # from this point simulate the game 10 times appending the results
    results = 0
    for i in range(10):
        stateStart = stateCopy.CloneState()
        # shuffle deck
        stateStart.shuffle()
        
        # random rollout
        while not stateStart.isGameOver:
            m = stateStart.getRandomMove()
            stateStart.move(m.move)
            
        results += stateStart.checkWinner()
    
    # switch results for second player
    results = -results if (not isPlayer1) else results
    
    return results


def selection(population, fitnesses): # select one individual using tournament selection
    tournament = [randint(0, len(population)-1) for i in range(TOURNAMENT_SIZE)] # select tournament contenders
    tournament_fitnesses = [fitnesses[tournament[i]] for i in range(TOURNAMENT_SIZE)]
    return deepcopy(population[tournament[tournament_fitnesses.index(max(tournament_fitnesses))]]) 



def GP_Search(node, c_param):
    """
    Find the best child from the given node
    """
    global nodeValues
    global population
    global fitnesses
    
    state = node.state  # current game state
    
    # initial population
    population = init_population() 

    nodeValues = [[c.Q, c.visits, node.visits, c_param] for c in node.child]
    print(nodeValues)
    
    best_of_run = None
    best_of_run_f = 0
    best_of_run_gen = 0
    best_of_previous_gen = None
    worst_of_previous_gen = None
    
    print(f'Population Size: {len(population)}')
    
    fitnesses = [fitness(population[i], nodeValues, node.child, state, i) for i in range(POP_SIZE)]
    #print(f'Final Results: {fitnesses}, Average: {mean(fitnesses)}')
    
    best_of_previous_gen = population[np.argmax(fitnesses)]
    
    # evolution
    for gen in range(GENERATIONS):
        # new set each time        
        nextgen_population=[]
        for i in range(POP_SIZE):
            
            parent1 = selection(population, fitnesses)
            parent2 = selection(population, fitnesses)
            parent1.crossover(parent2)
            parent1.mutation()
            nextgen_population.append(parent1)
            
            
        population=nextgen_population
        fitnesses = [fitness(population[i], nodeValues, node.child, state, i) for i in range(POP_SIZE)]
        #print(f'Final Results: {fitnesses}, Average: {mean(fitnesses)}')
        worst_of_previous_gen = population[np.argmin(fitnesses)]
        population.remove(worst_of_previous_gen)
        population.append(best_of_previous_gen)
        
        # latest best tree
        best_of_previous_gen = population[np.argmax(fitnesses)]
        
        if max(fitnesses) > best_of_run_f:
            best_of_run_f = max(fitnesses)
            best_of_run_gen = gen
            best_of_run = deepcopy(population[fitnesses.index(max(fitnesses))])
        if best_of_run_f == 1: break
    
    #print("\n\n_________________________________________________\nEND OF RUN\nbest_of_run attained at gen " + str(best_of_run_gen) +\
    #      " and has f=" + str(round(best_of_run_f,3)))
    
    # best tree from final generation
    #print(population[np.argmax(fitnesses)])
    return population[np.argmax(fitnesses)]


