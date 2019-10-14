from farmware_tools import app
from farmware_tools import device
from farmware_tools import env
from farmware_tools import get_config_value

# Remember if using alternate inbetween last row is missed so:
# Normal grid: 3 rows x 2 columns = 6 cells
# Alternate in between grid: 2 rows x 4 columns = 6 cells as last rows 2 of alternate inbetween columns missed
# Not tested turning alternate inbetween on both grids at the same time
# A better way would be to initialise 2 arrays with x,y coordinates and loop through them but this algo works

# 1. Pick up tool
# 2. Move to first position first grid
# 3. Perform tool action (sequenceAfter1stGridMove)
# 4. Move to first position second grid
# 5. Perform tool action (sequenceAfter2ndGridMove)
# 6. Move to second position first grid
# 7. Repeat

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
startLastRowOfGrid1 = get_config_value(farmware_name='Grid2Grid', config_name='startLastRowOfGrid1', value_type=int)

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
        # Set the x and y positions on the first grid if alternateInBetween assume the first 
        # column is not an alternateInBetween then odd numbered colums are
        # if startLastRowOfGrid1 then the x position starts on the last row and moves backwards
        if alternateInBetweenGrid1 == 1 :
            if colGrid1Index > 0 and (colGrid1Index % 2) > 0 :
                device.log(message='Grid 1 alternateInBetween', message_type='success')
                if startLastRowOfGrid1 == 1 :
                    xPosGrid1 = startXGrid1 - (spaceBetweenRowsGrid1 * 0.5) - (spaceBetweenRowsGrid1 * rowGrid1Index)
                else
                    xPosGrid1 = startXGrid1 + (spaceBetweenRowsGrid1 * 0.5) + (spaceBetweenRowsGrid1 * rowGrid1Index)
            else :
                if startLastRowOfGrid1 == 1 :
                    xPosGrid1 = startXGrid1 - (spaceBetweenRowsGrid1 * rowGrid1Index)
                else
                    xPosGrid1 = startXGrid1 + (spaceBetweenRowsGrid1 * rowGrid1Index)
        else :
            if startLastRowOfGrid1 == 1 :
                xPosGrid1 = startXGrid1 - (spaceBetweenRowsGrid1 * rowGrid1Index)                    
            else
                xPosGrid1 = startXGrid1 + (spaceBetweenRowsGrid1 * rowGrid1Index)

        # 1st grid move set the first grid row index back to zero if alternate inbetween column on last row let the loop handle the rest
        if ((alternateInBetweenGrid1 == 1)                  # Is alternateInBetween
        and (colGrid1Index > 0 and (colGrid1Index % 2) > 0) # is on an alternateInBetween odd numbered (offset) column  
        and (rowGrid1Index >= rowsGrid1 - 1)) :             # is on the second to last row index as an alternateInBetween has 1 less row
            # Increment y column position for grid 1
            yPosGrid1 = yPosGrid1 + spaceBetweenColsGrid1
            device.log(message='Grid 1 alternateInBetween column last row so miss a row', message_type='success')
        else :
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

            # Run sequence after 1st grid move
            if sequenceAfter1stGridMove != "":
                device.log(message='Execute sequence: ' + sequenceAfter1stGridMove, message_type='success')
                device.execute(sequenceAfter1stGridMoveId)

            # Set the x and y positions on the second grid if alternateInBetween assume the first 
            # column is not an alternateInBetween then odd numbered colums are
            if alternateInBetweenGrid2 == 1 :
                if colGrid2Index > 0 and (colGrid2Index % 2) > 0 :
                    device.log(message='Grid 2 alternateInBetween column', message_type='success')
                    xPosGrid2 = startXGrid2 + (spaceBetweenRowsGrid2 * 0.5) + (spaceBetweenRowsGrid2 * rowGrid2Index)
                else :
                    xPosGrid2 = startXGrid2 + (spaceBetweenRowsGrid2 * rowGrid2Index)
            else :
                xPosGrid2 = startXGrid2 + (spaceBetweenRowsGrid2 * rowGrid2Index)
            
            yPosGrid2 = startYGrid2 + (spaceBetweenColsGrid2 * colGrid2Index)

            # 2nd grid move
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

            # Run sequence after 2nd grid move
            if sequenceAfter2ndGridMove != "":
                device.log(message='Execute sequence: ' + sequenceAfter2ndGridMove, message_type='success')
                device.execute(sequenceAfter2ndGridMoveId)

            # Increment y column position for grid 1
            yPosGrid1 = yPosGrid1 + spaceBetweenColsGrid1

            # Set the second grid row and column indexes
            if ((alternateInBetweenGrid2 == 1)                  # Is alternateInBetween
            and (colGrid2Index > 0 and (colGrid2Index % 2) > 0) # is on an alternateInBetween odd numbered (offset) column  
            and (rowGrid2Index >= rowsGrid2 - 2)) :              # is on the second to last row index as an alternateInBetween has 1 less row
                rowGrid2Index = 0                                   # Reset row index
                colGrid2Index += 1                                  # Increment column index to move to the next column
            elif rowGrid2Index >= (rowsGrid2 - 1) :             # else if on the last row
                rowGrid2Index = 0                                   # Reset row index
                colGrid2Index += 1                                  # Increment column index to move to the next column
            else :                                              # else
                rowGrid2Index += 1                                  # Increment row index to move to the next row