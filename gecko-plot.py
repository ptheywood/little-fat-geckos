#! /usr/bin/python3

import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.dates as mdates
from pandas.plotting import register_matplotlib_converters
import os
import sys
from distutils.util import strtobool


DEFAULT_DPI = 96
EXT_PDF = "pdf"
EXT_PNG = "png"

MARKERS=["H", "s", "^", "p", "X", "P"]
LINES=["-", "--", ":"]

def ith(lst, i):
    return lst[i % len(lst)]

def user_yes_no_query(question):
    # http://stackoverflow.com/questions/3041986/python-command-line-yes-no-input
    sys.stdout.write('%s [y/n]\n' % question)
    while True:
        try:
            return strtobool(input().lower())
        except ValueError:
            sys.stdout.write('Please respond with \'y\' or \'n\'.\n')

def file_overwrite_check(f):
    """ Return if it is safe to write to the target file, potentially after user involvement
    """
    if os.path.exists(f):
        if os.path.isfile(f):
            overwrite = user_yes_no_query("The file {:} exists, do you wish to overwrite?".format(f))
            return overwrite
        else:
            return False
    else:
        return True

def show_or_save(filepath, dpi, force):
    if filepath is None:
        plt.show()
    else:
        # Save the file
        if force or file_overwrite_check(filepath):
            plt.savefig(filepath, dpi=dpi)
            print("Figure saved as {:}".format(filepath))
        else:
            print("Warning: Protected file {:}. Figure not saved.".format(filepath))

def command_line_args():

    parser = argparse.ArgumentParser(
        description="Tool for plotting the fatness of geckos"
    )
    parser.add_argument(
        "-i",
        "--input",
        type=str,
        nargs=1,
        # nargs="+",
        help="Input CSV files to parse",
        required=True
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="Path to file for saving."
    )
    parser.add_argument(
        "-g",
        "--geckos",
        type=str,
        nargs="+",
        help="Names of geckos to be output",
    )
    parser.add_argument(
        "--dpi",
        type=int,
        help="DPI for output files",
        default=DEFAULT_DPI
    )
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Flag to force overwrite of files"
    )

    args = parser.parse_args()
    return args


def load_data(csv):
    raw_df = pd.read_csv(csv, parse_dates=["date"])
    raw_df = raw_df.rename(columns=lambda x: x.strip())

    # Strip the names
    raw_df["gecko"] = raw_df["gecko"].map(str.strip)

    return raw_df


def geckos_to_plot(df, gecko_whitelist):
    # Find the geckos in the dataset. 
    geckos = df["gecko"].unique()

    # Find which geckos should be plot.
    if gecko_whitelist is not None and len(gecko_whitelist) > 0:
        geckos_to_plot = []
        # For each gecko in the whitelist
        for gecko in gecko_whitelist:
            # If the gecko exists, add it to the ordered list of geckos to plot.
            if gecko in geckos:
                geckos_to_plot.append(gecko)
        geckos = geckos_to_plot

    return geckos

def generate_per_gecko_dataframe(raw_df, geckos):
    # Build a data frame for each valid gecko.
    gecko_dfs = {}
    for gecko in geckos:
        gecko_dfs[gecko] = raw_df.query("gecko == '{:}'".format(gecko))
    return gecko_dfs


def plot(gecko_dfs, output, dpi, force):
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

    # Plot a series for each valid gecko
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

    # Set the figure title
    plt.title("Gecko Fatness")

    # Add a legend
    ax.legend(
        loc="lower right",
        title="Gecko", 
        shadow=True, 
        ncol=1
    )

    # Remove top/right spines
    sns.despine()

    # Make good use of space
    plt.tight_layout()

    # format the ticks for dates
    ax.xaxis.set_major_locator(years)
    ax.xaxis.set_major_formatter(yearsFmt)
    ax.xaxis.set_minor_locator(months)

    # round to nearest years...
    raw_datemin = min([df[xcol].min() for df in gecko_dfs.values()])
    raw_datemax = max([df[xcol].max() for df in gecko_dfs.values()])

    datemin = np.datetime64(raw_datemin, 'Y')
    datemax = np.datetime64(raw_datemax, 'Y') + np.timedelta64(1, 'Y')
    ax.set_xlim(datemin, datemax)

    ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')
    ax.grid(True)

    # rotates and right aligns the x labels, and moves the bottom of the
    # axes up to make room for them
    fig.autofmt_xdate()

    # Set axis limits.
    ax.set_ylim(bottom=0)

    # Either show or save the output figure.
    show_or_save(output, dpi, force)


def main():
    args = command_line_args()

    # Load the CSV into a dataframe
    raw_df = load_data(args.input[0])

    
    # Get the names of geckos to plot
    geckos = geckos_to_plot(raw_df, args.geckos)

    if len(geckos) ==  0:
        print("Error: No valid geckos specified")
        return

    
    # Get a dataframe per gecko
    gecko_dfs = generate_per_gecko_dataframe(raw_df, geckos)


    # Plot the data
    plot(
        gecko_dfs, 
        args.output, 
        args.dpi, 
        args.force
    )

    

if __name__ == "__main__":
    main()
