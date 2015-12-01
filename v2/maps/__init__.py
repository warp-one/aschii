from map import TileMap
from formations import *

Med10x10_1 = MediumHollow(cave10x10)
Boulders = (RandomBoulder(*xy) for xy in [(11, 11), (17, 17), (23, 23)])