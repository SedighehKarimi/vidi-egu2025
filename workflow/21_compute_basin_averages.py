#!/usr/bin/env python
# coding: utf-8

# ![Vidi_Waterflux_Banner](https://raw.githubusercontent.com/ITC-Water-Resources/Vidi-waterflux-merch/refs/heads/main/jupyter/Vidi_Waterflux_Banner.png)
# *Roelof Rietbroek, Sedigheh Karimi, Amin Shakya EGU 2025*
# 
# # Compute spectral basin averages of GRACE derived TWS over the specified basins


import os
import geopandas as gpd
import shxarray
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from geoslurp import GeoslurpManager
from geoslurp.tools.xarray import *

from common.config import read_config




def main():



    shxengine='shtns' #requires shtns backend but is much quicker
    conf=read_config()
    datadir=conf['dataroot']


    # # In[20]:


    # #load basin coefficients (truncated)
    ncbasins=os.path.join(datadir,conf['ncbasin'])
    dsbasins_sh=xr.open_dataset(ncbasins)
    dsbasins_sh=dsbasins_sh.sh.build_nmindex()

    #load tws coefficients
    nctws=os.path.join(datadir,conf['nctws'])
    datws=xr.open_dataset(nctws).tws.sh.build_nmindex()
    filtername='DDK5'
    nmaxinput=datws.sh.nmax
    dabasin_avs=datws.sh.basinav(dsbasins_sh.basins.sh.truncate(nmaxinput),filtername=filtername,leakage_corr='vishwa2016',engine=shxengine)
    dabasin_avs=dabasin_avs.to_dataset(name='tws_ddk5_vw2016')
    #also compute a simply scaled basin average version
    dabasin_avs['tws_ddk5_scaled']=datws.sh.basinav(dsbasins_sh.basins,filtername=filtername,leakage_corr='scale',engine=shxengine)
    #save to netcdf 
    ncbasav=os.path.join(datadir,conf['ncbasav'])
    dabasin_avs.to_netcdf(ncbasav)



if __name__ == "__main__":
    main()
