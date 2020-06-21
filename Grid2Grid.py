from farmware_tools import app
from farmware_tools import device
from farmware_tools import env
from farmware_tools import get_config_value
import json
import os
import time

# TODO add extra row for alternate Inbetween and do a diamond patten
# i.e. instead of an 11 x 8 grid with alternateinbetween configure a 21 x 8 grid with alternate inbetween and then don't load every second value into the list
# otherwise load all values into the list simple

# Rewrite of Grid2Grid to run in 20 minutes due to limitations put on Farmware 
# i.e. Farmware can only run for 20 minutes and there is a 2 second delay between device calls
# the only way to loop is to use sequence recursion at the end of each row 
# the movesPerCycle specifies how many grid2grid moves can be made in 20 minutes before 
# breaking out of the loop anfd writing that position to a config file
# the sequence then recalls Grid2Grid and starts moving from whare it left off

# TODO work out why it takes the Farmware librarys so long to load: 
# https://forum.farmbot.org/t/farmware-moveabsolute-and-executesequence-not-working/5784/28

# To work out Z axis height:
# 1. To work out the X axis angle use simple trig: angle = sin(angle) = opposite \ hypotenuse i.e. angle = sin-1 (opposite \ hypotenuse)
# 2. To work out Z axis height i.e the opposite: hypotenuse = current X pos - beginining of X then opposite = sin(angle) * hypotenuse
# 3. Then add that height (the opposite) to the startZGrid value

# Remember if using alternate inbetween last row is missed so:
# Normal grid: 3 rows x 2 columns = 6 cells
# Alternate in between grid: 2 rows x 4 columns = 6 cells as last rows 2 of alternate inbetween columns missed
# Not tested turning alternate inbetween on both grids at the same time
# A better way would be to initialise 2 arrays with x,y coordinates and loop through them but this algo works

# Future considerations:
# Load two arrays of coordinates first and then loop through them note one grid could be diamond pattern one could be normal grid
# Think if using alternate inbetween then instead of x count = 11, x count = the number of actual x positions i.e. x count = 21 
# then on any column tell it when to use the odd or even numbered x positions

#try :
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
evName = 'xyCoordinates'
configContents = ''

# Initialise row (X) and column (Y) indexes for all grids
grid1Coordinates = []
grid2Coordinates = []
xIndex = 0
yIndex = 0
moveCount = 0
canMove = False
loopBreaked = False

addToZHeightGrid1 = 0
addToZHeightGrid2 = 0

# Initialise positions
xPosGrid1 = startXGrid1
yPosGrid1 = startYGrid1
xPosGrid2 = startXGrid2
yPosGrid2 = startYGrid2

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

# Parse the data into variables
currentPositionXstr = str(configContents[evName]).split(",",-1)[0]
currentPositionX = int(currentPositionXstr.split('.')[0])
currentPositionYstr = str(configContents[evName]).split(",",-1)[1]
currentPositionY = int(currentPositionYstr.split('.')[0])

device.log(message='currentPositionXstr: ' + currentPositionXstr + ' currentPositionYstr:' + currentPositionYstr, message_type='success')

# Set the canMove and hasMoved flags
canMove = False

# Load Grid1 Values and set y and x
for yIndex in range(yPositionsGrid1):
    yPosGrid1 = startYGrid1 + (spaceBetweenYGrid1 * yIndex)
    for xIndex in range(xPositionsGrid1):
        xPosGrid1 = startXGrid1 + (spaceBetweenXGrid1 * xIndex)

        # Set the Z offset
        if (startOfXSlopeGrid1 != 0) and (sineOfXAngleGrid1 != 0) :
            hypotenuseGrid1 = xPosGrid1 - startOfXSlopeGrid1
            addToZHeightGrid1 = sineOfXAngleGrid1 * hypotenuseGrid1

        # If alternate inbetween and the sum of indexes adds to an even value or 0 add position
        if alternateInBetweenGrid1 == 1 and (((yIndex + xIndex) % 2) >= 0):
            gridPosition1 = GridPosition(yPosGrid1, yPosGrid1, addToZHeightGrid1)
            grid1Coordinates.append(gridPosition1)

        # If not alternate inbetween add position
        elif alternateInBetweenGrid1 == 0:
            gridPosition1 = GridPosition(yPosGrid1, yPosGrid1, addToZHeightGrid1)
            grid1Coordinates.append(gridPosition1)

# Load Grid2 Values and set y and x
for yIndex in range(yPositionsGrid2):
    yPosGrid2 = startYGrid2 + (spaceBetweenYGrid2 * yIndex)
    for xIndex in range(xPositionsGrid2):
        xPosGrid2 = startXGrid2 + (spaceBetweenXGrid2 * xIndex)

         # Set the Z offset
        if (startOfXSlopeGrid2 != 0) and (sineOfXAngleGrid2 != 0) :
            hypotenuseGrid2 = xPosGrid2 - startOfXSlopeGrid2
            addToZHeightGrid2 = sineOfXAngleGrid2 * hypotenuseGrid2

        # If alternate inbetween and the sum of indexes adds to an even value or 0 add position
        if alternateInBetweenGrid2 == 1 and (((yIndex + xIndex) % 2) >= 0):
            gridPosition2 = GridPosition(yPosGrid2, yPosGrid2, addToZHeightGrid2)
            grid2Coordinates.append(gridPosition2)

        # If not alternate inbetween add position
        elif alternateInBetweenGrid2 == 0:
            gridPosition2 = GridPosition(yPosGrid2, yPosGrid2, addToZHeightGrid2)
            grid2Coordinates.append(gridPosition2)

device.log(message='grid1Coordinates: ' + str(len(grid1Coordinates)) + ' grid2Coordinates:' + str(len(grid2Coordinates)), message_type='success')           

# Now move
for plant in range(numberOfPlants):

    # Move Grid 1
    grid1Item = GridPosition(grid1Coordinates[plant])
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
    grid2Item = GridPosition(grid2Coordinates[plant])
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

# Remove
# if currentPositionX == 0 and currentPositionY == 0:
#     canMove = True

# for yIndex in range(yAxisCount):
#     # Set Y coordinates
#     yPosGrid1 = startYGrid1 + (spaceBetweenYGrid1 * yIndex)
#     yPosGrid2 = startYGrid2 + (spaceBetweenYGrid2 * yIndex)

#     for xIndex in range(xAxisCount):
#         # Grid 1
#         # Set X coordinates
#         if alternateInBetweenGrid1 == 1 :
#             if yIndex > 0 and (yIndex % 2) > 0 :
#                 xPosGrid1 = startXGrid1 + (spaceBetweenXGrid1 * 0.5) + (spaceBetweenXGrid1 * xIndex)
#             else :
#                 xPosGrid1 = startXGrid1 + (spaceBetweenXGrid1 * xIndex)
#         else :
#             xPosGrid1 = startXGrid1 + (spaceBetweenXGrid1 * xIndex)
        
#         if ((alternateInBetweenGrid1 == 1)              # If we can move and not set to alternateInBetween 
#         and (yIndex > 0 and (yIndex % 2) > 0)           # on an alternateInBetween odd numbered (offset) y value  
#         and (xIndex >= xAxisCount - 1)) :               # on the last x position as an alternateInBetween which has 1 less x position
#             yPosGrid1 = yPosGrid1 + spaceBetweenYGrid1  # Bump up the Y position to the next row
#             xPosGrid1 = startXGrid1                     # Set the X position back to the start of a non alternateInBetween
#             device.log(message='alternateInBetweenGrid1 last row', message_type='success')

#         if (startOfXSlopeGrid1 != 0) and (sineOfXAngleGrid1 != 0) :
#             hypotenuseGrid1 = xPosGrid1 - startOfXSlopeGrid1
#             addToZHeightGrid1 = sineOfXAngleGrid1 * hypotenuseGrid1

#         if canMove :
#             device.move_absolute(
#                 {
#                     'kind': 'coordinate',
#                     'args': {'x': xPosGrid1, 'y': yPosGrid1, 'z': addToZHeightGrid1}
#                 },
#                 100,
#                 {
#                     'kind': 'coordinate',
#                     'args': {'x': 0, 'y': 0, 'z': 0}
#                 }
#             )
#             if sequenceAfter1stGridMoveId > 0 :
#                 device.log(message='Execute sequence: ' + sequenceAfter1stGridMove, message_type='success')
#                 device.execute(sequenceAfter1stGridMoveId)
#                 time.sleep(waitSeconds)

#         # Grid 2
#         if alternateInBetweenGrid2 == 1 :
#             if yIndex > 0 and (yIndex % 2) > 0 :
#                 xPosGrid2 = startXGrid2 + (spaceBetweenXGrid2 * 0.5) + (spaceBetweenXGrid2 * xIndex)
#             else :
#                 xPosGrid2 = startXGrid2 + (spaceBetweenXGrid2 * xIndex)
#         else :
#             xPosGrid2 = startXGrid2 + (spaceBetweenXGrid2 * xIndex)

#         if((alternateInBetweenGrid2 == 1)               # If we can move and not set to alternateInBetween 
#         and (yIndex > 0 and (yIndex % 2) > 0)           # on an alternateInBetween odd numbered (offset) y value  
#         and (xIndex >= xAxisCount - 1)) :               # on the last position as an alternateInBetween which has 1 less x position
#             yPosGrid2 = yPosGrid2 + spaceBetweenYGrid2  # Bump up the Y position to the next row
#             xPosGrid2 = startXGrid2                     # Set the X position back to the start of a non alternateInBetween
#             device.log(message='alternateInBetweenGrid2 last row', message_type='success')

#         if (startOfXSlopeGrid2 != 0) and (sineOfXAngleGrid2 != 0) :
#             hypotenuseGrid2 = xPosGrid2 - startOfXSlopeGrid2
#             addToZHeightGrid2 = sineOfXAngleGrid2 * hypotenuseGrid2

#         if canMove :
#             device.move_absolute(
#                 {
#                     'kind': 'coordinate',
#                     'args': {'x': xPosGrid2, 'y': yPosGrid2, 'z': addToZHeightGrid2}
#                 },
#                 100,
#                 {
#                     'kind': 'coordinate',
#                     'args': {'x': 0, 'y': 0, 'z': 0}
#                 }
#             ) 
#             if sequenceAfter2ndGridMoveId > 0 :
#                 device.log(message='Execute sequence: ' + sequenceAfter2ndGridMove, message_type='success')
#                 device.execute(sequenceAfter2ndGridMoveId) 
#                 time.sleep(waitSeconds)

#             moveCount += 1 # **** check this works with alternate inbetween and you don't end up loosing a or gaining an extra move

#         if ((xPosGrid2 - 5) <= currentPositionX <= (xPosGrid2 + 5)) and ((yPosGrid2 - 5) <= currentPositionY <= (yPosGrid2 + 5)) :
#             canMove = True

#         if moveCount >= movesPerCycle :
#             loopBreaked = True
#             break

#     if moveCount >= movesPerCycle :
#         loopBreaked = True
#         break

# os.remove(configFileName)                                           # Write the current position of the 2nd grids x,y co-ordinates to the config
# configContents = {evName: str(xPosGrid2) + "," + str(yPosGrid2)}
# with open(configFileName, 'w') as f:
#     json.dump(configContents, f)
#     f.close()

# if loopBreaked == False :
#     device.write_pin(3,0,0)
#     time.sleep(waitSeconds)