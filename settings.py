FPS = 30 # frames per second to update the screen
WINWIDTH = 800 # width of the program's window, in pixels
WINHEIGHT = 800 # height in pixels
HALF_WINWIDTH = int(WINWIDTH / 2)
HALF_WINHEIGHT = int(WINHEIGHT / 2)

# The total width and height of each tile in pixels.
TILEWIDTH = 50
TILEHEIGHT = 75
TILEFLOORHEIGHT = 40

CAM_MOVE_SPEED = 5 # how many pixels per frame the camera moves

# The percentage of outdoor tiles that have additional
# decoration on them, such as a tree or rock.
OUTSIDE_DECORATION_PCT = 20

BRIGHTBLUE = (  0, 170, 255)
WHITE      = (255, 255, 255)
BGCOLOR = BRIGHTBLUE
TEXTCOLOR = WHITE

UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'

BASICFONT = "Arial"

# A global dict value that will contain all the Pygame
# Surface objects returned by pygame.image.load().
IMAGESDICT = {'uncovered goal': 'RedSelector.gif',
              'covered goal': 'Selector.gif',
              'star': 'Star.gif',
              'corner': 'Wall_Block_Tall.gif',
              'wall': 'Wood_Block_Tall.gif',
              'inside floor': 'Plain_Block.gif',
              'outside floor': 'Grass_Block.gif',
              'title': 'star_title.gif',
              'solved': 'star_solved.gif',
              'princess': 'princess.gif',
              'boy': 'boy.gif',
              'catgirl': 'catgirl.gif',
              'horngirl': 'horngirl.gif',
              'pinkgirl': 'pinkgirl.gif',
              'rock': 'Rock.gif',
              'short tree': 'Tree_Short.gif',
              'tall tree': 'Tree_Tall.gif',
              'ugly tree': 'Tree_Ugly.gif'}

# These dict values are global, and map the character that appears
# in the level file to the Surface object it represents.
TILEMAPPING = {'x': IMAGESDICT['corner'],
               '#': IMAGESDICT['wall'],
               'o': IMAGESDICT['inside floor'],
               ' ': IMAGESDICT['outside floor']}
OUTSIDEDECOMAPPING = {'1': IMAGESDICT['rock'],
                      '2': IMAGESDICT['short tree'],
                      '3': IMAGESDICT['tall tree'],
                      '4': IMAGESDICT['ugly tree']}

# PLAYERIMAGES is a list of all possible characters the player can be.
PLAYERIMAGES = [IMAGESDICT['princess'],
                IMAGESDICT['boy'],
                IMAGESDICT['catgirl'],
                IMAGESDICT['horngirl'],
                IMAGESDICT['pinkgirl']]
