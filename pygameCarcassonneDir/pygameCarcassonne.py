# import local scripts
from Player import HumanPlayer, RandomPlayer
from MCTS_Player import MCTSPlayer
from MCTS_RAVE_Player import MCTS_RAVEPlayer
from MCTS_GP_Player import MCTS_GP_Player
from MCTS_ES_Player import MCTS_ES_Player
from Star1_Player import Star1
from Star2_5_Player import Star2_5

from Carcassonne import CarcassonneState
from Tile import Tile

from pygameCarcassonneDir.pygameNextTile import nextTile
from pygameCarcassonneDir.pygameFunctions import playMove, drawGrid, diplayGameBoard, printScores, printTilesLeft

from pygameCarcassonneDir.pygameSettings import BLACK, WHITE, GRID, GRID_SIZE, GRID_BORDER, MENU_WIDTH
from pygameCarcassonneDir.pygameSettings import MEEPLE_SIZE
from pygameCarcassonneDir.pygameSettings import displayScreen

# import packages
import sys



# Import and initialize the pygame library
import pygame

# Number Keys
NumKeys = [pygame.K_KP0, pygame.K_KP1, pygame.K_KP2, pygame.K_KP3, pygame.K_KP4, 
           pygame.K_KP5, pygame.K_KP6, pygame.K_KP7, pygame.K_KP8, pygame.K_KP9]

# main game loop
def main():
    """
    Main game logic
    """
    
    # globals
    global GAME_DISPLAY, CLOCK
    
    # initiate pygame
    pygame.init()
    
    # manage how fast the screen updates
    CLOCK = pygame.time.Clock()
    
    # pack all settings into one object
    DisplayScreen = displayScreen(GRID, GRID_SIZE, GRID_BORDER, MENU_WIDTH, MEEPLE_SIZE)
    #game display window
    GAME_DISPLAY = DisplayScreen.pygameDisplay 
    pygame.display.set_caption('Carcassonne')  # windown name
    
    # background image
    background = pygame.image.load('pygame_images/table.jpg')
    background = pygame.transform.scale(background, (DisplayScreen.Window_Width, DisplayScreen.Window_Height))
    # add game title
    title = pygame.image.load('pygame_images/game_title.png')
    title = pygame.transform.scale(title, (274, 70))
    background.blit(title, (40, 7))
    
    
    ##########################
    #  ADD NEW PLAYERS HERE  #
    ##########################
    
    PLAYER_DICT = {
        "Human": HumanPlayer(),
        #"Random": RandomPlayer(),
        #"MCTS": MCTSPlayer(timeLimit=8),
        "MCTS_GP":MCTS_ES_Player(),
        #"RAVE": MCTS_RAVEPlayer(),
        #"Star1": Star1(),
        #"Star2.5": Star2_5(),
        }
    
    
    # custom choices
    if len(sys.argv) > 1:
        if len(sys.argv) != 3:
            print("ERROR - Please Provide Two Arguments OR No Arguments")
            return
        else:
            p1 = PLAYER_DICT.get(sys.argv[1])
            p2 = PLAYER_DICT.get(sys.argv[2])
            if (not p1):
                print(f'{sys.argv[1]} is not a playable option')
                return
            else:
                print(f'Player 1: {p1.name}')
                
            if (not p2):
                print(f'{sys.argv[2]} is not a playable option')
                return
            else:
                print(f'Player 2: {p2.name}')
                
    
    # default options
    else:
        
        p1 = PLAYER_DICT.get("Human")
        p2 = PLAYER_DICT.get("MCTS_GP")
        #p1 = PLAYER_DICT.get("Random")
        #p2 = PLAYER_DICT.get("Random")
        
    
    # initiate game state  
    Carcassonne = CarcassonneState(p1,p2)

    # initialize the 'next tile' onject
    NT = nextTile(Carcassonne, DisplayScreen)
    
    # stay constant
    done = False  # loop until the user clicks the close button.
    player = Carcassonne.p1  # player 1 starts
    isGameOver = False
    # isStartOfTurn - indicates whether it is the first tick of the next player's turn
    # hasSomethingNew - indicates an action has just happened
    isStartOfGame = isStartOfTurn = hasSomethingNew = True
    selectedMove = [16, 0, 0, 0, None] # first move of game
    
    # default settings
    rotation = 0
    newRotation = False
    numberSelected = 0  # default choice is no meeple
    
    # main pygame loop
    while not done:
        
        # main event loop
        for event in pygame.event.get():
            
            # QUIT game
            if event.type == pygame.QUIT:
                pygame.quit()
                
            # show next tile in top right
            if not isGameOver:
                
                # check if player is 'AI' or is a 'Humnan' 
                # different game loops and allowable commands for each player
                if player.isAIPlayer:
                    
                    # if a keyboard button is pressed
                    if event.type == pygame.KEYDOWN:
                    
                        # play AI move when space bar is clicked
                        if event.key == pygame.K_SPACE:
                            player, selectedMove = playMove(NT, player, Carcassonne, NT.nextTileIndex, isStartOfGame, ManualMove = None)
                            NT = nextTile(Carcassonne, DisplayScreen)  # next tile
                            print(f'Scores: {Carcassonne.FeatureScores}')
                            isStartOfTurn = True  # new turn
                            hasSomethingNew = True  # action just happened
                            isStartOfGame = False # if move is made, the game has now started
                        
                    # check if game is over
                    isGameOver = Carcassonne.isGameOver
                        
                # human player loop
                else:
                    
                    # if a keyboard button is pressed
                    if event.type == pygame.KEYDOWN:
                        
                        # tile rotations
                        if event.key == pygame.K_LEFT:
                            rotation = -1
                            newRotation = True
                        elif event.key == pygame.K_RIGHT:
                            rotation = 1
                            newRotation = True
                        
                        # number selection - for Meeple selection
                        if event.key in NumKeys:
                            numberStr = pygame.key.name(event.key)[1]
                            numberSelected = int(numberStr)  # selection of meeple location
                            if numberSelected == 0:
                                NT.Meeple = None
                            hasSomethingNew = True  # action just happened
                    
                    # is mouse is clicked
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        # get position of click
                        X, Y = NT.evaluate_click(pygame.mouse.get_pos(), DisplayScreen)
                        
                        # check is selection is valid
                        if (X, Y) in NT.possibleCoordsMeeples:
                            rotation = (90*NT.Rotated)  # rotation
                            ManualMove = (NT.nextTileIndex, X, Y, rotation, NT.Meeple)
                            player, selectedMove = playMove(NT, player, Carcassonne, NT.nextTileIndex, isStartOfGame, ManualMove)
                            NT = nextTile(Carcassonne, DisplayScreen)
                            print(f'Scores: {Carcassonne.FeatureScores}')
                            isStartOfTurn = True  # new turn
                            hasSomethingNew = True
                            isStartOfGame = False
                        elif (X,Y) in list(NT.Carcassonne.Board.keys()):
                            print("check")
                            text = NT.displayTextClickedTile(X,Y)
                            print(text)
                        else:
                            print(f'X: {X}')
                            print(f'Y: {Y}')
                            print("invalid")
                        
                # check if game is over
                isGameOver = Carcassonne.isGameOver
                
                if isGameOver:
                    isStartOfTurn = False
                    hasSomethingNew = False
                     
            # if game is over
            else:
                # print winner
                print(f'Winner: Player {Carcassonne.winner}, Scores:  P1: {Carcassonne.Scores[0]} - P2: {Carcassonne.Scores[1]}')
                pygame.quit()
    
                    
        # display game screen
        GAME_DISPLAY.blit(background, (0, 0))  # wooden table background
        drawGrid(DisplayScreen)  # draw grid
        
        
        if hasSomethingNew:
            # meeple locations
            if player.name == "Human":
                # keep track of index
                    NT.resetImage()
                    i = 1
                    for location_key in NT.Tile.AvailableMeepleLocs:
                        location_value = NT.Tile.AvailableMeepleLocs[location_key]
                        NT.addMeepleLocations(location_key, location_value, i, numberSelected, NT.nextTileIndex)
                        NT.updateMeepleMenu(location_key, location_value, i, numberSelected)
                        i += 1
                    NT.rotate(NT.Rotated, newRotation)
            # instruction to press 'Space'   
            else:
                if not isGameOver:
                    NT.pressSpaceInstruction()
            
        
        if isStartOfTurn:
            # last play
            NT.updateMoveLabel(Carcassonne, selectedMove, isStartOfGame)
        
        # print scores
        printScores(Carcassonne, DisplayScreen)
        #displayTilesLeft
        printTilesLeft(Carcassonne, DisplayScreen)
        
        # show next tile in top right
        if not isGameOver:
            # show tile in top corner
            NT.showNextTile(DisplayScreen, rotation, newRotation)
            #print meeple info
            NT.showInfos(DisplayScreen)
            # possible moves
            NT.highlightPossibleMoves(DisplayScreen)
            
        # only one rotation per click
        newRotation = False
        numberSelected = 0
        
        # show all tiles in the board
        diplayGameBoard(Carcassonne, DisplayScreen)
        
        # update game screen
        pygame.display.flip()
        
        # first tick is over
        isStartOfTurn = False
        hasSomethingNew = False
        
        # FPS
        CLOCK.tick(8)
            
if __name__ == "__main__":
    main()
    
    

    
