from MCTS_Player import MCTSPlayer
from MCTS_RAVE_Player import MCTS_RAVEPlayer
from Carcassonne import CarcassonneState

import time

def playMultipleGames(p1, p2, games):
    """
    Play a sample of agmes game between AI Players where each player gets a different
    number of UCT iterations (= simulations)
    """
    startTime = time.time()
    
    # start game state
    state = CarcassonneState(p1,p2)
    
    # variables 
    info1, info2 = "",""
    if(p1.name == 'MCTS' or p1.name == 'MCTS_RAVE'):
        isTimeLimitedP1 = p1.isTimeLimited
        if isTimeLimitedP1:
            info1 = f' Time Limited - {p1.timeLimit} seconds'
        else:
            info1 = f' Number of Iterations: {p1.iterations}'
            
    if(p2.name == 'MCTS' or p2.name == 'MCTS_RAVE'):
        isTimeLimitedP2 = p2.isTimeLimited
        if isTimeLimitedP2:
            info2 = f' Time Limited - {p2.timeLimit} seconds'
        else:
            info2 = f' Number of Iterations: {p2.iterations}'
            
    # types of players
    p1_name = (p1.name + 'Player') if (p1.name != 'MCTS') else (p1.name + info1)
    p2_name = (p2.name + 'Player') if (p2.name != 'MCTS') else (p2.name + info2)
    
    # preliminary print statement
    prnt_stat = f'{state.name}, {p1_name} vs. {p2_name}\n'
    print(prnt_stat)
    
    wins = 0
    losses = 0
    number_games = 0
    
    global moves 
    global lost_moves
    global lost_trees
   
    lost_moves = []
    lost_trees = []
    
    for game in range(games):
        
        state = state.reset()
        
        # define players
        p1 = state.p1
        p2 = state.p2
        
        # game loop
        while (not state.isGameOver):
            
            if state.playerSymbol == 1:
                m = p1.chooseAction(state)
            else:
                m = p2.chooseAction(state)
        
            # make the move on the board
            state.move(m)
            
        number_games += 1
        
        # check final results
        if state.winner == 1:
            wins += 1
            #break
        elif state.winner == 2:
            losses += 1
            
    endTime = time.time()
    
    prnt_stat += f'\nGames: {number_games}, Wins: {wins}, Losses: {losses}, Time taken: {round(endTime-startTime, 2)} seconds \n'
    print(prnt_stat)
    


if __name__ == "__main__":
    
    """
    Play 
    """
    
    
    p1 = MCTSPlayer(timeLimit = 10, isTimeLimited = True)
    p2 = MCTS_RAVEPlayer(timeLimit = 10, isTimeLimited = True)
    playMultipleGames(p1,p2, 10)
    
    """
    # players
    players1 = [
        RandomPlayer(),
        MCTSPlayer(iterations = 100),
        #MCTSPlayer(iterations = 500),
        #MCTSPlayer(iterations = 1000),
        #MCTSPlayer(iterations = 1500),
        #MCTSPlayer(timeLimit = 1, isTimeLimited = True),
        #MCTSPlayer(timeLimit = 5, isTimeLimited = True),
        #MCTSPlayer(timeLimit = 10, isTimeLimited = True),
        #MCTSPlayer(timeLimit = 15, isTimeLimited = True),
        #MCTSPlayer(timeLimit = 25, isTimeLimited = True),
        ]
    
    players2 = [
        RandomPlayer(),
        MCTSPlayer(iterations = 100),
        #MCTSPlayer(iterations = 500),
        #MCTSPlayer(iterations = 1000),
        #MCTSPlayer(iterations = 1500),
        #MCTSPlayer(timeLimit = 1, isTimeLimited = True),
        #MCTSPlayer(timeLimit = 5, isTimeLimited = True),
        #MCTSPlayer(timeLimit = 10, isTimeLimited = True),
        #MCTSPlayer(timeLimit = 15, isTimeLimited = True),
        #MCTSPlayer(timeLimit = 25, isTimeLimited = True),
        ]
    
    
    data = []
    
    cpu_set_num = 1
    cpu_count_iter = 0
    
    for p1 in players1:
        for p2 in players2:
            #if (p1.name != "Random") and (p2.name != "Random"):
                
            data.append((p1, p2, 10))
                
    for d in data:
        p1 = d[0]
        p2 = d[1]
        games = d[2]
        
        playMultipleGames(p1,p2,games)
     """       
            
    
    
    