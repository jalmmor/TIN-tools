import numpy as np

class PlaneCalc:
    def __init__(self, vertices):
        mp=[np.array([v.x(),v.y(), v.z() ]) for v in vertices]
        v1 = mp[2] - mp[0]
        v2 = mp[1] - mp[0]
        cp = np.cross(v1, v2)
        a, b, c = cp
        d = np.dot(cp, mp[2])
        self.coef=(a, b, c, d)

    def cal_z(self, x, y):
        a, b, c, d = self.coef
        z=(d-a*x -b*y)/c
        return z

