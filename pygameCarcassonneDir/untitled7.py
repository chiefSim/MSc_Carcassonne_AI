from Tile import Tile

t=Tile(4)


i=1
for location_key in t.AvailableMeepleLocs:
    print(i)
    i+=1
    print(location_key)
    