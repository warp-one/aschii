_DEBUG = False

# actual size of the window
SCREEN_WIDTH = 60
SCREEN_HEIGHT = 45

FONT_IMG =  '16x16custom.png' #'terminal8x8_gs_ro.png'#

LVL0_MAP_WIDTH = 1
LVL0_MAP_HEIGHT = 1
 
LIMIT_FPS = 20   # frames-per-second maximum
PROFILE = False#True #

PLAYER_MAX_SIGHT = 61
RENDER_RADIUS_CIRCLE = PLAYER_MAX_SIGHT + 5

# these are more like game constants...

EAST_RIGHT_FOOT = 128   # libtcod maps characters to tiles in the tileset with
EAST_LEFT_FOOT = 129  # the integers 0-255
NORTH_LEFT_FOOT = 130
NORTH_RIGHT_FOOT = 131
WEST_RIGHT_FOOT = 132
WEST_LEFT_FOOT = 133
SOUTH_LEFT_FOOT = 134
SOUTH_RIGHT_FOOT = 135

FEET_CHARS = {(1, 0):(EAST_LEFT_FOOT, EAST_RIGHT_FOOT),
              (0, -1):(NORTH_LEFT_FOOT, NORTH_RIGHT_FOOT),
              (-1, 0):(WEST_RIGHT_FOOT, WEST_LEFT_FOOT),
              (0, 1):(SOUTH_RIGHT_FOOT, SOUTH_LEFT_FOOT),
              (1, 1):(EAST_LEFT_FOOT, EAST_RIGHT_FOOT)
              }