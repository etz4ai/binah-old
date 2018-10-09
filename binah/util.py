import logging
import sys 
from pathlib import Path
import os
import inspect
from tensorflow.train import SessionRunHook

from tqdm import tqdm

def log(msg):
    caller = inspect.stack()[1][3]
    print(f'INFO:binah:{caller} -> {msg}')

def get_home():
    home = os.environ.get('ETZHOME')
    if home:
        home = Path(home)
    else:
        home = Path.home() / '.etz'
    if not home.is_dir():
        Path.mkdir(home, parents=True)
    return home

def get_data_home():
    home = get_home()
    home = home / 'data'
    if not home.is_dir():
        Path.mkdir(home, parents=True)
    return home

def get_vectors_home():
    home = get_home()
    home = home / 'vectors'
    if not home.is_dir():
        Path.mkdir(home, parents=True)
    return home

def get_models_home():
    home = get_home()
    home = home / 'models'
    if not home.is_dir():
        Path.mkdir(home, parents=True)
    return home

class ProgressBar(SessionRunHook):
    def __init__(self, desc='Training batches'):
        self.progress = tqdm(desc=desc)

    def after_run(self, run_context, run_values):
        pass

os.environ['TFHUB_CACHE_DIR'] = str(get_models_home() / 'tfhub')
