#!/usr/bin/env python
from geoslurp import GeoslurpManager
#local python tools
from common.config import read_config
import geoslurp.tools.pandas
import geopandas as gpd
import os
from copy import deepcopy
from glob import glob
import xarray as xr
#import glofas base class (to be modified for our needs)
from geoslurp.dataset.cdsbase import CDSBase



conf=read_config()
datadir=conf['dataroot']
glofasdir=os.path.join(datadir,'GloFAS')
schema=conf['geoslurpschema']
disloctable=f"{schema}.glofasv4dischlocations"

gsman=GeoslurpManager(dbalias='marge',readonly_user=False)


# read the dicharge outlet locations from the database
dfdisloc=gpd.GeoDataFrame.gslrp.load(gsman.conn,f"SELECT * from  {disloctable}",geom_col='geom')
dfdisloc.head()
#create a derived glofas class with the data holdings
class GloFASOutletsv4(CDSBase):
    schema=schema
    resource='cems-glofas-historical'
    productType='consolidated'
    variables='river_discharge_in_the_last_24_hours'
    oformat='grib'
    res=0.05 #degrees
    version=(4,0,0)
    yrstart=2000
    yrend=2024
    cdsalias='glofas'
    timePriority=True
    resumejobs=True
    
    def createRequests(self):
        """Builds a set of dictionary for the cdsapi"""
        reqdict=self.getDefaultDict()
        reqdict['system_version']='version_4_0'
        reqdict['hydrological_model']='lisflood'
        reqdict['hyear']= [f"{yr}" for yr in range(self.yrstart,self.yrend+1)]
        reqdict['hmonth']=[f"{mn:02d}" for mn in range(1,13)]
        reqdict['hday']=[f"{mn:02d}" for mn in range(1,32)]
        
        prio=0

        #loop over the requested years (need to split this up to prevent too large requests
        for yr in range(self.yrstart,self.yrend+1):
            reqdictcp=deepcopy(reqdict)
            reqdictcp["hyear"]=f"{yr}"
            name_yr=f"{self.resource}_{yr}"
            self.addRequest(name_yr,reqdictcp,prio)

        
    def metaExtractor(self,uri):
        name="".join(os.path.basename(uri.url).split('_')[-2:])[0:-4]
        ds=xr.open_dataset(uri.url,engine='cfgrib')
        data={"dimensions":{ky:val for ky,val in ds.dims.items()},"variables":{ky:{"long_name":val.attrs["long_name"],"dimensions":val.dims} for ky,val in ds.variables.items()}}

        tstart=np_to_datetime(ds.time.values[0])
        tend=np_to_datetime(ds.time.values[-1])
        latmin=ds.latitude.min().values
        latmax=ds.latitude.max().values
        lonmin=ds.longitude.min().values
        lonmax=ds.longitude.max().values
        bbox=Polygon([(lonmin,latmin),(lonmin,latmax),(lonmax,latmax),(lonmax,latmin)])
        return {"name":name,"lastupdate":uri.lastmod,"tstart":tstart,"tend":tend,"uri":uri.url,"data":data,"geom":wktdumps(bbox)}
glofasds=GloFASOutletsv4(gsman.conn)
glofasds.setDataDir(glofasdir)

glofasds.createRequests()
glofasds.pull()

#load global grids and subtract time series
print("extracting outlet time series")
glofasfiles=sorted(glob(glofasdir+'/cems-glofas-historical_cems-glofas-historical_*grb'))
dsglofas=xr.open_mfdataset(glofasfiles,chunks=dict(time=59,longitude=7200,latitude=3000),engine='cfgrib',decode_timedelta=True)
#extract data for the dedicated outl;et points
#note: change from 1 to zero index
x=xr.DataArray(dfdisloc.x-1,dims=['noutlets'])
y=xr.DataArray(dfdisloc.y-1,dims=['noutlets'])

dsglofasoutlets=dsglofas.dis24[:,y,x].to_dataset()
dsglofasoutlets['basins']=('noutlets',dfdisloc.name)
dsglofasoutlets['endo']=('noutlets',dfdisloc.endo)
dsglofasoutlets['upstream_area']=('noutlets',dfdisloc.upstream_area)

glofasfout=os.path.join(datadir,'glofasv4_outlets.nc')
# Overwrite time series data
dsglofasoutlets.to_netcdf(glofasfout,mode='w')










