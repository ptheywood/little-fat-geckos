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
import itertools


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
        nargs="+",
        action="append",
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

def get_gecko_name(csv):
    # get the file name without extension from the path. Assume this is the geckos name.
    name = os.path.basename(csv)
    name = os.path.splitext(name)[0]
    return name

def load_data(csv):
    # Load the csv with the date column as dates rather than strings.
    if os.path.isfile(csv):
        try:
            df = pd.read_csv(csv, parse_dates=["date"])
            df = df.rename(columns=lambda x: x.strip())
            return df
        except Exception as e:
            print("Warning: Error parsing `{:}`. Ignoring.".format(csv))
    else: 
        return None

def load_dataframes(csvs):
    REQUIRED_COLS = set(["date", "mass"])
    dict_of_df = {}
    for csv_path in csvs:
        if os.path.exists(csv_path):
            # Get the geckos name 
            gecko = get_gecko_name(csv_path)
            # Load the data
            df = load_data(csv_path)
            # Check the required columns are present.
            if df is not None and REQUIRED_COLS.issubset(df.columns):
                # Store in the dict.
                dict_of_df[gecko] = df
        else: 
            print("Warning: {:} does not exist.".format(csv_path))
    return dict_of_df

def geckos_to_plot(loaded_geckos, gecko_whitelist):
    # Find which geckos should be plot.
    if gecko_whitelist is not None and len(gecko_whitelist) > 0:
        geckos_to_plot = []
        # For each gecko in the whitelist
        for gecko in gecko_whitelist:
            # If the gecko exists, add it to the ordered list of geckos to plot.
            if gecko in loaded_geckos:
                geckos_to_plot.append(gecko)
        return geckos_to_plot
    else:
        return loaded_geckos

def filter_dataframes(raw_dataframes, geckos):
    # Build a dict of only valid geckos.
    filtered_dataframes = {}
    for gecko in geckos:
        if gecko in raw_dataframes:
            filtered_dataframes[gecko] = raw_dataframes[gecko]
    return filtered_dataframes

def mutate_dataframes(dataframes):
    new_dfs = {}
    for k, v in dataframes.items():
        print(k)
        df = v.copy()

        # df["rolling"] = df["mass"].rolling(window=2).mean()
        df["rolling"] = df["mass"].ewm(span=2, adjust=False).mean()

        new_dfs[k] = df

    
    return new_dfs


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

    sns.set_palette(sns.color_palette("husl", len(gecko_dfs)))

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

        ax.plot(
            df[xcol], 
            df["rolling"],
            marker="X",#ith(MARKERS, i),
            linestyle="--",#ith(LINES,i),
            label="rolling " + gecko,
        )
        i+=1

    # Set the figure title
    plt.title("Gecko Fatness")

    # Add a legend
    ax.legend(
        title="Gecko", 
        shadow=True, 
        ncol=1,
        bbox_to_anchor=(1.05, 1),
        loc='upper left',
        borderaxespad=0.
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

    # Add title / axis labels
    plt.title("Little Fat Geckos")
    plt.xlabel("Date")
    plt.ylabel("Mass (g)")

    # Either show or save the output figure.
    show_or_save(output, dpi, force)

def main():
    args = command_line_args()

    # Flatten the input arg. 
    inputs = list(itertools.chain.from_iterable(args.input))

    # Load input csvs into a dictionary of dataframes
    raw_dataframes = load_dataframes(inputs)
    
    # Get the names of geckos to plot, based on csv names but only valid ones.
    geckos = geckos_to_plot(raw_dataframes.keys(), args.geckos)

    if len(geckos) ==  0:
        print("Error: No valid geckos specified")
        return
    
    # Build a dictionary of only dataframes to plot.
    gecko_dataframes = filter_dataframes(raw_dataframes, geckos)

    # Mutate dataframes
    gecko_dataframes = mutate_dataframes(gecko_dataframes)

    # Plot the data
    plot(
        gecko_dataframes, 
        args.output, 
        args.dpi, 
        args.force
    )

    

if __name__ == "__main__":
    main()
