import PIL
from binah.util import get_data_home, log
from binah.model import Image
from pathlib import Path
from multiprocessing import cpu_count, Pool

THUMBNAIL_SIZE = (360, 203)
THUMBNAIL_DIR = get_data_home() / 'thumbnails'
if not THUMBNAIL_DIR.is_dir():
    Path.mkdir(THUMBNAIL_DIR, parents=True)
IMAGES_DIR = get_data_home() / 'images'

def thumbnail(imgid): 
    fname = str(imgid)
    path = str(IMAGES_DIR / fname)
    with PIL.Image.open(path) as img:
            img.thumbnail(THUMBNAIL_SIZE)
            img.save(str(THUMBNAIL_DIR / fname), "JPEG")

def Thumbnails(session):
    files = [imgid for (imgid,) in session.query(Image.id)]
    log('Creating thumbnails')
    pool = Pool(cpu_count())
    pool.map(thumbnail, files)
    