from math import asin, atan2, copysign, pi

def rad2deg(rad):
    return rad / pi * 180

def deg2rad(deg):
    return deg / 180 * pi

def getEulerAngles(q):
    sinr_cosp = q[0] * q[1] + q[2] * q[3]
    cosr_cosp = 1 - 2 * (q[1] * q[1] + q[2] * q[2])
    sinp =  2 * (q[0] * q[2] - q[3] * q[1])

    roll = atan2(sinr_cosp, cosr_cosp)

    if (abs(sinp) >= 1):
        pitch = copysign(pi /2, sinp)
    else:
        pitch = asin(sinp)

    siny_cosp = 2 * (q[0] * q[3] + q[1] * q[2])
    cosy_cosp = 1 - 2 * (q[2] * q[2] + q[3] * q[3])
    yaw = atan2(siny_cosp, cosy_cosp)

    return yaw, pitch, roll

