import os
import pandas as pd

class Player:
    """
    Players must be defined in pairs
    
    MCTS player returns the node and the optimal move.
    
    All other player returns None (instead of a node) and the chosen move.
    """
    
    # Player 1 selects the optimal UCT move 
    # Player 2 selects the worst move from Player 1's position
    isFirstPlayer = True
    
    def __init__(self):
        self.isFirstPlayer = Player.isFirstPlayer
        self.name = "No Name"
        self.fullName = "Definitely has no name"
        self.isAIPlayer = True
        self.family = None
        
        # switch
        Player.isFirstPlayer = not Player.isFirstPlayer
        
    
    def chooseAction(self):
        """
        Move choice based on type of player
        """
        pass
    
    def __repr__(self):
        return self.name
    
    
    def CreateFile(self):
        """
        Creates a Unique File for the MCTS and Expectimax Stats
        """
        # name of player
        name = self.name
        
        # current list of files
        current_logs = os.listdir('logs')
        
        # get files of matching names
        matching = [file for file in current_logs if name in file]
        
        # remove specific files from search
        for file in ['ExpectimaxStats.csv', 'FinalLeagueTable.csv', 'MCTSStats.csv', 'PlayerStats.csv']:
            if file in matching:
                matching.remove(file)
    
        # if no files exist so far
        if matching == []:
            df = pd.DataFrame(columns = self.cols)
            new_file = 'logs/' + str(0) + '_' + name + '_Stats.csv'
            df.to_csv(new_file, index=False) 
            return new_file
        
        # get file number of latest file    
        highest_number = max([int(file.split('_')[0]) for file in matching])
        
        # new file number
        next_number = highest_number + 1
        new_file = 'logs/' + str(next_number) + '_' + name + '_Stats.csv'
        
        # blank template file
        df = pd.read_csv('logs/0_' + name + '_Stats.csv')
        
        # create new file
        df.to_csv(new_file, index=False) 
        
        return new_file
    
    
    def UpdateFile(self, data):
        """
        Update csv file with data
        """
        df = pd.read_csv(self.file)  # read in file
        df = df.append(data, ignore_index = True)  # new data
        df.to_csv(self.file, index=False)  # export
        
        
            
class HumanPlayer(Player):
    
    def __init__(self, name = 'Human'):
        super().__init__()
        self.name = name
        self.fullName = "Human Player"
        self.isAIPlayer = False
    
    def chooseAction(self, state, TileIndex):
        """
        state - The current state of the game board
        """
        positions = state.availableMoves(TileIndex)
        
        # user input
        while True:
            print(f'Available moves: \n {positions} \n')
            choice = int(input("Input your choice:"))
            if choice in positions:
                return choice
    
            
class RandomPlayer(Player):
    
    def __init__(self, name = 'Random'):
        super().__init__()
        self.name = name
        self.fullName = "Random Player"
        
    def ClonePlayer(self):
        return self
    
        
    def chooseAction(self, state):
        """
        Make a random move from all possible actions
        """
        return state.getRandomMove().move
    
    

    
    
            
            
