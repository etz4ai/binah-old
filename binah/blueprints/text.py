import tensorflow as tf
import tensorflow_hub as hub

from tqdm import tqdm

from binah.model import Text, Vector
from binah.util import log
from binah.config import SENT_ENCODER

import tensorflow as tf

CAPTION_BATCH_SIZE = 283

config = tf.ConfigProto(device_count = {'GPU': 0})

def emit_texts(session, batch_size):
    query = session.query
    caps = []
    ids = []
    res = query(Text.id, Text.text)
    for example_id, text in res:
        caps.append(text)
        ids.append(example_id)
        if len(caps) == batch_size:
            yield caps, ids
            caps = []
            ids = []
    if len(ids) > 0:
        yield caps, ids

def TextVectors(session):
    log('Loading sentence embedding')
    with tf.Graph().as_default():
        sent_input = tf.placeholder(tf.string, shape=[None], name='sent_input')
        str2vec = hub.Module(SENT_ENCODER)
        str2vec = str2vec(sent_input)
        with tf.Session(config=config) as sess:
            sess.run([tf.global_variables_initializer(), tf.tables_initializer()])
            log(f'Embedding captions into vector space (batch size: {CAPTION_BATCH_SIZE})')
            for caps, capids in tqdm(emit_texts(session, CAPTION_BATCH_SIZE), unit=' tensor blocks'):
                vecs = sess.run(str2vec, feed_dict={'sent_input:0': caps})
                for capid, vec in zip(capids, vecs):
                    row = Vector(vec=vec.tobytes(), id=capid)
                    session.merge(row)
                session.flush()
    session.commit()
  