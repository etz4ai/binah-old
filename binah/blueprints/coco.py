import codecs
import json
from io import BytesIO
from urllib.request import urlopen, urlretrieve
from urllib.error import HTTPError
from zipfile import ZipFile

from dateutil import parser
from sqlalchemy import (Boolean, Column, Date, Float, ForeignKey, Integer,
                        SmallInteger, String, create_engine)
from tqdm import tqdm

from binah.model import (Caption, Category, ControlledImport, Dataset,
                              Image, License, BoundingBox, Type, Text, Example,
                              Lifecycle)
from binah.util import log


utf = codecs.getreader("utf-8")
ANNOTATIONS_URL = 'http://images.cocodataset.org/annotations/annotations_trainval2017.zip'


class CocoImport(ControlledImport):
    def __init__(self, session):
        super(CocoImport, self).__init__(session, has_files=True)

    def create_database(self):
        log(f'Getting COCO annotations from {ANNOTATIONS_URL}')
        zip = ZipFile(BytesIO(urlopen(ANNOTATIONS_URL).read()))
        session = self.session

        dsinfo = Dataset(
            name='COCO',
            desc='COCO is a large-scale object detection, segmentation, and captioning dataset.',
            url='http://cocodataset.org/')
        session.add(dsinfo)
        session.flush()
        cocoid = dsinfo.id
        
        surrigate = {}

        def populate_images(index, lifecycle):
            for image in tqdm(
                    index['images'], desc='Image metadata', unit=' rows'):
                example_row = Example(
                        dataset_id=cocoid,
                        type=Type.JPEG,
                        lifecycle=lifecycle,
                        license_id=image['license']
                        )
                session.add(example_row)
                session.flush()
                image_row = Image(
                    id=example_row.id,
                    src_filename=image['file_name'],
                    url=image['coco_url'],
                    captured=parser.parse(
                        image['date_captured']),
                    orig_url=image['flickr_url'])
                session.add(image_row)
                surrigate[image['id']] = example_row.id 

        def populate_annotations(index, lifecycle):
            for i, annotation in enumerate(
                    tqdm(index['annotations'], desc='Annotations', unit=' rows')):
                if annotation.get('bbox'):
                    row = BoundingBox(
                        image_id=surrigate[annotation['image_id']],
                        category_id=annotation['category_id'],
                        x1=annotation['bbox'][0],
                        y1=annotation['bbox'][1],
                        x2=annotation['bbox'][2],
                        y2=annotation['bbox'][3])
                    session.add(row)
                else:
                    example_row = Example(
                        dataset_id=cocoid,
                        type=Type.DBTEXT,
                        lifecycle=lifecycle, 
                        license_id=4  # 4 is CC-Attr, which is license for annotations
                    )
                    session.add(example_row)
                    session.flush()
                    text_row = Text(id=example_row.id, text=annotation['caption'])
                    caption_row = Caption(text_id=example_row.id, image_id=surrigate[annotation['image_id']])
                    session.add(text_row)
                    session.add(caption_row)
                # This reduces memory usage at the cost of some rows/sec.
                if (i % 900) == 0:  
                    session.flush()
            session.flush()

        def populate_metadata(index):
            for category in index['categories']:
                row = Category(**category)
                session.add(row)
            for lic in index['licenses']:
                row = License(**lic)
                session.add(row)
            session.flush()

        with zip.open('annotations/instances_train2017.json') as fd:
            log('Processing training instances.')
            index = json.load(utf(fd))
            populate_metadata(index)
            populate_images(index, Lifecycle.TRAIN)
            populate_annotations(index, Lifecycle.TRAIN)
        with zip.open('annotations/captions_train2017.json') as fd:
            log('Processing training captions.')
            index = json.load(utf(fd))
            populate_annotations(index, Lifecycle.TRAIN)
        with zip.open('annotations/instances_val2017.json') as fd:
            log('Processing validation instances.')
            index = json.load(utf(fd))
            populate_images(index, Lifecycle.VERIFY)
            populate_annotations(index, Lifecycle.VERIFY)
        with zip.open('annotations/captions_val2017.json') as fd:
            log('Processing validation captions.')
            index = json.load(utf(fd))
            populate_annotations(index, Lifecycle.VERIFY)

        session.commit()

    def create_files(self):
        log('Downloading images')
        try_again = False
        query = self.session.query(Image.url, Image.id)
        for url, imgid in tqdm(query, desc='Images downloaded', unit=' imgs', total=query.count()):
            filename = str(imgid)
            if not self.exists(filename):
                try:
                    urlretrieve(url, self.path(filename))
                except HTTPError as e:
                    raise RuntimeError(f'Could not download image {url} (HTTP Code: {e.code})')
                except:
                    try_again = True
                    continue
        if try_again:
            log('Some files failed download. Will retry.')
            self.create_files()


    def create(self):
        res = self.session.query(Dataset.name).filter(Dataset.name == 'COCO').first()
        if not res:
            log('COCO metadata missing. Will initiate downloading and processing of COCO metadata.')
            self.create_database()
        self.create_files()

def Coco(session):
    CocoImport(session).create()