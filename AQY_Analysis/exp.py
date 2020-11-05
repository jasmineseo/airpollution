###
# Script for plotting and animating both PurpleAir and AQY data from a controlled experiment
# across multiple rounds. If a similar experiment is performed in the future, the filenames
# and round times can be subsituted into the global variables at the top of the script to
# produce new plots
###

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from datetime import datetime
from datetime import timedelta
from pytz import timezone
from scipy import interpolate

S1 = "exp5_data/PA1.csv" #  0  0  0  0
S2 = "exp5_data/PA2.csv" #  2  6 10 14
S3 = "exp5_data/PA2.csv" #  4  8 12 16
S4 = "exp5_data/PA4.csv" # 30 30 30 30
AERO_EXHAUST = "exp5_data/AQY BD-1160 Data Export.csv"
AERO_DISTANT = "exp5_data/AQY BD-1161 Data Export.csv" # 30 4 8 12 16

# Start, End times for each round
ROUND_TIMES =  {1: ["16:28:54", "16:55:00"],
                2: ["15:07:52", "15:22:54"],
                3: ["15:32:28", "15:47:05"],
                4: ["15:58:46", "16:12:19"]}

GLOBAL_START = datetime.strptime("15:00:00", "%H:%M:%S").replace(tzinfo=timezone('US/Pacific'))

R1 = [datetime.strptime(ROUND_TIMES[1][0], "%H:%M:%S").replace(tzinfo=timezone('US/Pacific')), \
      datetime.strptime(ROUND_TIMES[1][1], "%H:%M:%S").replace(tzinfo=timezone('US/Pacific'))]
R2 = [datetime.strptime(ROUND_TIMES[2][0], "%H:%M:%S").replace(tzinfo=timezone('US/Pacific')), \
      datetime.strptime(ROUND_TIMES[2][1], "%H:%M:%S").replace(tzinfo=timezone('US/Pacific'))]
R3 = [datetime.strptime(ROUND_TIMES[3][0], "%H:%M:%S").replace(tzinfo=timezone('US/Pacific')), \
      datetime.strptime(ROUND_TIMES[3][1], "%H:%M:%S").replace(tzinfo=timezone('US/Pacific'))]
R4 = [datetime.strptime(ROUND_TIMES[4][0], "%H:%M:%S").replace(tzinfo=timezone('US/Pacific')), \
      datetime.strptime(ROUND_TIMES[4][1], "%H:%M:%S").replace(tzinfo=timezone('US/Pacific'))]

round_list = [R1, R2, R3, R4]

R2_RANGE = [datetime.strptime("15:02:00", "%H:%M:%S").replace(tzinfo=timezone('US/Pacific')), \
      datetime.strptime("15:28:00", "%H:%M:%S").replace(tzinfo=timezone('US/Pacific'))]

def dateToMinutes(start, date):
    delta = date - start
    secs = delta.total_seconds()
    return secs/60

def purple_air_full(filename):
    df = pd.read_csv(filename)
    pm = df["pm2_5_atm"].tolist()
    times = [x[-9:-1] for x in df["UTCDateTime"].tolist()]
    dates = [datetime.strptime(x, "%H:%M:%S") for x in times]
    utcTimes = [x.replace(tzinfo=timezone('UTC')) for x in dates]
    pstTimes = [x.astimezone(timezone('US/Pacific'))-timedelta(minutes=7) for x in utcTimes]
    for i in range(len(pstTimes)):
        if pstTimes[i].day == 31:
            pstTimes[i] = pstTimes[i]+timedelta(days=1)
    return [pm, [dateToMinutes(GLOBAL_START, x) for x in pstTimes]]

S1F = purple_air_full(S1)
S2F = purple_air_full(S2)
S3F = purple_air_full(S3)
S4F = purple_air_full(S4)

def purple_air(filename, timeRange = None):
    df = pd.read_csv(filename)
    pm = df["pm2_5_atm"].tolist()
    times = [x[-9:-1] for x in df["UTCDateTime"].tolist()]
    dates = [datetime.strptime(x, "%H:%M:%S") for x in times]
    utcTimes = [x.replace(tzinfo=timezone('UTC')) for x in dates]
    pstTimes = [x.astimezone(timezone('US/Pacific'))-timedelta(minutes=7) for x in utcTimes]
    for i in range(len(pstTimes)):
        if pstTimes[i].day == 31:
            pstTimes[i] = pstTimes[i]+timedelta(days=1)
    if timeRange != None:
        newVals = []
        newPstTimes = []
        for i in range(len(pstTimes)):
            date = pstTimes[i]
            if timeRange[0] < date and date < timeRange[1]:
                newVals.append(pm[i])
                newPstTimes.append(dateToMinutes(timeRange[0], date))
        return (newPstTimes, newVals)
    rounds = []
    for _ in range(5):
        rounds.append([[], []])
    for i in range(len(pstTimes)):
        date = pstTimes[i]
        if R1[0] < date and date < R1[1]:
            rounds[0][0].append(pm[i])
            rounds[0][1].append(dateToMinutes(R1[0], date))
        elif R2[0] < date and date < R2[1]:
            rounds[1][0].append(pm[i])
            rounds[1][1].append(dateToMinutes(R2[0], date))
        elif R3[0] < date and date < R3[1]:
            rounds[2][0].append(pm[i])
            rounds[2][1].append(dateToMinutes(R3[0], date))
        elif R4[0] < date and date < R4[1]:
            rounds[3][0].append(pm[i])
            rounds[3][1].append(dateToMinutes(R4[0], date))
    return rounds

S1R = purple_air(S1)
S2R = purple_air(S2)
S3R = purple_air(S3)
S4R = purple_air(S4)

def subtract(xR, yR):
    f = interpolate.interp1d(yR[1], yR[0], fill_value='extrapolate')
    yInterp = f(xR[1])
    return [a - b for a, b in zip(xR[0], yInterp)]

def subtractTest():
    plt.plot(S1R[0][1], S1R[0][0])
    testY = [[x+100 for x in S1R[0][0]], [y+4 for y in S1R[0][1]]]
    plt.plot(testY[1], testY[0])
    plt.plot(S1R[0][1], subtract(S1R[0], testY))
    plt.show()

def divide(xR, yR):
    f = interpolate.interp1d(yR[1], yR[0], fill_value='extrapolate')
    yInterp = f(xR[1])
    return [a / b for a, b in zip(xR[0], yInterp)]

def testPlot():
    plt.plot(S1R[2][1], S1R[2][0])
    plt.plot(S3R[2][1], S3R[2][0])
    plt.plot(S4R[2][1], S4R[2][0])
    plt.legend(["1", "3", "4"])
    plt.show()

def s2_ratios():
    r2s2sub = [subtract(S2R[1], S4R[1]), S2R[1][1]]
    r2s1sub = [subtract(S1R[1], S4R[1]), S1R[1][1]]
    r2div = divide(r2s2sub, r2s1sub)
    plt.plot(S2R[1][1], r2div)

    r3s2sub = [subtract(S2R[2], S4R[2]), S2R[2][1]]
    r3s1sub = [subtract(S1R[2], S4R[2]), S1R[2][1]]
    r3div = divide(r3s2sub, r3s1sub)
    plt.plot(S2R[2][1], r3div)

    r4s2sub = [subtract(S2R[3], S4R[3]), S2R[3][1]]
    r4s1sub = [subtract(S1R[3], S4R[3]), S1R[3][1]]
    r4div = divide(r4s2sub, r4s1sub)
    plt.plot(S2R[3][1], r4div)

    plt.legend(["Round 2 (2 ft)", "Round 3 (6 ft)", "Round 4 (10 ft)"])
    plt.show()

def s3_ratios():
    r2s3sub = [subtract(S3R[1], S4R[1]), S3R[1][1]]
    r2s1sub = [subtract(S1R[1], S4R[1]), S1R[1][1]]
    r2div = divide(r2s3sub, r2s1sub)
    plt.plot(S3R[1][1], r2div)

    r3s3sub = [subtract(S3R[2], S4R[2]), S3R[2][1]]
    r3s1sub = [subtract(S1R[2], S4R[2]), S1R[2][1]]
    r3div = divide(r3s3sub, r3s1sub)
    plt.plot(S3R[2][1], r3div)

    r4s3sub = [subtract(S3R[3], S4R[3]), S3R[3][1]]
    r4s1sub = [subtract(S1R[3], S4R[3]), S1R[3][1]]
    r4div = divide(r4s3sub, r4s1sub)
    plt.plot(S3R[3][1], r4div)

    plt.legend(["Round 2 (4 ft)", "Round 3 (8 ft)", "Round 4 (12 ft)"])
    plt.show()

def aero(filename, param, plot=True, timeRange=None):
    df = pd.read_csv(filename)
    vals = df[param].tolist()
    times = [x[-5:] for x in df["Time"].tolist()]
    dates = [datetime.strptime(x, "%H:%M") for x in times]
    pstTimes = [x.replace(tzinfo=timezone('US/Pacific')) for x in dates]
    for i in range(len(pstTimes)):
        if pstTimes[i].day == 31:
            pstTimes[i] = pstTimes[i]+timedelta(days=1)
    if timeRange != None:
        newVals = []
        newPstTimes = []
        for i in range(len(pstTimes)):
            date = pstTimes[i]
            if timeRange[0] < date and date < timeRange[1]:
                newVals.append(vals[i])
                newPstTimes.append(dateToMinutes(timeRange[0], date))
        vals = newVals
        pstTimes = newPstTimes
    else:
        pstTimes = [dateToMinutes(GLOBAL_START, x) for x in pstTimes]
    if plot:
        plt.plot(pstTimes, vals)
    return pstTimes, vals

def fig1():
    """ Plots PM2.5 levels over the entire experiment for each PurpleAir and AQY sensor """
    plt.plot(S1F[1], S1F[0])
    plt.plot(S2F[1], S2F[0])
    plt.plot(S4F[1], S4F[0])
    aero(AERO_EXHAUST, "PM2.5 (µg/m³)")
    aero(AERO_DISTANT, "PM2.5 (µg/m³)")
    addTimeLines(GLOBAL_START)
    plt.legend(["PurpleAir 1", "PurpleAir 2", "PurpleAir 4", "Aeroqual Exhaust", "Aeroqual Distant"])
    plt.xlabel("Time [mins]")
    plt.ylabel("PM$_{2.5}$ Concentration [$\mu$g/m$^3$]")
    plt.title("PM$_{2.5}$ Measurements")
    plt.show()

def fig2():
    """ Plots NO2 levels over the entire experiment for each AQY sensor """
    aero(AERO_EXHAUST, "NO2 (ppb)")
    aero(AERO_DISTANT, "NO2 (ppb)")
    addTimeLines(GLOBAL_START)
    plt.legend(["Exhaust", "Distant"])
    plt.title("Aeroqual NO2 Measurements")
    plt.xlabel("Time [mins]")
    plt.ylabel("NO2 Concentration [ppb]")
    plt.show()

def fig3():
    """ Plots O3 levels over the entire experiment for each AQY sensor """
    aero(AERO_EXHAUST, "O3 (ppb)")
    aero(AERO_DISTANT, "O3 (ppb)")
    addTimeLines(GLOBAL_START)
    plt.legend(["Exhaust", "Distant"])
    plt.title("Aeroqual O3 Measurements")
    plt.xlabel("Time [mins]")
    plt.ylabel("O3 Concentration [ppb]")
    plt.show()

def fig4():
    """ Plots PM2.5 measurements for sensors 1 and 4 during round 2 """
    fig, ax = plt.subplots()
    S1X, S1Y = purple_air(S1, R2_RANGE)
    S4X, S4Y = purple_air(S4, R2_RANGE)
    plt.plot(S1X, S1Y)
    plt.plot(S4X, S4Y)
    ax.set_ylim(-20, 200)
    addGray(ax, R2_RANGE[0], [2])
    plt.legend(["1 ft from vehicle", "30 ft from vehicle"])
    plt.xlabel("Time [mins]")
    plt.ylabel("PM$_{2.5}$ Concentration [$\mu$g/m$^3$]")
    plt.title("PM$_{2.5}$ by Distance")
    plt.show()

def addTimeLines(start, rounds = [1, 2, 3, 4]):
    for i in rounds:
        plt.axvline(x=dateToMinutes(start, round_list[i-1][0]), color=(1, 0, 0))
        plt.axvline(x=dateToMinutes(start, round_list[i-1][1]), color=(0, 0, 1))

def addGray(ax, start, rounds = [1, 2, 3, 4]):
    for i in rounds:
        ax.axvspan(dateToMinutes(start, round_list[i-1][0]), dateToMinutes(start, round_list[i-1][1]), alpha=0.2, color='gray')

def getInterpPoints(x1, y1, x2, y2, numPoints):
    """ Outputs numPoints interpolated points from [x1, x2) """
    Xs = []
    for i in range(numPoints):
        newX = x1 + (i * (x2-x1) / numPoints)
        Xs.append(newX)
    Ys = []
    f = interpolate.interp1d([x1, x2], [y1, y2], fill_value='extrapolate')
    for x in Xs:
        Ys.append(f(x).item())
    return Xs, Ys

def animate(framerate=60, speedMultiplier=2):
    """ Generates an animation of NO2 concentration over time for both AQY sensors """
    plt.rcParams['animation.ffmpeg_path'] = 'C:\\ffmpeg\\bin\\ffmpeg.exe'

    fig, ax = plt.subplots()
    xdata, ydata = [], []
    ln, = plt.plot([], [], color=(0, 0, 0))

    size = 15
    fig.set_size_inches(size, size/1.777)

    plt.ylabel("NO$_2$ Concentration [ppb]")
    plt.xlabel("Time [mins]")
    plt.title("NO$_{2}$ Concentration Over Time")

    locs1, vals1 = aero(AERO_EXHAUST, "NO2 (ppb)", False, R1)
    locs2, vals2 = aero(AERO_DISTANT, "NO2 (ppb)", False, R1)

    dataPreInterp = [[locs1, vals1], [locs2, vals2]]
    data = []

    for line in dataPreInterp:
        Xs, Ys = [], []
        for i in range(len(line[0])-1):
            interp = getInterpPoints(line[0][i], line[1][i], line[0][i+1], line[1][i+1], framerate)
            Xs.extend(interp[0])
            Ys.extend(interp[1])
        Xs.append(line[0][-1])
        Ys.append(line[1][-1])
        data.append([Xs, Ys])
    
    xyData = [[[], []], [[], []]]

    colors = [(0.796875, 0.14453125, 0.16015625), (0.22265625, 0.4140625, 0.69140625)]
    
    lines = []
    for index in range(len(data)):
        lobj = ax.plot([],[],lw=2,color=colors[index])[0]
        lines.append(lobj)
    
    def initTest():
        ax.set_xlim(-20, len(locs1)+10)
        ax.set_ylim(-10, 100)
        return ln,
    
    def frameTest(i):
        xdata.append(data[0][0][i])
        ydata.append(data[0][1][i])
        ln.set_data(xdata, ydata)
        return ln,
    
    def init():
        ax.set_xlim(-2, len(locs1)+2)
        ax.set_ylim(-2, 80)
        for line in lines:
            line.set_data([],[])
        legend = plt.legend(["1 ft from vehicle", "30 ft from vehicle"], loc="upper left")
        for i in range(len(data)):
            legend.legendHandles[i].set_color(colors[i])
        return lines

    def frame(i):
        for n in range(len(data)):
            if i < len(data[n][0]) and i < len(data[n][1]):
                xyData[n][0].append(data[n][0][i])
                xyData[n][1].append(data[n][1][i])
        for n in range(len(lines)):
            if i < len(data[n][0]) and i < len(data[n][1]):
                lines[n].set_data(xyData[n][0], xyData[n][1])
        legend = plt.legend(["1 ft from vehicle", "30 ft from vehicle"], loc="upper left")
        for i in range(len(data)):
            legend.legendHandles[i].set_color(colors[i])
        return lines + [legend]
    
    anim = animation.FuncAnimation(fig, frame, init_func=init,
                                frames=len(data[0][0]), interval=20, blit=True)
    
    FFMpegWriter = animation.writers['ffmpeg']
    writer = FFMpegWriter(fps=framerate*speedMultiplier, metadata=dict(artist='Me'), bitrate=1800)
    
    anim.save('basic_animation_exp4.mp4', writer=writer)

def main():
    fig1()

if __name__ == "__main__":
    main()