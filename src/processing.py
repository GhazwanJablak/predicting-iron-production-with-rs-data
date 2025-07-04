from rasterio.mask import mask
from pathlib import Path
from typing import Dict, Tuple
import geopandas as gpd
import rasterio as rio
import numpy as np
from logging_config import logger

def _output_params(
    input_path: Path,
) -> Tuple[str, str]:
    """
    Function to extract date and variable name from Sentinel 2 file.

    Parameters:
        input_path: Path to the raster file.
    Return:
        date: Date string.
        varname: Variable string.
    """
    if "Cloud" in input_path:
        date = input_path.split("_")[3]
    else:
        date = input_path.split("_")[-1].split(".")[0]
    varname = input_path.split("/")[3]
    return date, varname

def _crop_image(
    input_path: Path,
    shapefile_path: Path,
) -> Tuple[np.ndarray, Dict]:
    """
    Function to write cropped image to a new directory.

    Parameters:
        input_path: Path to the raster file.
        shapefile_path: Path to the bounday file.
    Return:
        crp_image: Array of the cropped data.
        crp_meta: Metadata dictionary.
    """
    logger.info(f"Opening {shapefile_path}")
    vec = gpd.read_file(shapefile_path)
    with rio.open(input_path) as img:
        logger.info(f"Opening {shapefile_path}")
        vec = vec.to_crs(img.crs)
        crp_img, crp_trans = mask(img, vec.geometry, crop=True)
        crp_meta = img.meta.copy()
    crp_meta.update(
        {
            "driver": "Gtiff",
            "height": crp_img.shape[1],
            "width": crp_img.shape[2],
            "transform": crp_trans
        }
    )
    return crp_img, crp_meta


def _write_image(
    img: rio.io.DatasetReader,
    metadata: Dict,
    date: str,
    location: str,
    varname: str,
    output_path: Path
):
    """
    Function to write an array to a raster.

    Parameters:
        img: Raster to be written to a new directory.
        metadata: Metadata dictionary.
        date: Date string.
        location: Location string
        varname: Variable string.
        output_path: Pth to the new directory.
    """
    output_path = Path(output_path+"/"+location+"/"+varname)
    output_path.mkdir(parents=True, exist_ok=True)
    with rio.open(f"{output_path}/{varname}_{location}_{date}.tif"
                  , "w", **metadata) as out:
        out.write(img)


def _image_processing(
    cloud_file: Path,
    feature_file: Path,
    cloud_free=True
) -> Tuple[np.ndarray, Dict]:
    """
    Function to remove cloudy pixels from a raster.

    Parameters:
        cloud_file: Path to cloud raster file.
        feature_file: Path to Sentinel 2 raster file
    Return:
        clfarr: Cloud-free array.
        feat_file.meta: Metadata dictionary.
    """
    logger.info(f"Opening cloud file {cloud_file}")
    with rio.open(cloud_file) as cl_file:
        clarr = cl_file.read()
    logger.info(f"feature file {feature_file}")
    with rio.open(feature_file) as feat_file:
        featarr = feat_file.read()
    if cloud_free:
        mask = np.isin(clarr, [0])
    else:
        mask = np.isin(clarr, [0, 2])
    clfarr = np.where(mask, featarr, np.nan)
    return clfarr, feat_file.meta