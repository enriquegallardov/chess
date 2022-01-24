import configparser

# Load configuration parser
config = configparser.ConfigParser()
config.read("config/config.ini")

TILESIZE = int(config["TILESIZE"]["TILESIZE"])


def get_position_from_coordinates(coords):
    """Return the grid position based on the x and y coordinates"""
    return (coords[1] // TILESIZE, coords[0] // TILESIZE)
