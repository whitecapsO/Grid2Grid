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

#TODO if you miss the last movement on one axis because of alternateinbetween you are still in the same loop and their will
# be a move on the other axis. You need to change alternate inbetween to jump a movement rather than just missing it out so reset the 
# x axis indexes when doing that

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
alternateInBetweenGrid1 = get_config_value(farmware_name='Grid2Grid', config_name='alternateInBetweenGrid1', value_type=int)

device.log(message='Setting second grid variables', message_type='success')
rowsGrid2 = get_config_value(farmware_name='Grid2Grid', config_name='rowsGrid2', value_type=int)
colsGrid2 = get_config_value(farmware_name='Grid2Grid', config_name='colsGrid2', value_type=int)
spaceBetweenRowsGrid2 = get_config_value(farmware_name='Grid2Grid', config_name='spaceBetweenRowsGrid2', value_type=float)
spaceBetweenColsGrid2 = get_config_value(farmware_name='Grid2Grid', config_name='spaceBetweenColsGrid2', value_type=float)
startXGrid2 = get_config_value(farmware_name='Grid2Grid', config_name='startXGrid2', value_type=float)
startYGrid2 = get_config_value(farmware_name='Grid2Grid', config_name='startYGrid2', value_type=float)
startZGrid2 = get_config_value(farmware_name='Grid2Grid', config_name='startZGrid2', value_type=float)
sequenceAfter2ndGridMove = get_config_value(farmware_name='Grid2Grid', config_name='sequenceAfter2ndGridMove', value_type=str)
alternateInBetweenGrid2 = get_config_value(farmware_name='Grid2Grid', config_name='alternateInBetweenGrid2', value_type=int)

device.log(message='Starting Grid2Grid', message_type='success')

# Initialise row (X) and column (Y) indexes for the second grid
rowGrid2Index = 0
colGrid2Index = 0

# Set constant Z positions
zPosGrid1 = startZGrid1
zPosGrid2 = startZGrid2

# Get sequence IDs if name given
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
for rowGrid1Index in range(rowsGrid1):
    # Set first grids y position back to the first column
    yPosGrid1 = startYGrid1

    for colGrid1Index in range(colsGrid1):
        # Initialise or increment x position of first grid if alternateInBetween assume the first 
        # column is not an alternateInBetween
        if alternateInBetweenGrid1 == 1 :
            if colGrid1Index > 0 and (colGrid1Index % 2) > 0 :
                device.log(message='Grid 1 alternateInBetween', message_type='success')
                xPosGrid1 = startXGrid1 + (spaceBetweenRowsGrid1 * 0.5) + (spaceBetweenRowsGrid1 * rowGrid1Index)
            else :
                xPosGrid1 = startXGrid1 + (spaceBetweenRowsGrid1 * rowGrid1Index)
        else :
            xPosGrid1 = startXGrid1 + (spaceBetweenRowsGrid1 * rowGrid1Index)


        # 1st grid move if not alternateInBetweenGrid1 and on last row
        if (alternateInBetweenGrid1 == 0 or (alternateInBetweenGrid1 == 1 and rowGrid1Index < rowsGrid1 - 1)) : 
            device.log('Grid 1 moving to ' + str(xPosGrid1) + ', ' + str(yPosGrid1) + ', ' + str(zPosGrid1), 'success', ['toast'])
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
        else :
            device.log(message='Grid 1 alternateInBetween so abort last position', message_type='success')

        # Run sequence after 1st grid move
        if sequenceAfter1stGridMove != "":
            device.log(message='Execute sequence: ' + sequenceAfter1stGridMove, message_type='success')
            device.execute(sequenceAfter1stGridMoveId)

        # Increment the row index and reset the column index if alternateInBetweenGrid2 and in an
        # alternateInBetweenGrid2 row i.e. row index is an odd number and 
        # or if we reached the last column 

        # if ((alternateInBetweenGrid2 == 1) 
        # and (colGrid2Index > 0 and (colGrid2Index % 2) > 0) 
        # and (rowGrid1Index < rowsGrid1 - 1))
        # or (colGrid2Index >= colsGrid2) :
        #     rowGrid2Index +
        #     colGrid2Index = 0

        # Set the x and y positions on the second grid if alternateInBetween assume the first 
        # column is not an alternateInBetween
        if alternateInBetweenGrid2 == 1 :
            if colGrid2Index > 0 and (colGrid2Index % 2) > 0 :
                if rowGrid1Index < rowsGrid1 - 1 :
                    device.log(message='Grid 2 last row of alternateInBetween column', message_type='success')
                else :
                    device.log(message='Grid 2 alternateInBetween column', message_type='success')
                    xPosGrid2 = startXGrid2 + (spaceBetweenRowsGrid2 * 0.5) + (spaceBetweenRowsGrid2 * rowGrid2Index)
            else :
                xPosGrid2 = startXGrid2 + (spaceBetweenRowsGrid2 * rowGrid2Index)
        else :
            xPosGrid2 = startXGrid2 + (spaceBetweenRowsGrid2 * rowGrid2Index)
        
        yPosGrid2 = startYGrid2 + (spaceBetweenColsGrid2 * colGrid2Index)

        # 1st grid move if not alternateInBetweenGrid1 and on last row
        if (alternateInBetweenGrid2 == 0 or (alternateInBetweenGrid2 == 1 and rowGrid2Index < rowsGrid2 - 1)) : 
            device.log('Grid 2 moving to ' + str(xPosGrid2) + ', ' + str(yPosGrid2) + ', ' + str(zPosGrid2), 'success', ['toast'])
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
        else :
            device.log(message='Grid 2 alternateInBetween so abort last position', message_type='success')

        # Run sequence after 2nd grid move
        if sequenceAfter2ndGridMove != "":
            device.log(message='Execute sequence: ' + sequenceAfter2ndGridMove, message_type='success')
            device.execute(sequenceAfter2ndGridMoveId)

        # Increment y column position for grid 1
        yPosGrid1 = yPosGrid1 + spaceBetweenColsGrid1

        if rowGrid2Index >= (rowsGrid2 - 1) :
            rowGrid2Index = 0
            colGrid2Index += 1
        else :
            rowGrid2Index += 1
        
