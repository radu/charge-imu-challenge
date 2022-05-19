#!/usr/bin/python3
import numpy as np
import pandas as pd
from numpy.linalg import inv
from math import sin, cos, atan2, asin, acos, pi, copysign

import sys

from cubedraw import *
from angles import *

def main(alpha):
    measurements = pd.read_csv('imu.csv', sep="\s*[,]\s*", engine="python")
    measurements = measurements.apply(pd.to_numeric)

    xaccel = measurements[['accel_x']].to_numpy()[:,0]
    yaccel = measurements[['accel_y']].to_numpy()[:,0]
    zaccel = measurements[['accel_z']].to_numpy()[:,0]

    # acceleration norm
    a = np.sqrt(np.square(xaccel) + np.square(yaccel) + np.square(zaccel))

    t = measurements[['time']].to_numpy()[:,0]

    # first calculate pitch and roll from accel only, for the entire vector
    roll = np.arctan2(yaccel / a, zaccel / a)
    pitch = np.arctan2(-xaccel / a, np.sqrt(np.square(yaccel / a) + np.square(zaccel / a)))

    # a quaternion representation is more robust + easier to work with
    zsq_pos = np.sqrt(2*(zaccel + 1))
    zsq_neg = np.sqrt(2*(1-zaccel))

    # accelerometer-only quaternion
    qacc  = np.array([ np.array(
                [(az+1) / zp , -ay/zp, ax/zp, 0] 
            ).T if az >=0 else
            np.array(
                [-ay / zn, (1-az) / zn, 0, ax/zn ]
            ).T for ax, ay, az, zp, zn in zip(xaccel, yaccel, zaccel, zsq_pos, zsq_neg)])

    # now let's look at the gyro
    gyro = measurements[['gyro_x', 'gyro_y', 'gyro_z']].to_numpy()

    # initializing t=0 attitude from accel only
    att = np.zeros_like(qacc)
    att[0] = qacc[0]

    # a complementary filter leaves the low-frequency updates to the accel and essentially high pass filters the gyro
    delta = 0.05

    video_flags = OPENGL | DOUBLEBUF
    pygame.init()
    screen = pygame.display.set_mode((640, 480), video_flags)
    pygame.display.set_caption("orientation visualization")
    resizewin(640, 480)
    cubeinit()

    for i in range(1,len(t)):
        framestart = pygame.time.get_ticks()

        event = pygame.event.poll()
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            break
        if event.type == KEYDOWN:
            if event.key == K_EQUALS or event.key == K_PLUS:
                alpha = min(alpha + delta, 1.0)
            elif event.key == K_MINUS:
                alpha = max(alpha - delta, 0.0)
            elif event.key == K_0:
                alpha = 0
            elif event.key == K_1:
                alpha = 1          

        dt = t[i] - t[i-1]

        wx, wy, wz = tuple(gyro[i])

        #  gyro-only attitude propagation
        qw = (np.identity(4) + dt/2*np.array([
            [0, -wx, -wy, -wz],
            [wx, 0, wz, -wy],
            [wy, -wz, 0, wx],
            [wz, wy, -wx, 0]
            ])).dot(att[i-1])

        # tilt from accel only at this time step
        p2 = pitch[i]/2
        t2 = roll[i]/2
        
        # since we don't have a magentometer, we could use the last heading from the gyro integration only
        lq = qw / np.linalg.norm(qw)
        lyaw, _, _ = getEulerAngles(lq)

        h2 = lyaw / 2

        # unfortunately this gets confused when upside down, so discarding heading for now :(
        h2 = 0

        qam = np.array([
            cos(p2)*cos(t2)*cos(h2)+sin(p2)*sin(t2)*sin(h2),
            sin(p2)*cos(t2)*cos(h2)-cos(p2)*sin(t2)*sin(h2),
            cos(p2)*sin(t2)*cos(h2)-sin(p2)*cos(t2)*sin(h2),
            cos(p2)*cos(t2)*sin(h2)-sin(p2)*sin(t2)*cos(h2),
        ]).T

        att[i] = qw*(1-alpha) + qam * alpha
        
        cubedraw(att[i], alpha)
        
        pygame.display.flip()

        pygame.time.wait(int(dt*1000 - framestart))
    

if __name__ == "__main__":
    #  alpha = 1 is accel only
    #  alpha = 0 is gyro only

    for arg in sys.argv :
        if arg == 'gyro':
            main(0)
        elif arg == 'accel':
            main(1)

    main(0.05)