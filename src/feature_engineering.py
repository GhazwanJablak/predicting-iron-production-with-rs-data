from pathlib import Path
from glob import glob
import rasterio as rio
import pandas as pd
import numpy as np

def _enginner_features(
    folder_path: Path
) -> pd.DataFrame:
    """
    Function to create two time series from a raster.
    80th and 20th qunatiles will be extracted at every available dates.
    
    Parameters:
        folder_path: File path to the raster.
    Return:
        df: Dataframe of time series.
    """
    Dates, q20, q80 = [], [], []
    files = sorted(glob(f"{folder_path}/*.tif"))
    loc = files[0].split("/")[3]
    feature = files[0].split("/")[4]
    for f in files:
        Dates.append(f.split("/")[-1].split("_")[-1]
                     .split(".")[0])
        arr = rio.open(f).read()
        q20.append(np.nanquantile(arr,0.2))
        q80.append(np.nanquantile(arr, 0.8))
    df = pd.DataFrame(
        {"Dates": Dates,
         f"{feature}_{loc}_Q20": q20,
         f"{feature}_{loc}_Q80": q80}
    )
    return df


def aggregation(
        df: pd.DataFrame
        ) -> pd.DataFrame:
     """
    Function to aggregate daily time series to monthly level.
    minimum and maximum of the 80th and 20th qunatiles will be aggregated.
    
    Parameters:
        df: Dataframe of daily time series.
    Return:
        df2: Dataframe of monthly time series.
    """
     df["Dates"] = pd.to_datetime(df["Dates"], format="%Y%m%d")
     df["Year"] = df["Dates"].dt.year
     df["Month"] = df["Dates"].dt.month
     time_cols = ["Dates", "Year", "Month"]
     feat_cols = [col for col in df.columns if col not in time_cols]
     df = df[time_cols + feat_cols]
     df2 = df.groupby(["Year", "Month"]).agg(
        {
            df.columns[-1]: ["max", "min"],
            df.columns[-2]: ["max", "min"]
        }
    ).reset_index()
     df2.columns = [("_").join((a, b)) for a, b in df2.columns.ravel()]
     return df2