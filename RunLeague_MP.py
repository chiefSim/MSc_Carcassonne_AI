from Player import RandomPlayer
from MCTS_Player import MCTSPlayer
from MCTS_RAVE_Player import MCTS_RAVEPlayer
from MCTS_GP_Player import MCTS_GP_Player
from MCTS_ES_Player import MCTS_ES_Player
from MCTS_TREE_ES_Player import MCTS_TREE_ES_Player
from MCTS_HALF_TREE_ES_Player import MCTS_HALF_TREE_ES_Player
from Star1_Player import Star1
from Star2_5_Player import Star2_5

from Carcassonne import CarcassonneState

import os
import time
import pandas as pd
from datetime import date
from collections import OrderedDict
import random

import multiprocessing as mp




iterations = 500
EA_iterations = 400
logs = True

PLAYER_LIST = [
    MCTSPlayer(iterations=iterations, logs=True),
    MCTS_RAVEPlayer(iterations=iterations, logs=True),
    MCTS_GP_Player(iterations=iterations, logs=True),
    MCTS_ES_Player(iterations=EA_iterations, logs=True),
    MCTS_TREE_ES_Player(iterations=EA_iterations, logs=True),
    MCTS_HALF_TREE_ES_Player(iterations=iterations, logs=True),
    #RandomPlayer(),
    #Star1(Init=Init),
    #Star2_5(Init=Init)
    ]

GAMES = 15





###################################################

###################################################


def RunLeague(players=PLAYER_LIST, gamesPerMatch=GAMES):

    # number of players
    n = len(players)
    
    # initial statement
    print(f'Welcome to the start of a new League \nDate: {date.today().strftime(("%d %B, %Y"))} \n')
    
    # print each competitor
    print('Here are the competitors: \n')
    i = 1
    for player in players:
        print(f'{i}. {player}')
        i += 1
        
    # create league table
    data = {
        "Pos": list(range(1,n+1)),
        "Player": [player for player in players], 
        "MatchesPlayed": n*[0], 
        "Points": n*0, 
        "BWP": n*0, 
        "BLP": n*0, 
        "W": n*0, 
        "L": n*0, 
        "D": n*0, 
        "PD": n*0
        }
    # create pandas league table
    df_league = pd.DataFrame(OrderedDict(data))
    # create empty log files
    df_league.to_csv('logs/FinalLeagueTable.csv', index=False)
    
    
    # get full fixture list
    fixtures = Fixtures(players)
    
    # initialize full list of games
    fixtureGames = []
    
    fixtureSetNumber = 1
    # each set of fixtures
    for fixtureSet in fixtures:
        j = 1
        for pairing in fixtureSet:
            
            if 'Idle' in pairing: # skip match if there is an 'Idle' player
                continue
            
            p1name = pairing[0].name
            p2name = pairing[1].name
            
            if p1name != p2name:
                player1 = pairing[0].ClonePlayer()
                player2 = pairing[1].ClonePlayer()
                
                j += 1
                # add game to list
                fixtureGames.append((player1, player2, gamesPerMatch, fixtureSetNumber))
        
        # increment by 1
        fixtureSetNumber += 1
        
    # multiprocessing, play multiple games
    pool = mp.Pool(mp.cpu_count())
    pool.map(PlayFullMatchMultiWrapper, fixtureGames)
    
    # group all files together
    CombineFiles()
    
    


def PlayFullMatchMultiWrapper(args):
    PlayFullMatch(*args)

    
def Fixtures(players):
    """
    Returns a round robin fixture with "home-and-away" results
    """
    # need an even amount of players
    if len(players) % 2:
        players.append("Idle")
    
    n = len(players)
    
    matchs = []  # individual matches (P1 vs P2)
    fixtures = []  # set of matches containing each player [(P1 vs. P2), (P3 vs. P4)]
    return_matches = []
    for fixture in range(1, n):
        for i in range(n//2):
            matchs.append((players[i], players[n - 1 - i]))
            return_matches.append((players[n - 1 - i], players[i]))
        players.insert(1, players.pop())
        fixtures.insert(len(fixtures)//2, matchs)
        fixtures.append(return_matches)
        matchs = []
        return_matches = []
    
    return fixtures
  

    
def CombineFiles():
    """
    Group the individual files and combine them into one file
    """
    
    # current list of files
    current_logs = os.listdir('logs')

    # split files into groups
    expecetimaxGroup = [file for file in current_logs if 'Star' in file]
    mctsGroup = [file for file in current_logs if 'MCTS' in file or 'M_RAVE' in file]
    statsGroup = [file for file in current_logs if 'Match_Stats' in file]

    groups = [expecetimaxGroup, mctsGroup, statsGroup]
    fileNames = ['ExpectimaxStats', 'MCTSStats', 'PlayerStats']

    i = 0

    for group in groups:
        if group == []:
            i += 1
            continue
        first = True
        
        for file in group:
            if first:
                df = pd.read_csv('logs/' + file)
                first = False
            else:
                dfNew = pd.read_csv('logs/' + file)
                df = df.append(dfNew)
        
        df.to_csv('logs/' + fileNames[i] + '.csv', index=False)
        i += 1


    


    

def PlayOneGame(player1, player2, gameNumber, fixtureSetNumber, dfStats, showLogs=False):
    """
    Plays a single game between two players
    """
    times = [[],[]] # record each player's play time
    numberMeeples = [0,0] # record number of meeples each player places
    meepleTurn = [[],[]] # record when each player plays a meeple
    meepleFeature = [[],[]]  # record what feature they place meeple on
    
    # record time of game
    startTime = time.time()
    
    # begin the game state
    state = CarcassonneState(player1, player2)
    
    # record the turn number
    turns = [1,1]
    
    # game loop
    while (not state.isGameOver):
        
        if state.playerSymbol == 1:
            # calculate move time
            initialMoveTime = time.time()
            m = player1.chooseAction(state) # make move
            endMoveTime = time.time()
            times[0].append(endMoveTime - initialMoveTime)
            # record meeple info
            if (m != 0) and (m[4] is not None):
                numberMeeples[0] += 1  # meeple has been played
                meepleTurn[0].append(turns[0])  # record turn
                meepleFeature[0].append(m[4][0])  # record feature type
            turns[0] += 1
            
        else:
            # calculate move time
            initialMoveTime = time.time()
            m = player2.chooseAction(state) # make move
            endMoveTime = time.time()
            times[1].append(endMoveTime - initialMoveTime)
            # record meeple info
            #print(m)
            if (m != 0) and (m[4] is not None):
                numberMeeples[1] += 1  # meeple has been played
                meepleTurn[1].append(turns[1])  # record turn
                meepleFeature[1].append(m[4][0])  # record feature type
            turns[1] += 1
        
        # make the move on the board
        state.move(m)
    
    # final scores
    finalScore = state.Scores
    # winner (1 = P1 wins, 2 = P2 wins, 0 = Draw)
    winner = state.winner
    # result = P1 score - P2 Score
    result = state.result
    
    # game time 
    endTime = time.time()
    timeTaken = endTime-startTime
    
    print(f'\nGame Over: \nFixture Set: {fixtureSetNumber},  Game: {gameNumber}, Players:  {player1}  vs. {player2}')
    
    gameResult = 'Draw' if winner == 0 else f'Player{winner} Wins'
    
    # update players stats table
    dfStats = UpdateStatsTable(player1, player2, gameNumber, fixtureSetNumber, dfStats, finalScore, winner, state.FeatureScores, times, numberMeeples, meepleTurn, meepleFeature, turns)
    
    if showLogs:
        print(f'    Game {gameNumber}, Player1: {finalScore[0]} - Player2: {finalScore[1]}      {gameResult}     (Time: {int(timeTaken//60)} Mins {int(timeTaken%60)} Secs)')
    # return results of game
    return winner, result, timeTaken, dfStats



def UpdateStatsTable(player1, player2, gameNumber, fixtureSetNumber, dfStats, finalScore, winner, FeatureScores, times, numberMeeples, meepleTurn, meepleFeature, turns):
    """
    Update a players stats after each game
    """
    # new data to be added
    data = {"FixtureSet": fixtureSetNumber, "Game": gameNumber, "Player": player1, "Opponent": player2, "Result": winner,
            "Win":int(winner==1), "Loss":int(winner==2), "Draw":int(winner==0), 
            "PlayerScore": finalScore[0], "OpponentScore": finalScore[1], "CompleteCityScore": FeatureScores[0][0], 
            "CompleteRoadScore": FeatureScores[0][1], "CompleteMonasteryScore": FeatureScores[0][2], 
            "IncompleteCityScore": FeatureScores[0][3], "IncompleteRoadScore": FeatureScores[0][4], 
            "IncompleteMonasteryScore": FeatureScores[0][5], "FarmScore": FeatureScores[0][6],
            "MeeplesPlayed": numberMeeples[0], "MeepleTurns": [meepleTurn[0]], "MeepleFeatures": [meepleFeature[0]], 
            "Turns": turns[0], "AvgTurnTime": (sum(times[0]))/turns[0]}
    p1_data = pd.DataFrame(data)
    dfStats = dfStats.append(p1_data)  # add new data to table
    
    # new data to be added
    data = {"FixtureSet": fixtureSetNumber, "Game": gameNumber, "Player": player2, "Opponent": player1, "Result": (3-winner)%3,
            "Win":int(winner==2), "Loss":int(winner==1), "Draw":int(winner==0), 
            "PlayerScore": finalScore[1], "OpponentScore": finalScore[0], "CompleteCityScore": FeatureScores[1][0], 
            "CompleteRoadScore": FeatureScores[1][1], "CompleteMonasteryScore": FeatureScores[1][2], 
            "IncompleteCityScore": FeatureScores[1][3], "IncompleteRoadScore": FeatureScores[1][4], 
            "IncompleteMonasteryScore": FeatureScores[1][5], "FarmScore": FeatureScores[1][6],
            "MeeplesPlayed": numberMeeples[1], "MeepleTurns": [meepleTurn[1]], "MeepleFeatures": [meepleFeature[1]], 
            "Turns": turns[1], "AvgTurnTime": (sum(times[1]))/turns[1]}
    p2_data = pd.DataFrame(data)
    dfStats = dfStats.append(p2_data)  # add new data to table
    
    return dfStats



def CreateNewStatsFile():
    """
    A new stats file per match
    """
    # create a table of stats for all players
    columnNames = ["FixtureSet", "Game", "Player", "Opponent", "Result", "Win", "Loss", "Draw", 
               "PlayerScore", "OpponentScore", "CompleteCityScore", "CompleteRoadScore", 
               "CompleteMonasteryScore", "IncompleteCityScore", "IncompleteRoadScore", 
               "IncompleteMonasteryScore", "FarmScore","MeeplesPlayed", "MeepleTurns", 
               "MeepleFeatures", "Turns", "AvgTurnTime"]
    dfStats = pd.DataFrame(columns = columnNames)
    
    # current list of files
    current_logs = os.listdir('logs')
    
    # get files of matching names
    matching = [file for file in current_logs if 'Match_Stats' in file]
    print(f'Matching: {matching}')

    # if no files exist so far
    if matching == []:
        new_file = 'logs/0_Match_Stats.csv'
        print(new_file)
        dfStats.to_csv(new_file, index=False) 
        return new_file, dfStats
    
    # get file number of latest file    
    highest_number = max([int(file.split('_')[0]) for file in matching])
    
    # new file number
    next_number = highest_number + 1
    new_file = 'logs/' + str(next_number) + '_Match_Stats.csv'
    print(new_file)
    
    # create new file
    dfStats.to_csv(new_file, index=False) 
    return new_file, dfStats



def PlayFullMatch(player1, player2, gamesPerMatch, fixtureSetNumber, showLogs=False):
    """
    Play a full set of games between two players
    """
    print("\n###############################################\n\n###############################################")
    print(f'Fixture Set: {fixtureSetNumber},  Players:  {player1}  vs. {player2}')
    winners = [0,0,0]  # [P1 wins, P2 wins, Draws]
    results = []  # points difference of each games
    timePerMatch = []
    
    # wait a few seconds between each file being made
    n1 = random.randint(0, 100)
    n2 = random.randint(20, 80)
    time.sleep(n1/n2)
    new_file, dfStats = CreateNewStatsFile()
    
    for game in range(gamesPerMatch):
        winner, result, timeTaken, dfStats = PlayOneGame(player1, player2, game+1, fixtureSetNumber, dfStats)
        # record the results
        winners[(winner-1)%3] += 1
        results.append(result)
        timePerMatch.append(timeTaken)
        
    # update league table
    UpdateLeagueTable(player1, player2, gamesPerMatch, winners, results)
    
    # export stats table
    dfStats.to_csv(new_file, index=False) 
    
    if showLogs:
        print(f'Games:{gamesPerMatch} - Player1 Wins:{winners[0]}    Player2 Wins:{winners[1]}    Draws:{winners[2]}')



def UpdateLeagueTable(player1, player2, gamesPerMatch, winners, results):
    """
    Update table with the results after a full match
    """
    # read in latest league table csv
    df_league = pd.read_csv('logs/FinalLeagueTable.csv')

    p1Wins, p2Wins = winners[0], winners[1]
    isP1Winner = isP1Loser = isP2Winner = isP2Loser = isDraw = False  
    isP1BW = isP2BW = isP1BL = isP2BL = False
    p1Score = p2Score = 0  # initialize scores
    
    if p1Wins > p2Wins:  # player 1 wins
        p1Score += 4
        isP1Winner = True
        isP2Loser = True
        if (p1Wins/gamesPerMatch >= 0.7):  # dominant winner
            p1Score += 1
            isP1BW = True
        elif (p1Wins/gamesPerMatch <= 0.55): # bonus losing point for other player
            p2Score += 1
            isP2BL = True
            
    elif p2Wins > p1Wins:  # player 2 wins
        p2Score += 4
        isP2Winner = True
        isP1Loser = True
        if (p2Wins/gamesPerMatch >= 0.7):  # dominant winner
            p2Score += 1
            isP2BW = True
        elif (p2Wins/gamesPerMatch <= 0.55): # bonus losing point for other player
            p1Score += 1
            isP1BL = True
            
    else: # draw
        p1Score += 2
        p2Score += 2
        isDraw = True
    
    avgScoreDifference = round(sum(results)/len(results), 3)
    
    # update table with these values
    p1Update = [player1.name, 1, p1Score, int(isP1BW), int(isP1BL), int(isP1Winner), int(isP1Loser), int(isDraw), round(avgScoreDifference,2)]
    p2Update = [player2.name, 1, p2Score, int(isP2BW), int(isP2BL), int(isP2Winner), int(isP2Loser), int(isDraw), -round(avgScoreDifference,2)]
    
    print(f'Points Earned - Player 1: {p1Score}    Player 2: {p2Score}')
    
    # update values for each player 
    for update in (p1Update, p2Update):
        updateValue = 1
        for column in df_league.columns:
            player = update[0]
            if column != "Pos" and column != "Player":
                df_league.loc[df_league['Player'] == player, column] += update[updateValue]
                updateValue += 1
                
    # sort league table by points, then PD, then wins
    df_league = df_league.sort_values(by=['Points', 'PD', 'W'], ascending=False)
    df_league['Pos'] = df_league['Pos'].sort_values().values
    # export the updated table
    df_league.to_csv('logs/FinalLeagueTable.csv', index=False)

#########################

if __name__ == "__main__":
    
    
    # run league
    RunLeague()

