# module minimal pour charger une config dans un fichier yaml
import yaml
from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

def readConfig(filepath):
    with open(filepath, 'r') as f:
        return yaml.load(f, Loader=Loader)
