import yaml
import pathlib
import os

thisdir=pathlib.Path(__file__).parent.resolve()

def read_config():
    with open(os.path.join(thisdir,'config.yml'),'r') as fid:
        config=yaml.safe_load(fid)

    return config


