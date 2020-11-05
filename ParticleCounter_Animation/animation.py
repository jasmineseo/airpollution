###
# Script for plotting and animating data from Prof. Hawkins's particle counter
###

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation

START_TIME = "15:18:13"
END_TIME = "15:36:55"

def extract(param):
    df = pd.read_csv("counter_data.csv")
    vals = list(df[param].values)
    times = list(df["HR:MN:SC"].values)
    for i in range(len(times)):
        if times[i] == START_TIME:
            vals = vals[i:]
            times = times[i:]
            break
    for i in range(len(times)):
        if times[i] == END_TIME:
            vals = vals[:i+1]
            times = times[:i+1]
            break
    return vals, times

def getTicksAndTimes(rawTimes, interval = 180):
    ticks = list(range(0, len(rawTimes), 180))
    times = []
    for i in range(0, len(rawTimes), 180):
        times.append(rawTimes[i])
    return ticks, times

def plot(param):
    """ Plots the data for the specified parameter """
    vals, rawTimes = extract(param)
    locs = list(range(len(vals)))
    ticks, times = getTicksAndTimes(rawTimes, 180)
    plt.xticks(ticks, times)

    plt.ylabel("Concentration [particles$/cm^3$]")
    plt.xlabel("Time [min]")
    plt.title("PM$_{0.007}$ - PM$_{2.0}$ Concentration")

    plt.plot(locs, vals)
    plt.show()

def animate(param):
    """ Generates an animation of the specified parameter over time """
    plt.rcParams['animation.ffmpeg_path'] = 'C:\\ffmpeg\\bin\\ffmpeg.exe'

    fig, ax = plt.subplots()
    xdata, ydata = [], []
    ln, = plt.plot([], [], color=(0, 0, 0))

    size = 15
    fig.set_size_inches(size, size/1.777)

    plt.ylabel("Particles Per Cubic Centimeter")
    plt.xlabel("Seconds")
    plt.title("PM$_{0.007}$ - PM$_{2.0}$ Concentration")

    vals, rawTimes = extract(param)
    locs = list(range(len(vals)))

    def init():
        ax.set_xlim(-20, len(vals)+175)
        ax.set_ylim(9000, 14000)
        return ln,

    def frame(i):
        xdata.append(locs[i])
        ydata.append(vals[i])
        ln.set_data(xdata, ydata)
        return ln,
    
    anim = animation.FuncAnimation(fig, frame, init_func=init,
                                frames=len(vals), interval=20, blit=True)
    
    FFMpegWriter = animation.writers['ffmpeg']
    writer = FFMpegWriter(fps=51, metadata=dict(artist='Me'), bitrate=1800)
    
    anim.save('basic_animation.mp4', writer=writer)

if __name__ == "__main__":
    plot("concent")