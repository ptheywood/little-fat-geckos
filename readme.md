# Gecko Fatness

Repo containing data and plotting script for the fatness of my geckos.

## Data

Data is stored in CSV files in the `data` directory. One gecko per file.

## Plotting

Run the script to view the figure, selecting which file(s) to view.

``` bash
python3 plot-litte-fat-geckos.py -i data/bojak.csv data/biscuit.csv
```

Use the `-h/--help` option for further usage information.


### Example

E.g. to generate a plot of bojak and biscuit:

```bash
python3 plot-litte-fat-geckos.py -i data/bojak.csv data/biscuit.csv -o samples/bojack-and-biscuit.png -f
```

![Bojak and Biscuit](samples/bojack-and-biscuit.png)
