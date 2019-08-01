from farmware_tools import app
from farmware_tools import device
from farmware_tools import env
from farmware_tools import get_config_value

# 1. Pick up tool
# 2. Move to first position first grid
# 3. Perform tool action (sequenceAfter1stGridMove)
# 4. Move to first position second grid
# 5. Perform tool action (sequenceAfter2ndGridMove)
# 6. Move to second position first grid
# 7. Repeat

#todo implement alternateInBetween calculations for x position

# Values for testing
# *** First grid ***
# rowsGrid1 = 4
# colsGrid1 = 7 
# spaceBetweenRowsGrid1 = 47
# spaceBetweenColsGrid1 = 45 
# startXGrid1 = 310.2
# startYGrid1 = 563.8
# startZGrid1 = 210.96
# sequenceAfter1stGridMove = '' 
# alternateInBetweenGrid1 = false
# 
# rowsGrid2 = 4
# colsGrid2 = 7
# spaceBetweenRowsGrid2 = 140
# spaceBetweenColsGrid2 = 200 
# startXGrid2 = 
# startYGrid2 = 
# startZGrid2 = 
# sequenceAfter2ndGridMove = '' 
# alternateInBetweenGrid2 = false


device.log(message='Setting first grid variables', message_type='success')
rowsGrid1 = get_config_value(farmware_name='Grid2Grid', config_name='rowsGrid1', value_type=int)
colsGrid1 = get_config_value(farmware_name='Grid2Grid', config_name='colsGrid1', value_type=int)
spaceBetweenRowsGrid1 = get_config_value(farmware_name='Grid2Grid', config_name='spaceBetweenRowsGrid1', value_type=float)
spaceBetweenColsGrid1 = get_config_value(farmware_name='Grid2Grid', config_name='spaceBetweenColsGrid1', value_type=float)
startXGrid1 = get_config_value(farmware_name='Grid2Grid', config_name='startXGrid1', value_type=float)
startYGrid1 = get_config_value(farmware_name='Grid2Grid', config_name='startYGrid1', value_type=float)
startZGrid1 = get_config_value(farmware_name='Grid2Grid', config_name='startZGrid1', value_type=float)
sequenceAfter1stGridMove = get_config_value(farmware_name='Grid2Grid', config_name='sequenceAfter1stGridMove', value_type=str)
alternateInBetweenGrid1 = get_config_value(farmware_name='Grid2Grid', config_name='alternateInBetweenGrid1', value_type=bool)

device.log(message='Setting second grid variables', message_type='success')
rowsGrid2 = get_config_value(farmware_name='Grid2Grid', config_name='rowsGrid2', value_type=int)
colsGrid2 = get_config_value(farmware_name='Grid2Grid', config_name='colsGrid2', value_type=int)
spaceBetweenRowsGrid2 = get_config_value(farmware_name='Grid2Grid', config_name='spaceBetweenRowsGrid2', value_type=float)
spaceBetweenColsGrid2 = get_config_value(farmware_name='Grid2Grid', config_name='spaceBetweenColsGrid2', value_type=float)
startXGrid2 = get_config_value(farmware_name='Grid2Grid', config_name='startXGrid2', value_type=float)
startYGrid2 = get_config_value(farmware_name='Grid2Grid', config_name='startYGrid2', value_type=float)
startZGrid2 = get_config_value(farmware_name='Grid2Grid', config_name='startZGrid2', value_type=float)
sequenceAfter2ndGridMove = get_config_value(farmware_name='Grid2Grid', config_name='sequenceAfter2ndGridMove', value_type=str)
alternateInBetweenGrid2 = get_config_value(farmware_name='Grid2Grid', config_name='alternateInBetweenGrid2', value_type=bool)

device.log(message='Setting variables', message_type='success')
device.log(message='Change 5', message_type='success')

# Initialise row (X) and column (Y) indexes for the second grid
rowGrid2Index = 0
colGrid2Index = 0
# Set constant Z positions
zPosGrid1 = startZGrid1
zPosGrid2 = startZGrid2


device.log(message='Setting sequenceId variables', message_type='success')
if sequenceAfter1stGridMove != "":
    sequenceAfter1stGridMoveId = app.find_sequence_by_name(name=sequenceAfter1stGridMove)
else :
    sequenceAfter1stGridMoveId = 0

if sequenceAfter2ndGridMove != "":
    sequenceAfter2ndGridMoveId = app.find_sequence_by_name(name=sequenceAfter2ndGridMove)
else :
    sequenceAfter2ndGridMoveId = 0


device.log(message='Starting first grid row loop', message_type='success')

# Start the first grid movement
for r in range(rowsGrid1):
    
    # Initialise or increment x position of both grids
    xPosGrid1 = startXGrid1 + (spaceBetweenRowsGrid1 * r)

    # Set both first grids y position back to the begining of the row
    yPosGrid1 = startYGrid1

    device.log(message='Set positions', message_type='success')

    # Todo fix as rows and column totals will be different numbers in both grids
    for c in range(colsGrid1):
        # 1st grid move moveAbsolute(xPos, yPos, startZ)
        device.log('rowXGrid1Index: ' + str(r), 'success', ['toast'])
        device.log('colXGrid1Index: ' + str(c), 'success', ['toast'])
        device.log('Moving to ' + str(xPosGrid1) + ', ' + str(yPosGrid1) + ', ' + str(zPosGrid1), 'success', ['toast'])
        device.move_absolute(
            {
                'kind': 'coordinate',
                'args': {'x': xPosGrid1, 'y': yPosGrid1, 'z': zPosGrid1}
            },
            100,
            {
                'kind': 'coordinate',
                'args': {'x': 0, 'y': 0, 'z': 0}
            }
        )

        # Run sequence after 1st grid move
        if sequenceAfter1stGridMove != "":
            device.log(message='Execute sequence: ' + sequenceAfter1stGridMove, message_type='success')
            device.execute(sequenceAfter1stGridMoveId)

        # Set the x and y positions on the second grid
        xPosGrid2 = startXGrid2 + (spaceBetweenRowsGrid2 * rowGrid2Index)
        yPosGrid2 = startYGrid2 + (spaceBetweenColsGrid2 * colGrid2Index)

        # 2nd grid move
        device.log('rowGrid2Index: ' + str(rowGrid2Index), 'success', ['toast'])
        device.log('colGrid2Index: ' + str(colGrid2Index), 'success', ['toast'])
        device.log('Moving to ' + str(xPosGrid2) + ', ' + str(yPosGrid2) + ', ' + str(zPosGrid2), 'success', ['toast'])
        device.move_absolute(
            {
                'kind': 'coordinate',
                'args': {'x': xPosGrid2, 'y': yPosGrid2, 'z': zPosGrid2}
            },
            100,
            {
                'kind': 'coordinate',
                'args': {'x': 0, 'y': 0, 'z': 0}
            }
        )

        # Run sequence after 2nd grid move
        if sequenceAfter2ndGridMove != "":
            device.log(message='Execute sequence: ' + sequenceAfter2ndGridMove, message_type='success')
            device.execute(sequenceAfter2ndGridMoveId)

        # Increment y position for grid 1
        yPosGrid1 = yPosGrid1 + spaceBetweenColsGrid1

        # # Increment the indexes for grid 2
        if colGrid2Index < colsGrid2 :
            colGrid2Index += 1
        else :
            colGrid2Index = 0
            rowGrid2Index += 1