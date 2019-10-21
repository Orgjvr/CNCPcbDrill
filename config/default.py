# Note: Only uppercase variable names will be read
# DEBUG = False
SQLALCHEMY_ECHO = False
SERIALPORTBAUDRATE = 115200
UPLOAD_FOLDER = "uploads"
#INTEGER_DIGITS_IN_DRILLFILE = 3    #NOTE: repladed by reading file 
#DECIMAL_DIGITS_IN_DRILLFILE = 3    #NOTE: repladed by reading file 
GCODE_FLAVOUR = "G" # Possible values is (G)RBL, (M)arlin, (S)moothie
CAMERA_INDEX = 0
CNC_MOVES = {"coarse":10,"normal":1,"fine":0.1}
COLOR_DICT = { 1: "black", 2:"red", 3:"saddlebrown",
    4:"darkorange",5:"olivedrab",6:"green",
    7:"darkcyan",8:"dodgerblue",9:"blue",
    10:"darkviolet",11:"magenta",12:"crimson"}