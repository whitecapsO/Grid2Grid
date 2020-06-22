from farmware_tools import app
from farmware_tools import device
from farmware_tools import env
from farmware_tools import get_config_value
import json
import os
import time

# TODO work out why it takes the Farmware librarys so long to load: 
# https://forum.farmbot.org/t/farmware-moveabsolute-and-executesequence-not-working/5784/28

# To do use a diamond pattern on the grid set alternateinbetween i.e. instead of an 11 x 8 grid 
# with alternateinbetween configure a 21 x 8 grid and then don't load every second value into the list
# otherwise if not alternateinbetween load all values into the list 
# Not tested turning alternate inbetween on both grids at the same time

# To work out Z axis height:
# 1. To work out the X axis angle use simple trig: angle = sin(angle) = opposite \ hypotenuse i.e. angle = sin-1 (opposite \ hypotenuse)
# 2. To work out Z axis height i.e the opposite: hypotenuse = current X pos - beginining of X then opposite = sin(angle) * hypotenuse
# 3. Then add that height (the opposite) to the startZGrid value

# To signal to the recursve sequence that the Grid2Grid has finished turn on Pin3

class GridPosition:
    def __init__(self, xPosition, yPosition, zPosition):
        self.xPosition = xPosition
        self.yPosition = yPosition
        self.zPosition = zPosition

numberOfPlants = get_config_value(farmware_name='Grid2Grid', config_name='numberOfPlants', value_type=int)
movesPerCycle = get_config_value(farmware_name='Grid2Grid', config_name='movesPerCycle', value_type=int)

xPositionsGrid1 = get_config_value(farmware_name='Grid2Grid', config_name='xPositionsGrid1', value_type=int)
yPositionsGrid1 = get_config_value(farmware_name='Grid2Grid', config_name='yPositionsGrid1', value_type=int)
spaceBetweenXGrid1 = get_config_value(farmware_name='Grid2Grid', config_name='spaceBetweenXGrid1', value_type=float)
spaceBetweenYGrid1 = get_config_value(farmware_name='Grid2Grid', config_name='spaceBetweenYGrid1', value_type=float)
startXGrid1 = get_config_value(farmware_name='Grid2Grid', config_name='startXGrid1', value_type=float)
startYGrid1 = get_config_value(farmware_name='Grid2Grid', config_name='startYGrid1', value_type=float)
startOfXSlopeGrid1 = get_config_value(farmware_name='Grid2Grid', config_name='startOfXSlopeGrid1', value_type=float)
sineOfXAngleGrid1 = get_config_value(farmware_name='Grid2Grid', config_name='sineOfXAngleGrid1', value_type=float)
alternateInBetweenGrid1 = get_config_value(farmware_name='Grid2Grid', config_name='alternateInBetweenGrid1', value_type=int)
sequenceAfter1stGridMove = get_config_value(farmware_name='Grid2Grid', config_name='sequenceAfter1stGridMove', value_type=str)

xPositionsGrid2 = get_config_value(farmware_name='Grid2Grid', config_name='xPositionsGrid2', value_type=int)
yPositionsGrid2 = get_config_value(farmware_name='Grid2Grid', config_name='yPositionsGrid2', value_type=int)
spaceBetweenXGrid2 = get_config_value(farmware_name='Grid2Grid', config_name='spaceBetweenXGrid2', value_type=float)
spaceBetweenYGrid2 = get_config_value(farmware_name='Grid2Grid', config_name='spaceBetweenYGrid2', value_type=float)
startXGrid2 = get_config_value(farmware_name='Grid2Grid', config_name='startXGrid2', value_type=float)
startYGrid2 = get_config_value(farmware_name='Grid2Grid', config_name='startYGrid2', value_type=float)
startOfXSlopeGrid2 = get_config_value(farmware_name='Grid2Grid', config_name='startOfXSlopeGrid1', value_type=float)
sineOfXAngleGrid2 = get_config_value(farmware_name='Grid2Grid', config_name='sineOfXAngleGrid2', value_type=float)
alternateInBetweenGrid2 = get_config_value(farmware_name='Grid2Grid', config_name='alternateInBetweenGrid2', value_type=int)
sequenceAfter2ndGridMove = get_config_value(farmware_name='Grid2Grid', config_name='sequenceAfter2ndGridMove', value_type=str)

# Delay constant as some calls to Farmduino are now not synchronous
waitSeconds = 30

# Set config file and environment variable names
configFileName = '/tmp/farmware/config.json'
evName = 'MovesMade'
configContents = ''

# Initialise row (X) and column (Y) indexes for all grids
grid1Coordinates = []
grid2Coordinates = []

# Initialise loop indexes, counts and flags
xIndex = 0
yIndex = 0
moveCount = 0
canMove = False
loopBreaked = False

addToZHeightGrid1 = 0
addToZHeightGrid2 = 0

# Get sequence IDs if name given
if sequenceAfter1stGridMove == "NULL" :
    sequenceAfter1stGridMoveId = 0
else :
    sequenceAfter1stGridMoveId = app.find_sequence_by_name(name=sequenceAfter1stGridMove)

if sequenceAfter2ndGridMove == "NULL" :
    sequenceAfter2ndGridMoveId = 0
else :
    sequenceAfter2ndGridMoveId = app.find_sequence_by_name(name=sequenceAfter2ndGridMove)

# Get the current position for x and y from the config
with open(configFileName, 'r') as f:
    configContents = json.load(f)
    f.close()
savedMoveIndex = int(configContents[evName])
device.log(message='savedMoveIndex: ' + str(savedMoveIndex), message_type='success')

# If we are at the start then canMove
if savedMoveIndex == 0 :    
    canMove = True

# Load Grid1 x,y,z coordinates into a list 
for yIndex in range(yPositionsGrid1):
    yPosGrid1 = startYGrid1 + (spaceBetweenYGrid1 * yIndex)
    for xIndex in range(xPositionsGrid1):
        xPosGrid1 = startXGrid1 + (spaceBetweenXGrid1 * xIndex)

        # Set the Z offset
        if (startOfXSlopeGrid1 != 0) and (sineOfXAngleGrid1 != 0) :
            hypotenuseGrid1 = xPosGrid1 - startOfXSlopeGrid1
            addToZHeightGrid1 = sineOfXAngleGrid1 * hypotenuseGrid1

        # If alternate inbetween and the modulus sum of indexes equals 0 add position
        if alternateInBetweenGrid1 == 1 and (((yIndex + xIndex) % 2) == 0):
            gridPosition1 = GridPosition(yPosGrid1, yPosGrid1, addToZHeightGrid1)
            grid1Coordinates.append(gridPosition1)

        # If not alternate inbetween add position
        elif alternateInBetweenGrid1 == 0:
            gridPosition1 = GridPosition(yPosGrid1, yPosGrid1, addToZHeightGrid1)
            grid1Coordinates.append(gridPosition1)

# Load Grid2 x,y,z coordinates into a list (exactly the same as Grid1)
for yIndex in range(yPositionsGrid2):
    yPosGrid2 = startYGrid2 + (spaceBetweenYGrid2 * yIndex)
    for xIndex in range(xPositionsGrid2):
        xPosGrid2 = startXGrid2 + (spaceBetweenXGrid2 * xIndex)

        if (startOfXSlopeGrid2 != 0) and (sineOfXAngleGrid2 != 0) :
            hypotenuseGrid2 = xPosGrid2 - startOfXSlopeGrid2
            addToZHeightGrid2 = sineOfXAngleGrid2 * hypotenuseGrid2

        if alternateInBetweenGrid2 == 1 and (((yIndex + xIndex) % 2) == 0):
            gridPosition2 = GridPosition(yPosGrid2, yPosGrid2, addToZHeightGrid2)
            grid2Coordinates.append(gridPosition2)

        elif alternateInBetweenGrid2 == 0:
            gridPosition2 = GridPosition(yPosGrid2, yPosGrid2, addToZHeightGrid2)
            grid2Coordinates.append(gridPosition2)

# Check the number of items in both lists are the same
device.log(message='grid1Coordinates: ' + str(len(grid1Coordinates)) + ' grid2Coordinates:' + str(len(grid2Coordinates)), message_type='success')           

# Now move 
for plant in range(numberOfPlants):
    if canMove :
        # Move Grid 1
        grid1Item = grid1Coordinates[plant]
        device.move_absolute(
            {
                'kind': 'coordinate',
                'args': {'x': grid1Item.xPosition, 'y': grid1Item.yPosition, 'z': grid1Item.zPosition}
            },
            100,
            {
                'kind': 'coordinate',
                'args': {'x': 0, 'y': 0, 'z': 0}
            }
        )
        if sequenceAfter1stGridMoveId > 0 :
            device.log(message='Execute sequence: ' + sequenceAfter1stGridMove, message_type='success')
            device.execute(sequenceAfter1stGridMoveId)
            time.sleep(waitSeconds)

        # Move Grid 2
        grid2Item = grid2Coordinates[plant]
        device.move_absolute(
            {
                'kind': 'coordinate',
                'args': {'x': grid2Item.xPosition, 'y': grid2Item.yPosition, 'z': grid2Item.zPosition}
            },
            100,
            {
                'kind': 'coordinate',
                'args': {'x': 0, 'y': 0, 'z': 0}
            }
        ) 
        if sequenceAfter2ndGridMoveId > 0 :
            device.log(message='Execute sequence: ' + sequenceAfter2ndGridMove, message_type='success')
            device.execute(sequenceAfter2ndGridMoveId) 
            time.sleep(waitSeconds)

        moveCount += 1 

    if movesPerCycle > 0 and movesPerCycle == moveCount:    # Turn the moves off and save the index
        canMove == False
        os.remove(configFileName)   # Write the current position of the 2nd grids x,y co-ordinates to the config
        configContents = {evName: str(xPosGrid2) + "," + str(yPosGrid2)}
        with open(configFileName, 'w') as f:
            json.dump(configContents, f)
            f.close()
        
        if plant < numberOfPlants : # If we aren't at the end of the loop then break out of the loop
            loopBreaked = True
            break

    elif canMove == False and savedMoveIndex == plant:  # Turn the moves on if we have reached the saved index
        canMove == True

# If loop finishes without breaking then signal that Grid2Grid has finished
if loopBreaked == False :
    device.write_pin(3,0,0)
    time.sleep(waitSeconds)