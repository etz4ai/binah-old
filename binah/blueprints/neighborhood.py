from binah.util import log, get_data_home
from binah.model import Vector, Example, Type
from binah.config import VEC_SPACE_DIMENSIONS
from sqlalchemy import text
from annoy import AnnoyIndex
from tqdm import tqdm
import numpy as np

def Neighborhood(session):
        index = AnnoyIndex(VEC_SPACE_DIMENSIONS)
        log('Enrolling vectors in vector index.')
        query = session.query(Vector.id, Vector.vec).join(Example).filter(Example.type == Type.JPEG)
        for vec_id, vec in tqdm(query, desc='Vectors enrolled', total=query.count(), unit=' vecs'):
            vec = np.frombuffer(vec, dtype=np.float32)
            index.add_item(vec_id, vec)
        log('Building and saving vector index to disk.')
        index.build(10)
        index.save(str(get_data_home() / 'vectors.tree'))