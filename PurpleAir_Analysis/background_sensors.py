###
# Helper functions for handling background sensor data. Used in purple_data.py
###

import pandas as pd
import matplotlib.pyplot as plt
import statistics

def organizeDays(vals, times):
    dayDict = {}
    for i in range(len(times)):
        time = times[i]
        time = time.split()
        day = int(time[0][-2:])
        hour = int(time[1][:2])
        minute = int(time[1][3:5])
        pstHour = hour - 7
        if pstHour < 0:
            day -= 1
            pstHour += 24
        pstTime = pstHour + minute / 60
        if day not in dayDict:
            dayDict[day] = [[pstTime], [vals[i]]]
        else:
            dayDict[day][0].append(pstTime)
            dayDict[day][1].append(vals[i])
    return dayDict

def sensor_signal(name, param, days, disjoint = True):
    df_A = pd.read_csv("pilot_background/"+name+"_A_Primary.csv")
    df_B = pd.read_csv("pilot_background/"+name+"_B_Primary.csv")
    if param not in df_A.columns:
        df_A = pd.read_csv("pilot_background/"+name+"_A_Secondary.csv")
        df_B = pd.read_csv("pilot_background/"+name+"_B_Secondary.csv")
    
    times = df_A["created_at"].tolist()
    vals = df_A[param].tolist()
    vals_B = df_B[param].tolist()
    for i in range(len(vals_B)):
        try:
            vals[i] = (vals[i] + vals_B[i]) / 2
        except IndexError:
            pass
    
    dayDict = organizeDays(vals, times)
    if disjoint:
        output = []
        for day in days:
            output.append([dayDict[day][0], dayDict[day][1]])
    else:
        output = [[], []]
        for day in days:
            output[0].extend(dayDict[day][0])
            output[1].extend(dayDict[day][1])
    return output

def get_signals(names, param, days):
    output = []
    for name in names:
        output.append(sensor_signal(name, param, days, False))
    return output

def align_signals(signals):
    lens = [len(x[1]) for x in signals]
    min_length = min(lens)
    output = []
    for signal in signals:
        output.append([signal[0][:min_length], signal[1][:min_length]])
    return output

def average_signals(signals):
    avg_signal = signals[0]
    for signal in signals[1:]:
        avg_signal = [x+y for x, y in zip(avg_signal, signal)]
    avg_signal = [x/len(signals) for x in avg_signal]
    return avg_signal

def median_signals(signals):
    med_signal = []
    for i in range(len(signals[0])):
        vals = [x[i] for x in signals]
        med_signal.append(statistics.median(vals))
    return med_signal

def subtract_signals(first, second):
    """ first - second """
    return [x-y for x, y in zip(first, second)]