import yaml
import pathlib
import os
import requests
from zipfile import ZipFile
import json

thisdir=pathlib.Path(__file__).parent.resolve()

def read_config():
    with open(os.path.join(thisdir,'config.yml'),'r') as fid:
        config=yaml.safe_load(fid)

    return config


#color stuff
def add_alpha(hxcol,alpha):
    return hxcol+hex(int(alpha*255))[-2:]

posterdark='#003246'
posterred='#a52a2a'
itcgreen='#308b7d'
itcblue='#293f8b'
xarrayblue='#389ccb'



def get_background(name='HypsoReliefWater'):
    """ see also: https://docs.dkrz.de/doc/visualization/sw/python/source_code/python-matplotlib-example-high-resolution-background-image-plot.html"""

    imagedescr={"__comment__": "JSON file specifying background images. env CARTOPY_USER_BACKGROUNDS, ax.background_img()",
          "HypsoReliefWater": {
            "__comment__": "Cross Blended Hypso with Shaded Relief and Water",
            "__source__": "https://www.naturalearthdata.com/http//www.naturalearthdata.com/download/50m/raster/HYP_50M_SR_W.zip",
            "__projection__": "PlateCarree",
            "high": "HYP_50M_SR_W.tif"
      },
    }
    
    conf=read_config()
    crtbg=conf['cart_backgrounds']
    if not os.path.exists(crtbg):
        os.makedirs(crtbg)
    
    #also write the json file from the above image description dict
    imagedescrf=os.path.join(crtbg,'images.json')
    if not os.path.exists(imagedescrf):
        with open(imagedescrf,'wt') as fid:
            fid.write(json.dumps(imagedescr))

    url=imagedescr[name]['__source__']
    zipf=os.path.join(crtbg,os.path.basename(url))

    #download doesnt work ?? did a manual downlaod
    if not os.path.exists(zipf):
        r=requests.get(url)

        with open(zipf,'wb') as zid:
            zid.write(r.content)

    #extract
    with ZipFile(zipf) as zid:
        zid.extractall(crtbg)

    #set environment variable
    os.environ['CARTOPY_USER_BACKGROUNDS'] = crtbg