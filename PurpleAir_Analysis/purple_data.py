###
# Script for handling data from a PurpleAir sensor while taking into account the
# a and b channels (more info about this and about the outputs of this script are
# in pilot_analysis.pdf). Allows for comparison with the average and median of the
# signals of multiple "background" sensors, the data for which were obtained from
# the PurpleAir website
###

import pandas as pd
import matplotlib.pyplot as plt
import statistics
import background_sensors
import numpy as np

BACKGROUND_SENSOR_NAMES = ["01", "AQMD", "AQMD48", "Bike", "NW", "Piedmond"]

def relativeHours(times, minDay):
    hours = []
    for time in times:
        try:
            tIndex = time.find("T")
            day = int(time[tIndex-2:tIndex])
            hour = int(time[tIndex+1:tIndex+3])
            minute = int(time[tIndex+4:tIndex+6])
            utcHour = (day-minDay)*24 + hour + minute / 60
            pstHour = utcHour + 17
            pstHour = pstHour % 24
            hours.append(pstHour)
        except AttributeError:
            hours.append(hours[-1])
    return hours

def organizeDays(vals, times):
    dayDict = {}
    for i in range(len(times)):
        time = times[i]
        tIndex = time.find("T")
        day = int(time[tIndex-2:tIndex])
        hour = int(time[tIndex+1:tIndex+3])
        minute = int(time[tIndex+4:tIndex+6])
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

def overlayData(param, days, option = "NA", interval = 2):
    vals = []
    times = []
    for i in range(days[0], days[-1]+2):
        df = pd.read_csv("pilot/201910"+str(i)+".csv")
        a_channel = list(df[param].values)
        if option == "average":
            b_channel = list(df[param+"_b"].values)
            avg = []
            for i in range(len(a_channel)):
                avg.append((a_channel[i] + b_channel[i]) / 2)
            vals.extend(avg)
        else:
            vals.extend(a_channel)
        times.extend(list(df["UTCDateTime"].values))
    
    dayDict = organizeDays(vals, times)
    for day in days:
        plotData(dayDict[day][1], dayDict[day][0], interval)
    plt.legend(days, loc="upper right")

def combineData(param, combine, days, option = "NA", interval = 2):
    vals = []
    times = []
    for i in range(days[0], days[-1]+2):
        df = pd.read_csv("pilot/201910"+str(i)+".csv")
        a_channel = list(df[param].values)
        if option == "average":
            b_channel = list(df[param+"_b"].values)
            avg = []
            for i in range(len(a_channel)):
                avg.append((a_channel[i] + b_channel[i]) / 2)
            vals.extend(avg)
        else:
            vals.extend(a_channel)
        times.extend(list(df["UTCDateTime"].values))

    dayDict = organizeDays(vals, times)
    if combine == "average":
        vals = dayDict[days[0]][1]
        times = dayDict[days[0]][0]
        for day in days[1:]:
            vals = [a+b for a,b in zip(vals, dayDict[day][1])]
        numDays = len(days)
        vals = [x/numDays for x in vals]
    elif combine == "median":
        vals = []
        times = dayDict[days[0]][0]
        for i in range(len(times)):
            valsToMedian = []
            for day in days:
                valsToMedian.append(dayDict[day][1][i])
            vals.append(statistics.median(valsToMedian))
    plotData(vals, times, interval)

def allData(param, days, option = "NA", interval = 6, plot = True, trend = False, color = None):
    vals = []
    times = []
    for i in range(days[0], days[-1]+2):
        df = pd.read_csv("pilot/201910"+str(i)+".csv")
        a_channel = list(df[param].values)
        if option == "average":
            b_channel = list(df[param+"_b"].values)
            avg = []
            for i in range(len(a_channel)):
                avg.append((a_channel[i] + b_channel[i]) / 2)
            vals.extend(avg)
        else:
            vals.extend(a_channel)
        times.extend(list(df["UTCDateTime"].values))
    
    dayDict = organizeDays(vals, times)
    allVals = []
    allTimes = []
    for day in days:
        allVals.extend(dayDict[day][1])
        allTimes.extend(dayDict[day][0])
    if plot:
        plotData(allVals, allTimes, interval, color)
        if trend:
            z = np.polyfit(list(range(len(allVals))), allVals, 10)
            p = np.poly1d(z)
            plt.plot(list(range(len(allVals))),p(list(range(len(allVals)))),"r--")
    return allVals, allTimes

def relevantHours(locs, hours, interval = 4):
    ticks = []
    evenHours = []
    for i in range(len(hours)):
        loc = locs[i]
        hour = hours[i]
        if hour % interval < .017:
            ticks.append(loc)
            evenHours.append(str(int(hour)))
    return ticks, evenHours

def plotData(vals, hours, interval = 4, color = None):
    """ Helper function for plotting data, where vals are the data values and hours
    are the fractional hours since the start of data collection. Hour ticks are placed
    at interval hours apart """
    locs = list(range(len(vals)))
    ticks, evenHours = relevantHours(locs, hours, interval)
    plt.xticks(ticks, evenHours)
    if color == None:
        plt.plot(locs, vals)
    else:
        plt.plot(locs, vals, color)

def plotSensor(name, param, days, interval = 6):
    """ Helper function for plotting data for a sensor on the specified days """
    outputs = background_sensors.get_signals([name], param, days)[0]
    plotData(outputs[1], outputs[0], interval)

def combineBackground(param, days, combine = "average"):
    """ Get the average or median of the background signals for the given parameter
    on the specified days """
    outputs = background_sensors.get_signals(BACKGROUND_SENSOR_NAMES, param, days)
    outputs = background_sensors.align_signals(outputs)
    signals = [x[1] for x in outputs]
    if combine == "average":
        return (background_sensors.average_signals(signals), outputs[0][0])
    elif combine == "median":
        return (background_sensors.median_signals(signals), outputs[0][0])

def plotBackground(param, days, combine = "average", interval = 6, color=None):
    vals, times = combineBackground(param, days, combine)
    plotData(vals, times, interval, color)

def plotSensorsAndAverage():
    plotBackground("PM2.5_CF1_ug/m3", [12], "average", 2)
    for name in BACKGROUND_SENSOR_NAMES:
        plotSensor(name, "PM2.5_CF1_ug/m3", [12], 2)
    plt.legend(["Average"]+BACKGROUND_SENSOR_NAMES)
    plt.show()

def plotSensorsAndMedian():
    plotBackground("PM2.5_CF1_ug/m3", [12], "median", 2)
    for name in BACKGROUND_SENSOR_NAMES:
        plotSensor(name, "PM2.5_CF1_ug/m3", [12], 2)
    plt.legend(["Average"]+BACKGROUND_SENSOR_NAMES)
    plt.show()

def plotBackgroundMedAndPilot():
    """ Figure 3. Plots the median of the background signals against the pilot sensor signal """
    plotBackground("PM2.5_ATM_ug/m3", list(range(10, 22)), "median", 6, color="#009933")
    allData("pm2_5_atm", list(range(10, 22)), "average", 6, color="#00004d")
    plt.legend(["Background Median", "Pilot Sensor"])
    plt.title("PM$_{2.5}$ Pilot Sensor vs Median Background Data (Oct 10th-21st)")
    plt.ylabel("PM$_{2.5}$ Concentration [$\mu$g/m$^3$]")
    plt.xlabel("Time [hour]")
    for i in range(12):
        plt.axvline(x=722*i+240, color=(1, 0, 0))
        plt.axvline(x=722*i+435, color=(0, 0, 1))
    plt.show()

def plotBackMedAndPilotDifference():
    """ Figure 4 """
    med_signal, times = combineBackground("PM2.5_ATM_ug/m3", list(range(10, 22)), "median")
    pilot_signal, pilot_times = allData("pm2_5_atm", list(range(10, 22)), "average", 6, False)
    minLength = min(len(med_signal), len(pilot_signal))
    med_signal = med_signal[:minLength]
    times = times[:minLength]
    pilot_signal = pilot_signal[:minLength]
    diff_signal = background_sensors.subtract_signals(pilot_signal, med_signal)
    plotData(diff_signal, times, 6, color="#00004d")
    plt.title("PM$_{2.5}$ Pilot Minus Median Background (Oct 10th-21st)")
    plt.ylabel("Difference in PM$_{2.5}$ Concentration [$\mu$g/m$^3$]")
    plt.xlabel("Time [hour]")
    for i in range(12):
        plt.axvline(x=722*i+240, color=(1, 0, 0))
        plt.axvline(x=722*i+435, color=(0, 0, 1))
    plt.show()

def avgDiffTimeRange(start, end, days):
    med_signal, times = combineBackground("PM2.5_CF1_ug/m3", days, "median")
    pilot_signal, pilot_times = allData("pm2_5_cf_1", days, "average", 6, False)
    minLength = min(len(med_signal), len(pilot_signal))
    med_signal = med_signal[:minLength]
    times = times[:minLength]
    pilot_signal = pilot_signal[:minLength]
    diff_signal = background_sensors.subtract_signals(pilot_signal, med_signal)
    relevantVals = []
    for i in range(len(times)):
        if (times[i] >= start) and (times[i] <= end):
            relevantVals.append(diff_signal[i])
    print(statistics.mean(relevantVals))

def pilotWithTrend():
    """ Figure 1. Plots the pilot sensor data with a trendline """
    allData("pm2_5_atm", list(range(10, 22)), "average", 6, True, trend=True, color="#00004d")
    plt.title("PM$_{2.5}$ Pilot Sensor (Oct 10th-21st)")
    plt.ylabel("PM$_{2.5}$ Concentration [$\mu$g/m$^3$]")
    plt.xlabel("Time [hour]")
    for i in range(12):
        plt.axvline(x=722*i+240, color=(1, 0, 0))
        plt.axvline(x=722*i+435, color=(0, 0, 1))
    plt.show()

def weekendWeekdays():
    """ Figure 2. Plots the average and median signals for weekends versus non-Wednesday weekdays """
    combineData("pm2_5_atm", "average", [10, 11, 14, 15, 17, 18, 21], "average")
    combineData("pm2_5_atm", "median", [10, 11, 14, 15, 17, 18, 21], "average")
    combineData("pm2_5_atm", "average", [12, 13, 19, 20], "average")
    combineData("pm2_5_atm", "median", [12, 13, 19, 20], "average")
    plt.legend(["Non-Wed Weekdays Average", "Non-Wed Weekdays Median", "Weekends Average", "Weekends Median"])
    plt.title("Pilot Sensor Non-Wed Weekdays vs Weekends (Oct 10th-21st)")
    plt.ylabel("PM$_{2.5}$ Concentration [$\mu$g/m$_3$]")
    plt.xlabel("Time [hour]")

    plt.axvline(x=235, color=(1, 0, 0))
    plt.axvline(x=245, color=(1, 0, 0))
    plt.axvline(x=430, color=(0, 0, 1))
    plt.axvline(x=450, color=(0, 0, 1))
    plt.show()

def main():
    #avgDiffTimeRange(7.5, 8.5, [10, 11, 14, 15, 16, 17, 18, 21])
    pilotWithTrend()

if __name__ == "__main__":
    main()