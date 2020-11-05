###
# Script for handling uploaded AQY data stored in multiple csvs
###

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import os
from datetime import datetime
from datetime import timedelta
from pytz import timezone
from scipy import interpolate

# Set GLOBAL_START to be the time of the chronologically first data point
GLOBAL_START = datetime.strptime("3/20/2020 10:04", "%m/%d/%Y %H:%M")

PARAMS = {"pm":"PM2.5 (µg/m³)", "no2":"NO2 (ppb)", "o3":"O3 (ppb)"}

def time_minus_start(time):
    """ Returns the decimal number of days since the GLOBAL_START time """
    delta = time - GLOBAL_START
    secs = delta.total_seconds()
    return secs/86400 # days since global start time

def get_data(param):
    """ Fetches data from every csv in data directory (the names are irrelevant). Converts times 
    to datetime objects, returning the parameter values and corresponding times sorted chronologically, 
    where the times are the decimal number of days since the GLOBAL_START time """
    files = os.listdir("data")
    overall_pm = []
    overall_times = []
    for f in files:
        try:
            df = pd.read_csv("data/"+f, skiprows=6)
            df = df[df[PARAMS[param]].notna()]
        except: # some files have an abnormal layout
            df = pd.read_csv("data/"+f, skiprows=0)
            df = df[df[PARAMS[param]].notna()]
        pm = df[PARAMS[param]].tolist()
        table_times = df["Time"].tolist()
        if len(table_times[0]) == 19:
            times = [datetime.strptime(x, "%Y/%m/%d %H:%M:%S") for x in table_times]
        else: # abnormal time representation
            times = [datetime.strptime(x, "%m/%d/%Y %H:%M") for x in table_times]
        days_since_start = [time_minus_start(x) for x in times]
        overall_pm += pm
        overall_times += days_since_start
    overall_times, overall_pm = zip(*sorted(zip(overall_times, overall_pm)))
    return overall_pm, overall_times

def plot_pm():
    """ Plots PM2.5 levels for the sensor by days since GLOBAL_START """
    fig, ax = plt.subplots()
    pm, times = get_data("pm")
    plt.scatter(times, pm, s=4)
    ax.set_ylim(-4, 35)
    plt.xlabel("Time [days]")
    plt.ylabel("Concentration [$\mu$g/m$^3$]")
    plt.title("AQY PM$_{2.5}$ Measurements March 20 - April 21")
    plt.show()

def plot_no2_o3():
    """ Plots NO2 and O3 levels for the sensor by days since GLOBAL_START """
    no2, times = get_data("no2")
    plt.scatter(times, no2, s=4)
    o3, times = get_data("o3")
    plt.scatter(times, o3, s=4)
    plt.legend(["NO$_2$", "O$_3$"])
    plt.xlabel("Time [days]")
    plt.ylabel("Concentration [ppb]")
    plt.title("AQY NO$_2$ and O$_3$ Measurements March 20 - April 21")
    plt.show()

def plot_no2_plus_o3():
    """ Plots NO2 and O3 levels added together for the sensor by days since GLOBAL_START """
    no2, times1 = get_data("no2")
    o3, times2 = get_data("o3")
    i = 0
    j = 0
    sums = []
    sums_times = []
    while i < len(times1) and j < len(times2):
        if times1[i] == times2[j]:
            sums.append(no2[i] + o3[j])
            sums_times.append(times1[i])
            i += 1
            j += 1
        elif times1[i] < times2[j]:
            i += 1
        else:
            j += 1
    plt.scatter(sums_times, sums, s=4)
    plt.xlabel("Time [days]")
    plt.ylabel("Concentration [ppb]")
    plt.title("AQY NO$_2$+O$_3$ Total March 20 - April 21")
    plt.show()

if __name__ == "__main__":
    plot_no2_plus_o3()