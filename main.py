import turtle
import random
from settings import *
from time import sleep

# 0 off 1 on
debug = 1

def debugprint(statement):
  if debug == 1:
    print statement

tiles = []
interfaces = {
  "instructions" : None,
  "solved" : None,
  "level" : None
}

game_state = {
  "level"        : 0,
  "levels"       : None,
  "player_image" : 0
};

class Interface(turtle.Turtle):
  def __init__(self, screen, x = 0, y = 0):
    turtle.Turtle.__init__(self)
    self.hideturtle()
    self.speed(0)
    self.penup()
    self.setpos(x, y)
    self.done = False

class Tile(turtle.Turtle):
    def __init__(self, screen, x = 0, y = 0, shape = 'turtle'):
      turtle.Turtle.__init__(self)
      self.speed(0)
      self.penup()
      self.goto(x,y)
      self.shape(shape)
      self.left(90)

def main():
    if debug == 1:
      debugprint("main")
    
    mainscreen = turtle.Screen()
    mainscreen.setup(WINWIDTH, WINHEIGHT, 0, 0)
    mainscreen.setworldcoordinates(0,0,WINWIDTH,WINHEIGHT)
    mainscreen.tracer(0)
    mainscreen.colormode(255)
    mainscreen.bgcolor(BGCOLOR)
    
    for key in interfaces:
      interfaces[key] = Interface(mainscreen)

    for file in IMAGESDICT.values():
      print file
      #debugprint(shape)
      mainscreen.register_shape(file)
    
    # Read in the levels from the text file. See the readLevelsFile() for
    # details on the format of this file and how to make your own levels.
    game_state["levels"] = readLevelsFile('starPusherLevels.txt')
    game_state["level"]  = 0;
    game_state["player_image"] = 0;

    def nextLevel(result):
      if result in ('solved', 'next'):
        # Go to the next level.
        game_state["level"] += 1;
        if game_state["level"] >= len(game_state["levels"]):
            # If there are no more levels, go back to the first one.
            game_state["level"] = 0
      elif result == 'back':
        # Go to the previous level.
        game_state["level"] -= 1
        if game_state["level"] < 0:
            # If there are no previous levels, go to the last one.
            game_state["level"] = len(game_state["levels"])-1
      elif result == 'reset':
        return # Do nothing. Loop re-calls runLevel() to reset the level
    
      runLevel(game_state, mainscreen, nextLevel)
      
    startScreen(game_state, mainscreen, nextLevel) # show the title screen until the user presses a key
  
def runLevel(game_state, screen, done):
    if debug == 1:
      debugprint("run level")
    
    solved = None
    levelwriter = interfaces["level"]
    levelwriter.clear()
    levelNum = game_state["level"]
    levels  = game_state["levels"]
    levelObj = game_state["levels"][game_state["level"]]
    mapObj = decorateMap(levelObj['mapObj'], levelObj['startState']['player'])
    # TODO: Copy!
    levelState = levelObj['startState']
    levelState['complete'] = False
    levelState['redraw'] = True
    
    levelwriter.goto(20, WINHEIGHT - 35)
    levelwriter.write('Level %s of %s' % (levelNum + 1, len(levels)), align = "left")
    
    mapWidth = len(mapObj) * TILEWIDTH
    mapHeight = (len(mapObj[0]) - 1) * TILEFLOORHEIGHT + TILEHEIGHT
    MAX_CAM_X_PAN = abs(HALF_WINHEIGHT - int(mapHeight / 2)) + TILEWIDTH
    MAX_CAM_Y_PAN = abs(HALF_WINWIDTH - int(mapWidth / 2)) + TILEHEIGHT

    # Track how much the camera has moved:
    cameraOffsetX = 0
    cameraOffsetY = 0
    # Track if the keys to move the camera are being held down:
    cameraUp = False
    cameraDown = False
    cameraLeft = False
    cameraRight = False
    
    def end():
      done("solved")
    
    def update_screen():
      if levelState['redraw']:
        drawMap(mapObj, levelState, levelObj['goals'], screen)
        screen.update()
        levelState['redraw'] = False

      if cameraUp and cameraOffsetY < MAX_CAM_X_PAN:
          cameraOffsetY += CAM_MOVE_SPEED
      elif cameraDown and cameraOffsetY > -MAX_CAM_X_PAN:
          cameraOffsetY -= CAM_MOVE_SPEED
      if cameraLeft and cameraOffsetX < MAX_CAM_Y_PAN:
          cameraOffsetX += CAM_MOVE_SPEED
      elif cameraRight and cameraOffsetX > -MAX_CAM_Y_PAN:
          cameraOffsetX -= CAM_MOVE_SPEED
      
      if levelState["complete"]:
        debugprint("level is complete")
        solved = Interface(screen, 50, WINHEIGHT - 50)
        # solved.clear()
        solved.shape(IMAGESDICT['solved'])
        screen.update()
        sleep(3)
        end()
     
    def move(playerMoveTo):
      debugprint("move " + playerMoveTo)
      moved = makeMove(mapObj, levelState, playerMoveTo)

      if moved:
        # increment the step counter.
        levelState['stepCounter'] += 1
        levelState['redraw'] = True

      if isLevelFinished(levelObj, levelState):
        # level is solved, we should show the "Solved!" image.
        levelState["complete"] = True
      
      update_screen()

    def left():
      move(LEFT)

    def right():
      move(RIGHT)

    def up():
      move(DOWN)

    def down():
      move(UP)
    
    screen.onkey(left, 'Left')
    screen.onkey(right, 'Right')
    screen.onkey(up, 'Up')
    screen.onkey(down, 'Down')
    # Todo: implement other controls

    update_screen()

def isWall(mapObj, x, y):
    """Returns True if the (x, y) position on
    the map is a wall, otherwise return False."""
    if x < 0 or x >= len(mapObj) or y < 0 or y >= len(mapObj[x]):
        return False # x and y aren't actually on the map.
    elif mapObj[x][y] in ('#', 'x'):
        return True # wall is blocking
    return False


def decorateMap(mapObj, startxy):
    """Makes a copy of the given map object and modifies it.
    Here is what is done to it:
        * Walls that are corners are turned into corner pieces.
        * The outside/inside floor tile distinction is made.
        * Tree/rock decorations are randomly added to the outside tiles.
    Returns the decorated map object."""

    startx, starty = startxy # Syntactic sugar

    # Copy the map object so we don't modify the original passed
    # TODO: Copy!
    mapObjCopy = mapObj[:]

    # Remove the non-wall characters from the map data
    for x in range(len(mapObjCopy)):
        for y in range(len(mapObjCopy[0])):
            if mapObjCopy[x][y] in ('$', '.', '@', '+', '*'):
                mapObjCopy[x][y] = ' '

    # Flood fill to determine inside/outside floor tiles.
    floodFill(mapObjCopy, startx, starty, ' ', 'o')

    # Convert the adj8oined walls into corner tiles.
    for x in range(len(mapObjCopy)):
        for y in range(len(mapObjCopy[0])):

            if mapObjCopy[x][y] == '#':
                if (isWall(mapObjCopy, x, y-1) and isWall(mapObjCopy, x+1, y)) or \
                   (isWall(mapObjCopy, x+1, y) and isWall(mapObjCopy, x, y+1)) or \
                   (isWall(mapObjCopy, x, y+1) and isWall(mapObjCopy, x-1, y)) or \
                   (isWall(mapObjCopy, x-1, y) and isWall(mapObjCopy, x, y-1)):
                    mapObjCopy[x][y] = 'x'

            elif mapObjCopy[x][y] == ' ' and random.randint(0, 99) < OUTSIDE_DECORATION_PCT:
                mapObjCopy[x][y] = random.choice(list(OUTSIDEDECOMAPPING.keys()))

    return mapObjCopy


def isBlocked(mapObj, gameStateObj, x, y):
    """Returns True if the (x, y) position on the map is
    blocked by a wall or star, otherwise return False."""

    if isWall(mapObj, x, y):
        return True

    elif x < 0 or x >= len(mapObj) or y < 0 or y >= len(mapObj[x]):
        return True # x and y aren't actually on the map.

    elif (x, y) in gameStateObj['stars']:
        return True # a star is blocking

    return False


def makeMove(mapObj, gameStateObj, playerMoveTo):
    """Given a map and game state object, see if it is possible for the
    player to make the given move. If it is, then change the player's
    position (and the position of any pushed star). If not, do nothing.
    Returns True if the player moved, otherwise False."""

    debugprint("makemove")
    # Make sure the player can move in the direction they want.
    playerx, playery = gameStateObj['player']

    # This variable is "syntactic sugar". Typing "stars" is more
    # readable than typing "gameStateObj['stars']" in our code.
    stars = gameStateObj['stars']

    # The code for handling each of the directions is so similar aside
    # from adding or subtracting 1 to the x/y coordinates. We can
    # simplify it by using the xOffset and yOffset variables.
    if playerMoveTo == UP:
        xOffset = 0
        yOffset = 1
    elif playerMoveTo == RIGHT:
        xOffset = 1
        yOffset = 0
    elif playerMoveTo == DOWN:
        xOffset = 0
        yOffset = -1
    elif playerMoveTo == LEFT:
        xOffset = -1
        yOffset = 0

    # See if the player can move in that direction.
    if isWall(mapObj, playerx + xOffset, playery + yOffset):
        return False
    else:
        if (playerx + xOffset, playery + yOffset) in stars:
            # There is a star in the way, see if the player can push it.
            if not isBlocked(mapObj, gameStateObj, playerx + (xOffset*2), playery + (yOffset*2)):
                # Move the star.
                ind = stars.index((playerx + xOffset, playery + yOffset))
                stars[ind] = (stars[ind][0] + xOffset, stars[ind][1] + yOffset)
            else:
                return False
        # Move the player upwards.
        gameStateObj['player'] = (playerx + xOffset, playery + yOffset)
        return True


def startScreen(game_state, screen, done):
    if debug == 1:
      debugprint("startscreen")

    """Display the start screen (which has the title and instructions)
    until the player presses a key. Returns None."""
    
    writer = interfaces["instructions"]
    writer.clear()
    writer.color(TEXTCOLOR)
    title = Interface(screen)
    title.shape(IMAGESDICT['title'])
    
    # Position the title image.
    title.sety(HALF_WINHEIGHT)

    # Unfortunately, Pygame's font & text system only shows one line at
    # a time, so we can't use strings with \n newline characters in them.
    # So we will use a list with each line in it.
    instructionText = ['Push the stars over the marks.',
                       'Arrow keys to move, P to change character.',
                       'Backspace to reset level, Esc to quit.',
                       'N for next level, B to go back a level.',
                       'Press S to Start!']

    writer.setx(50)
    writer.sety(WINHEIGHT - 50)
    # Position and draw the text.
    for i in range(len(instructionText)):
        writer.write(instructionText[i], font=("Arial", 20), align = "left")
        writer.sety(writer.pos()[1] - 25) # 10 pixels will go in between each line of text.
    
    def begin():
      writer.clear()
      writer.done = True
      screen.update()
      debugprint("begin")
      done("start")
    
    def next_level():
      done("next")
    
    def prev_level():
      done("back")
      
    screen.onkey(terminate, 'Escape')
    screen.onkey(begin, "s")
    screen.onkey(next_level, "n")
    screen.onkey(prev_level, "b")
    
    screen.listen()
    screen.update()

    print "end  ???"
    turtle.mainloop()

def readLevelsFile(filename):
    #assert os.path.exists(filename), 'Cannot find the level file: %s' % (filename)
    mapFile = open(filename, 'r')
    # Each level must end with a blank line
    content = mapFile.readlines() + ['\r\n']
    mapFile.close()

    levels = [] # Will contain a list of level objects.
    levelNum = 0
    mapTextLines = [] # contains the lines for a single level's map.
    mapObj = [] # the map object made from the data in mapTextLines
    for lineNum in range(len(content)):
        # Process each line that was in the level file.
        line = content[lineNum].rstrip('\r\n')

        if ';' in line:
            # Ignore the ; lines, they're comments in the level file.
            line = line[:line.find(';')]

        if line != '':
            # This line is part of the map.
            mapTextLines.append(line)
        elif line == '' and len(mapTextLines) > 0:
            # A blank line indicates the end of a level's map in the file.
            # Convert the text in mapTextLines into a level object.

            # Find the longest row in the map.
            maxWidth = -1
            for i in range(len(mapTextLines)):
                if len(mapTextLines[i]) > maxWidth:
                    maxWidth = len(mapTextLines[i])
            # Add spaces to the ends of the shorter rows. This
            # ensures the map will be rectangular.
            for i in range(len(mapTextLines)):
                mapTextLines[i] += ' ' * (maxWidth - len(mapTextLines[i]))

            # Convert mapTextLines to a map object.
            for x in range(len(mapTextLines[0])):
                mapObj.append([])
            for y in range(len(mapTextLines)):
                for x in range(maxWidth):
                    mapObj[x].append(mapTextLines[y][x])

            # Loop through the spaces in the map and find the @, ., and $
            # characters for the starting game state.
            startx = None # The x and y for the player's starting position
            starty = None
            goals = [] # list of (x, y) tuples for each goal.
            stars = [] # list of (x, y) for each star's starting position.
            for x in range(maxWidth):
                for y in range(len(mapObj[x])):
                    if mapObj[x][y] in ('@', '+'):
                        # '@' is player, '+' is player & goal
                        startx = x
                        starty = y
                    if mapObj[x][y] in ('.', '+', '*'):
                        # '.' is goal, '*' is star & goal
                        goals.append((x, y))
                    if mapObj[x][y] in ('$', '*'):
                        # '$' is star
                        stars.append((x, y))

            # Basic level design sanity checks:
            assert startx != None and starty != None, 'Level %s (around line %s) in %s is missing a "@" or "+" to mark the start point.' % (levelNum+1, lineNum, filename)
            assert len(goals) > 0, 'Level %s (around line %s) in %s must have at least one goal.' % (levelNum+1, lineNum, filename)
            assert len(stars) >= len(goals), 'Level %s (around line %s) in %s is impossible to solve. It has %s goals but only %s stars.' % (levelNum+1, lineNum, filename, len(goals), len(stars))

            # Create level object and starting game state object.
            gameStateObj = {'player': (startx, starty),
                            'stepCounter': 0,
                            'stars': stars}
            levelObj = {'width': maxWidth,
                        'height': len(mapObj),
                        'mapObj': mapObj,
                        'goals': goals,
                        'startState': gameStateObj}

            levels.append(levelObj)

            # Reset the variables for reading the next map.
            mapTextLines = []
            mapObj = []
            gameStateObj = {}
            levelNum += 1
    return levels

def floodFill(mapObj, x, y, oldCharacter, newCharacter):
    """Changes any values matching oldCharacter on the map object to
    newCharacter at the (x, y) position, and does the same for the
    positions to the left, right, down, and up of (x, y), recursively."""

    # In this game, the flood fill algorithm creates the inside/outside
    # floor distinction. This is a "recursive" function.
    # For more info on the Flood Fill algorithm, see:
    #   http://en.wikipedia.org/wiki/Flood_fill
    if mapObj[x][y] == oldCharacter:
        mapObj[x][y] = newCharacter

    if x < len(mapObj) - 1 and mapObj[x+1][y] == oldCharacter:
        floodFill(mapObj, x+1, y, oldCharacter, newCharacter) # call right
    if x > 0 and mapObj[x-1][y] == oldCharacter:
        floodFill(mapObj, x-1, y, oldCharacter, newCharacter) # call left
    if y < len(mapObj[x]) - 1 and mapObj[x][y+1] == oldCharacter:
        floodFill(mapObj, x, y+1, oldCharacter, newCharacter) # call down
    if y > 0 and mapObj[x][y-1] == oldCharacter:
        floodFill(mapObj, x, y-1, oldCharacter, newCharacter) # call up


def drawMap(mapObj, gameStateObj, goals, screen):
    """Should create a turtle at each point on the grid and set its shape 
    to the correct one depending on the level's layout."""
    
    # mapSurf will be the single Surface object that the tiles are drawn
    # on, so that it is easy to position the entire map on the DISPLAYSURF
    # Surface object. First, the width and height must be calculated.
    # mapWidth = len(mapObj) * TILEWIDTH
    # mapSurfHeight = (len(mapObj[0]) - 1) * TILEFLOORHEIGHT + TILEHEIGHT
    # mapSurf = pygame.Surface((mapSurfWidth, mapSurfHeight))
    # mapSurf.fill(BGCOLOR) # start with a blank color on the surface.
    
    for i in xrange(len(tiles)):
      tiles[i].hideturtle()
    
    debugprint("drawing map")
    
    nxtiles = len(mapObj)
    nytiles = len(mapObj[0])
    
    xoffset = TILEWIDTH/2 + TILEWIDTH
    yoffset = WINHEIGHT - TILEHEIGHT/2 - TILEWIDTH
    
    tileCount = 0;
    
    def updateTile(screen, xpos, ypos, shape):
      global tiles
      
      if tileCount >= len(tiles):
        tiles.append(Tile(screen, xpos, ypos, shape))
      else:
        tiles[tileCount].goto(xpos, ypos)
        tiles[tileCount].shape(shape)
        tiles[tileCount].showturtle()

      return tileCount + 1
    
    # screen.tracer(1)
    # # Draw the tile sprites onto this surface.
    for x in range(nxtiles):
      for y in range(nytiles):
        xpos = x*TILEWIDTH + xoffset
        ypos = yoffset - y*40
        
        if mapObj[x][y] in TILEMAPPING:
          baseTile = TILEMAPPING[mapObj[x][y]]
        elif mapObj[x][y] in OUTSIDEDECOMAPPING:
          baseTile = TILEMAPPING[' ']

        # First draw the base ground/wall tile.
        tileCount = updateTile(screen, xpos, ypos, baseTile)
        # debugprint(xpos)
        # debugprint(ypos)
        if mapObj[x][y] in OUTSIDEDECOMAPPING:
          # Draw any tree/rock decorations that are on this tile.
          tileCount = updateTile(screen,xpos,ypos,OUTSIDEDECOMAPPING[mapObj[x][y]])
        elif (x, y) in gameStateObj['stars']:
          if (x, y) in goals:
              # A goal AND star are on this space, draw goal first.
              tileCount = updateTile(screen,xpos,ypos,IMAGESDICT['covered goal'])
          # Then draw the star sprite.
          tileCount = updateTile(screen,xpos,ypos,IMAGESDICT['star'])
        elif (x, y) in goals:
          # Draw a goal without a star on it.
          tileCount = updateTile(screen,xpos,ypos,IMAGESDICT['uncovered goal'])

        # Last draw the player on the board.
        if (x, y) == gameStateObj['player']:
          # Note: The value "player_image" refers
          # to a key in "PLAYERIMAGES" which has the
          # specific player image we want to show.
          tileCount = updateTile(screen,xpos,ypos,PLAYERIMAGES[game_state["player_image"]])
          debugprint(PLAYERIMAGES[game_state["player_image"]])

def isLevelFinished(levelObj, gameStateObj):
    """Returns True if all the goals have stars in them."""
    for goal in levelObj['goals']:
        if goal not in gameStateObj['stars']:
            # Found a space with a goal but no star on it.
            return False
    return True


def terminate(screen):
  screen.reset()
  screen.bye()

if __name__ == '__main__':
    main()
