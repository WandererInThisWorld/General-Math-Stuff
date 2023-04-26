import numpy as np

### RELEVANT CONSTANTS
UNIT = 20
PI = 3.14159265359


# Given a linear map, create a list of pairs of endpoints that represent a line.
# The pair of endpoints will come in the following form: ((start_x, start_y), (end_x, end_y))
# It will NOT be adjusted for the coordinates; however, the grid will be truncated so that
# it can be contained within a box of some width and length
# map: 2 by 2 linear matrix (rows, not columns, are basis vectors)
# width: the width of the grid
# height: the height of the grid
# coord: coordinate of upper left corner of box
def create_grid(map, width, height, coord):
    # The unit length is 20 pixels

    # multiply linear map by another linear map that reflects it across the x-axis.
    # however, since im dealing with basis vectors as rows instead of columns
    # this means i have to adjust my calculations likewise
    # the transpose of the reflection matrix is the reflection matrix
    norm_map = np.array([[1,0],[0,-1]])

    # the order in which the map is multiplied must reversed since row, not column, basis
    # map = np.matmul(norm_map,map)
    map = np.matmul(map,norm_map)

    # wrap the origin into a numpy array and get the unit vectors
    origin = np.array([coord[0] + width/2, coord[1] + height/2])
    unit_xaxis = np.array(map[0]) # unit_xaxis = np.array([1,0])
    unit_yaxis = np.array(map[1]) # unit_yaxis = np.array([0,1])

    ## Vertical lines generated by going along the (adjusted) x-axis
    vertical_lines = []

    # first find all the points that goes along the adjusted x-axis
    # find how much integer points is along the (adjusted) x-axis using the (adjusted) units
    max_units = (coord[0] - origin[0]) / (UNIT * unit_xaxis[0])
    endpoint_xaxis = (UNIT * max_units * unit_xaxis) + origin

    if endpoint_xaxis[1] < coord[1] or endpoint_xaxis[1] > coord[1] + height:
        # the adjusted x-axis does not intersect the vertical bounds but horizontal bounds
        # in this case, then use a different equation to find max_units
        max_units = (coord[1] - origin[1]) / (UNIT * unit_xaxis[1])
    normed_max = int(-max_units) if max_units < 0 else int(max_units)

    # create vertical lines by going along the x-axis (adjusted)
    normed_max += 1
    normed_max = 100 if normed_max > 100 else normed_max
    for disp in range(-normed_max,normed_max,1):
        point = origin + UNIT*(disp * unit_xaxis)
        # where does the "top" intersect
        # p + t*u_y = [x,coord[1]]
        t = (coord[1] - point[1])/unit_yaxis[1]
        top_p = point + t*unit_yaxis
        
        # there is a chance that the vertical line does not intersect the horizontal bounds but
        # vertical bounds. which vertical bound does it intersect though?
        if top_p[0] < coord[0]:
            t = (coord[0] - point[0])/unit_yaxis[0]
        elif top_p[0] > coord[0] + width:
            t = (coord[0] + width - point[0])/unit_yaxis[0]
        # with this, we can establish the top of the vertical line that goes through the point given
        vert_line_top = point + (t*unit_yaxis)

        # similar logic is necessary to get the bottom point
        # where does the "bottom" intersect
        b = (coord[1] + height - point[1])/unit_yaxis[1]
        bot_p = point + b*unit_yaxis

        if bot_p[0] < coord[0]:
            b = (coord[0] - point[0])/(unit_yaxis[0])  
        elif bot_p[0] > coord[0] + width:
            b = (coord[0] + width - point[0])/(unit_yaxis[0])
        vert_line_bottom = point + (b*unit_yaxis)

        # READ THIS: a natural question i had was do i have to check whether the "top" intersects the
        # top vertical line and the "bottom" the bottom line, or whether it was the opposite way around?
        # This turned out not to be a problem since "top" and "bottom" are symmetric.

        # vert_line_bottom = point - (height/2 * unit_yaxis)
        # vert_line_top    = point + (height/2 * unit_yaxis)

        # Use fact that (A*x)^T = x^T*A^T
        # vert_line_bottom = np.matmul(vert_line_bottom,map)
        # vert_line_top    = np.matmul(vert_line_top,map)

        vertical_lines.append((vert_line_bottom, vert_line_top))

    ## Horizontal lines generated by going along the (adjusted) y-axis
    horizontal_lines = []

    # first find all the points that goes along the adjusted y-axis
    # find how much integer points is along the (adjusted) y-axis using the (adjusted) units
    max_units = (coord[1]-origin[1])/(UNIT*unit_yaxis[1])
    endpoint_yaxis = (UNIT * max_units * unit_yaxis) + origin

    if endpoint_yaxis[0] < coord[0] or endpoint_yaxis[0] > coord[0] + width:
        # the adjusted x-axis does not intersect the vertical bounds but horizontal bounds
        # in this case, then use a different equation to find max_units
        max_units = (coord[1] - origin[1])/(UNIT*unit_xaxis[1])
    normed_max = int(-max_units) if max_units < 0 else int(max_units)

    # create horizontal lines going along the adjusted y-axis
    normed_max += 1
    normed_max = 100 if normed_max > 100 else normed_max
    for disp in range(-normed_max,normed_max,1):
        point = origin + UNIT*(disp * unit_yaxis)
        # where does the "left" intersect
        # p + l*u_y = [coord[0],y]
        l = (coord[0] - point[0])/unit_xaxis[0]
        left_p = point + l*unit_xaxis

        # the horizontal line does not intersect the vertical bounds but horizontal bounds
        # which horizontal bound does it intersect though?
        if left_p[1] < coord[1]:
            l = (coord[1] - point[1])/unit_xaxis[1]
        elif left_p[1] > coord[1] + height:
            l = (coord[1] + height - point[1])/unit_xaxis[1]
        # with this, we can establish the left point of the horizontal line that goes through the given point
        hor_line_left = point + (l*unit_xaxis)

        # we can similarly get the right point
        # where does the "right" intersect
        r = (coord[0] + width - point[0])/unit_xaxis[0]
        right_p = point + r*unit_xaxis

        # the horizontal line does not intersect the vertical bounds but horizontal bounds
        # which horizontal bound does it intersect though?
        if right_p[1] < coord[1]:
            r = (coord[1] - point[1])/unit_xaxis[1]
        elif right_p[1] > coord[1] + height:
            r = (coord[1] + height - point[1])/unit_xaxis[1]
        # with this, we can establish the right point of the horizontal line that goes through the given point
        hor_line_right = point + (r*unit_xaxis)

        # Use fact that (A*x)^T = x^T*A^T
        # hor_line_left  = np.matmul(hor_line_left,map)
        # hor_line_right = np.matmul(hor_line_right,map)

        # hor_line_left  = origin + hor_line_left
        # hor_line_right = origin + hor_line_right
        # horizontal_lines.append((hor_line_left, hor_line_right))


        horizontal_lines.append((hor_line_left, hor_line_right))
    
    '''
    vertical_lines = []
    adj_width = width/UNIT
    # create vertical lines by going along with x-axis (adjusted)
    for disp in range(int(-adj_width/2),int(adj_width/2) + 1,1):
        vert_line_bottom = UNIT*(disp * unit_xaxis) - (height/2 * unit_yaxis)
        vert_line_top    = UNIT*(disp * unit_xaxis) + (height/2 * unit_yaxis)

        # Use fact that (A*x)^T = x^T*A^T
        # vert_line_bottom = np.matmul(vert_line_bottom,map)
        # vert_line_top    = np.matmul(vert_line_top,map)

        vert_line_bottom = origin + vert_line_bottom
        vert_line_top    = origin + vert_line_top
        vertical_lines.append((vert_line_bottom, vert_line_top))
    '''
    '''
    horizontal_lines = []
    adj_height = height/UNIT
    # create horizontal lines by going along the y-axis (adjusted)
    for disp in range(int(-adj_height/2),int(adj_height/2) + 1,1):
        hor_line_left  = UNIT*(disp * unit_yaxis) - (width/2 * unit_xaxis)
        hor_line_right = UNIT*(disp * unit_yaxis) + (width/2 * unit_xaxis)

        # Use fact that (A*x)^T = x^T*A^T
        # hor_line_left  = np.matmul(hor_line_left,map)
        # hor_line_right = np.matmul(hor_line_right,map)


        hor_line_left  = origin + hor_line_left
        hor_line_right = origin + hor_line_right
        horizontal_lines.append((hor_line_left, hor_line_right))
    '''
    
    lines = []
    for vl in vertical_lines:
        lines.append(vl)
    for hl in horizontal_lines:
        lines.append(hl)
    # return [(neg_xaxis,pos_xaxis),(neg_yaxis,pos_yaxis)]
    return lines

#
def create_line():
    ...
    
def main():
    pygame.init()
    SCREEN_WIDTH = SCREEN_HEIGHT = 800
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    WHITE = (255,255,255)
    BLACK = (0,0,0)
    pygame.display.set_caption("Grid Example")

    clock = pygame.time.Clock()

    # line width 2
    LINE_WIDTH = 2
    m = 0
    grid_width = grid_height = SCREEN_WIDTH/2

    running = True
    while running:
        clock.tick(30)
        screen.fill(BLACK)

        angle = m * PI/60  
        cc_rotation = np.array([[cos(angle),sin(angle)],[-sin(angle),cos(angle)]])
        c_rotation = np.array([[cos(-angle),sin(-angle)],[-sin(-angle),cos(-angle)]])
        grid1 = create_grid(cc_rotation,grid_width,grid_height,(0, 0))
        grid2 = create_grid(c_rotation,grid_width,grid_height,(0, SCREEN_HEIGHT/2))
        grid3 = create_grid(c_rotation,grid_width,grid_height,(SCREEN_WIDTH/2, 0))
        grid4 = create_grid(cc_rotation,grid_width,grid_height,(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
        

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        for line in grid1:
            pygame.draw.line(screen,WHITE,line[0],line[1],LINE_WIDTH)
        for line in grid2:
            pygame.draw.line(screen,WHITE,line[0],line[1],LINE_WIDTH)
        for line in grid3:
            pygame.draw.line(screen,WHITE,line[0],line[1],LINE_WIDTH)
        for line in grid4:
            pygame.draw.line(screen,WHITE,line[0],line[1],LINE_WIDTH)
        
        pygame.display.flip()
        m += 1

    pygame.quit()
    

if __name__ == '__main__':
    import pygame
    from math import sin, cos
    main()

