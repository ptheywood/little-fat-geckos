#! /usr/bin/python3

import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.dates as mdates
from pandas.plotting import register_matplotlib_converters


CSV_FILE="geckos.csv"


series_to_plot=[
    "murphey",
    "bojack",
    "lu"
]

MARKERS=["H", "s", "^", "p", "X", "P"]
LINES=["-", "--", ":"]

def ith(lst, i):
    return lst[i % len(lst)]



def main():
    # @todo argparse

    # Load the CSV
    raw_df = pd.read_csv(CSV_FILE, parse_dates=["date"])
    raw_df = raw_df.rename(columns=lambda x: x.strip())

    # Strip the names
    raw_df["gecko"] = raw_df["gecko"].map(str.strip)

    # Find the geckos in the dataset. 
    geckos = raw_df["gecko"].unique()

    # Build a data frame for each gecko.
    gecko_dfs = {}
    for gecko in geckos:
        gecko_dfs[gecko] = raw_df.query("gecko == '{:}'".format(gecko))
        # print(gecko)
        # print(gecko_dfs[gecko])





    # Prepare some stuff for plotting.
    sns.set()
    sns.set_style("whitegrid")
    sns.set_context(
        # "notebook", 
        "talk",
        font_scale=1.5, 
        rc={"lines.linewidth": 2.5}
    )

    sns.set_palette(sns.color_palette("husl", 3))

    register_matplotlib_converters()
    years = mdates.YearLocator()   # every year
    months = mdates.MonthLocator()  # every month
    yearsFmt = mdates.DateFormatter('%Y')

    # Create a figure
    fig, ax = plt.subplots(
        figsize=(16, 9),
    )


    xcol = "date"
    ycol = "mass"

    # Plot each series
    i = 0
    for gecko, df in gecko_dfs.items():
        ax.plot(
            df[xcol], 
            df[ycol],
            marker=ith(MARKERS, i),
            linestyle=ith(LINES,i),
            label=gecko,
        )
        i+=1


    plt.title("Gecko Fatness")

    ax.legend(
        loc="lower right",
        title="Gecko", 
        shadow=True, 
        ncol=1
    )

    plt.tight_layout()

    sns.despine()



    # format the ticks
    ax.xaxis.set_major_locator(years)
    ax.xaxis.set_major_formatter(yearsFmt)
    ax.xaxis.set_minor_locator(months)

    # round to nearest years...
    datemin = np.datetime64(raw_df[xcol][0], 'Y')
    datemax = np.datetime64(raw_df[xcol].iloc[-1], 'Y') + np.timedelta64(1, 'Y')
    ax.set_xlim(datemin, datemax)

    ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')
    ax.grid(True)

    # rotates and right aligns the x labels, and moves the bottom of the
    # axes up to make room for them
    fig.autofmt_xdate()

    ax.set_ylim(bottom=0)

    plt.show()

if __name__ == "__main__":
    main()
