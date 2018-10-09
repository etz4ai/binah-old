from sanic import Sanic
from sanic.response import json
from urllib.parse import unquote
from annoy import AnnoyIndex
from binah.model import Image, get_config_single_host
from binah.util import get_data_home
import tensorflow_hub as hub
import tensorflow as tf
from binah.config import SENT_ENCODER, VEC_SPACE_DIMENSIONS
import os

app = Sanic(__name__)
tf.logging.set_verbosity(tf.logging.ERROR)

space = AnnoyIndex(VEC_SPACE_DIMENSIONS)
space.load(str(get_data_home() / 'vectors.tree'))

graph = tf.Graph()
with graph.as_default():
    sess = tf.Session(config=tf.ConfigProto(device_count = {'GPU': 0}))
    sess.as_default()
    str2vec = hub.Module(SENT_ENCODER)
    sess.run([tf.global_variables_initializer(), tf.tables_initializer()])

@app.route('/q/<query>')
async def text_query(request, query):
    with graph.as_default():
        res = sess.run(str2vec([unquote(query)]))
    res = space.get_nns_by_vector(res[0], 60)
    return json(res)

def main():
    script_dir = os.path.dirname(os.path.realpath(__file__))
    app.static('', os.path.join(script_dir, 'static', 'index.html'))
    app.static('/assets', os.path.join(script_dir, 'static', 'assets'))
    app.static('/images', str(get_data_home() / 'images'))
    app.static('/thumbnails', str(get_data_home() / 'thumbnails'))
    app.run(host='0.0.0.0', port=8080)

if __name__ == '__main__':
    main()