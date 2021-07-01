from Player import Player

import operator
import numpy as np
import time
import random
from statistics import mean

from deap import algorithms
from deap import base
from deap import creator
from deap import tools
from deap import gp



class MCTS_GP_Player(Player):
    
    # Player 1 selects the optimal UCT move 
    # Player 2 selects the worst move from Player 1's position
    
    def __init__(self, iterations = 500, timeLimit = 3, isTimeLimited = False, c_param = 9, logs=False):
        super().__init__()
        self.iterations = iterations
        self.timeLimit = timeLimit
        self.isTimeLimited = isTimeLimited
        self.c_param = c_param
        self.name = 'GP_MCTS'
        self.fullName = f'MCTS (Time Limit = {self.timeLimit})' if self.isTimeLimited else  f'MCTS (Iterations = {self.iterations})'
        self.family = "MCTS"
        self.logs = logs
        self.hasGPTree = False
        self.GPTree = None
        if self.logs:
            self.cols = ['Name','Simulations','Turn','TimeTaken']
            self.file = self.CreateFile()
        
        
    def ClonePlayer(self):
        Clone = MCTS_GP_Player(iterations=self.iterations, timeLimit=self.timeLimit, isTimeLimited = self.isTimeLimited, 
                               c_param=self.c_param, logs=self.logs)
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
        
        for i in range(self.iterations):
    
            node = root_node
            state = root_state.CloneState()
    
            # Select
            while node.untried_moves == [] and node.child != []:  # node is fully expanded
                if not self.hasGPTree:
                    # GP search
                    if root_state.Turn >= 40:
                        # get the GPTree of this turn
                        self.GPTree = GP_Search(node, self.c_param, self.hasGPTree, self.GPTree)
                        self.hasGPTree = True
                node = node.Search(self.c_param, self.hasGPTree, self.GPTree)
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
        
        print(f'(GP_MCTS) TimeTaken: {round(endTime - startTime,3)} secs, Time:{time.strftime("%H:%M:%S", time.localtime())}')
        
        
        # reset GP info
        self.GPTree = None
        self.hasGPTree = False
     
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
    
    
    def Search(self, c_param, hasGPTree, GPTree):
        """
        For the first half of the game use the UCB1 formula.
        Else, use GP to find an alternative to UCT 
        """
        # select the child chosen from the GP tree
        if hasGPTree:
            return GP_Search(self, c_param, hasGPTree, GPTree)
        # else, use normal UCT
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





def GP_Search(node, c_param, hasGPTree=False, GPTree=None):
    """
    Find the best child from the given node
    """
    
    state = node.state  # current game state
    nodeValues = [[c.Q, c.visits, node.visits, c_param] for c in node.child] # values of the nodes
    
    
    # set the number of inputs - [Q,n,N,c]
    pset = gp.PrimitiveSet("MAIN", 4)
    
    # Define new functions
    def div(left, right):
        if (abs(right) < 0.001):
            return 1
        else:
            return left/right
        
    # natural log
    def ln(left): 
        if left == 1: left = 1.001
        if left < 0.01: left = 0.01
        return np.log(abs(left))

    # add operators
    pset.addPrimitive(operator.add, 2)
    pset.addPrimitive(operator.sub, 2)
    pset.addPrimitive(operator.mul, 2)
    pset.addPrimitive(div, 2)
    pset.addPrimitive(operator.neg, 1)
    pset.addPrimitive(ln, 1)

    # rename the arguments
    pset.renameArguments(ARG0='Q')
    pset.renameArguments(ARG1='n')
    pset.renameArguments(ARG2='N')
    pset.renameArguments(ARG3='c')

    # want to maximise the solution
    creator.create("FitnessMax", base.Fitness, weights=(1.0,))
    # define the structure and the 
    creator.create("Individual", gp.PrimitiveTree, fitness=creator.FitnessMax) 
    
    #  register the generation functions into a Toolbox
    toolbox = base.Toolbox()
    toolbox.register("expr", gp.genHalfAndHalf, pset=pset, min_=1, max_=5)
    toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.expr)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    toolbox.register("compile", gp.compile, pset=pset)


    def evalTree(individual, nodeValues, state, childNodes):
        # Transform the tree expression in a callable function
        func = toolbox.compile(expr=individual)
        
        # copy the state
        stateCopy = state.CloneState()
        isPlayer1 = (stateCopy.playerSymbol == 1)
        
        # get the values of the tree for each child node
        v =  [func(Q,n,N,c) for Q,n,N,c in nodeValues]
        node = childNodes[np.argmax(v)] if isPlayer1 else childNodes[np.argmin(v)]
        
        # play the move of this child node
        stateCopy.move(node.Move.move)
        
        # from this point simulate the game 10 times appending the results
        SIMULATIONS = 10
        results = 0
        for i in range(SIMULATIONS):
            #print(f'Simulation {i+1} out of {SIMULATIONS}')
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
        return results/SIMULATIONS,
        

    
    # register gp functions
    toolbox.register("evaluate", evalTree, nodeValues=nodeValues, state=state, childNodes=node.child)
    toolbox.register("select", tools.selTournament, tournsize=2)
    toolbox.register("mate", gp.cxOnePoint)
    toolbox.register("expr_mut", gp.genFull, min_=0, max_=5)
    toolbox.register("mutate", gp.mutUniform, expr=toolbox.expr_mut, pset=pset)
    
    toolbox.decorate("mate", gp.staticLimit(key=operator.attrgetter("height"), max_value=17))
    toolbox.decorate("mutate", gp.staticLimit(key=operator.attrgetter("height"), max_value=17))
    
    # if MCTS already has a gpTree, return the values for each child
    if hasGPTree:
        playerSymbol = state.playerSymbol
        nodeValues = [[c.Q, c.visits, node.visits, c_param] for c in node.child]
        func = toolbox.compile(expr=GPTree)
        values = [func(Q,n,N,c) for Q,n,N,c in nodeValues]
        #print("(GPSeacrh - Returning optimal child")
        if playerSymbol == 1:
            return node.child[np.argmax(values)]
        else:
            return node.child[np.argmin(values)]
    
    # else, find the optimal tree using GP 
    else:
    
        random.seed(318)
        
        pop = toolbox.population(n=30)
        print(f'pop: {len(pop)}')
        hof = tools.HallOfFame(1)
            
        stats_fit = tools.Statistics(lambda ind: ind.fitness.values)
        stats_size = tools.Statistics(len)
        mstats = tools.MultiStatistics(fitness=stats_fit, size=stats_size)
        mstats.register("avg", np.mean)
        mstats.register("std", np.std)
        mstats.register("min", np.min)
        mstats.register("max", np.max)
        
        pop, log = algorithms.eaSimple(pop, toolbox, 0.7, 0.01, 10, stats=mstats,
                                           halloffame=hof, verbose=True)
        # return the best tree
        #print("(GPSeacrh) - Returning best tree")
        return hof[0]
    
    







