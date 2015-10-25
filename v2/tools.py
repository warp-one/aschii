from math import sqrt

def get_distance(p1, p2):
    return sqrt((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2)

def get_xy_from_index(i, num_cols):
    return i%num_cols, i/num_cols