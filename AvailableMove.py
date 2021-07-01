
class AvailableMove:
    """
    'AvailableMove' objects are used in the Carcassonne.availableMoves() 
    method to contain all the factors of a playable move into one object
    """
    
    def __init__(self, TileIndex, X, Y, Rotation, MeepleInfo = None):
    
        self.TileIndex = TileIndex
        self.X = X
        self.Y = Y
        self.Rotation = Rotation
        self.MeepleInfo = MeepleInfo
        self.move = (TileIndex, X, Y, Rotation, MeepleInfo)
        self.moveString = f'({TileIndex}, {X}, {Y}, {Rotation}, {MeepleInfo})'
        
    def __repr__(self):
        if self.MeepleInfo is not None:
            Location = self.MeepleInfo[0]
            LocationIndex = self.MeepleInfo[1]
            
            if Location == 'C':
                FullLocation = "City"
            elif Location == 'R':
                FullLocation = "Road"
            elif Location == "G":
                FullLocation = "Farm"
            else:
                FullLocation = "Monastery"
            
            MeepleString = ", Meeple Location: " + FullLocation + ", Location Index: " + str(LocationIndex)
            
        else:
            MeepleString = ""
        
        String = "TileIndex: " + str(self.TileIndex) + ", (X,Y): (" + str(self.X) + "," + str(self.Y) + "), Rotation: " + str(self.Rotation) + MeepleString
        return String
        