from glob import glob 
from typing import List

def _input_generator(shp_dirs: List, folders_list: List):
    for d in shp_dirs:
        for f in folders_list:
            files = glob(f"./Gijon2/Sentinel2/{f}/*.tif")
            for file in files:
                yield file, d


def _output_date(file):

    date = file.split("/")[-1].split("_")[-1].split(".")[0]
    varname = file.split("/")[3]
    return date, varname