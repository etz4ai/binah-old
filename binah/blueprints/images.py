import tensorflow as tf
import tensorflow_hub as hub
from tensorflow.estimator import EstimatorSpec, Estimator, ModeKeys
from tensorflow.estimator.export import ServingInputReceiver
from tensorflow.train import AdamOptimizer, get_global_step
from tensorflow.losses import mean_pairwise_squared_error

import numpy as np
from sqlalchemy import text

from binah.model import Caption, Vector, Image
from binah.util import log, get_models_home, get_data_home
from binah.config import IMG_ENCODER, VEC_SPACE_DIMENSIONS

import tensorflow as tf

from tqdm import tqdm

import os

IMG_BATCH_SIZE = 32
IMG_EPOCHS = 20

tf.logging.set_verbosity(tf.logging.WARN)

def get_img2vec_fns(session, mode=ModeKeys.TRAIN):
    # Ready the image embedding for fine tuning on the vector
    img2vec = hub.Module(IMG_ENCODER, trainable=True)
    _, out_dimensions = img2vec.get_output_info_dict()['default'].get_shape()
    out_dimensions = int(out_dimensions)
    width, height = hub.get_expected_image_size(img2vec) 
    images_path = get_data_home() / 'images'

    def infer_input_fn():
        query = session.query(Image.id).order_by(Image.id)
            
        def generate_example():
            for example, in query:
                example = str(images_path / str(example))
                yield example

        string_shape = tf.TensorShape([])
        dataset = tf.data.Dataset.from_generator(generate_example, tf.string, string_shape)

        def decode_and_resize(fd):
            out = tf.read_file(fd)
            # In TensorFlow, "decode_jpeg" can decode PNG files too.
            # "decode_image" will not work at all, because it doesn't return the 
            # tensor's shape.
            out = tf.image.decode_jpeg(out, channels=3, try_recover_truncated=True)
            out = tf.image.resize_images(out, [height, width], align_corners=True)
            return {'x': out}

        dataset = dataset.map(decode_and_resize)
        dataset = dataset.batch(1)
        features = dataset.make_one_shot_iterator().get_next()

        return features

    def train_input_fn():
        sql = text('select captions.image_id, vectors.vec from captions inner join vectors on captions.text_id=vectors.id')
        query = session.query(Caption.image_id, Vector.vec).from_statement(sql)
            
        def generate_example_pair():
            for example, vec in query:
                example = str(images_path / str(example))
                vec = np.frombuffer(vec, dtype=np.float32)
                yield example, vec

        string_shape = tf.TensorShape([])
        vector_shape = tf.TensorShape(tf.Dimension(VEC_SPACE_DIMENSIONS))

        dataset = tf.data.Dataset.from_generator(generate_example_pair, (tf.string, tf.float32), (string_shape, vector_shape))

        def decode_and_resize(fd, vecs):
            out = tf.read_file(fd)
            # In TensorFlow, "decode_jpeg" can decode PNG files too.
            # "decode_image" will not work at all, because it doesn't return the 
            # tensor's shape.
            out = tf.image.decode_jpeg(out, channels=3, try_recover_truncated=True)
            out = tf.image.resize_images(out, [height, width], align_corners=True)
            return {'x': out}, vecs

        dataset = dataset.map(decode_and_resize)
        dataset = dataset.batch(IMG_BATCH_SIZE)
        dataset = dataset.repeat(IMG_EPOCHS)
        
        features, labels = dataset.make_one_shot_iterator().get_next()

        return features, labels

    def model_fn(features, labels, mode): 
        tf.logging.set_verbosity(tf.logging.WARN)
        model = hub.Module(IMG_ENCODER, trainable=True)
        tf.logging.set_verbosity(tf.logging.INFO)  
        model = model(features['x'])
        regularizer = tf.get_collection(tf.GraphKeys.REGULARIZATION_LOSSES)
        output = tf.layers.dense(model, VEC_SPACE_DIMENSIONS, activation=tf.nn.relu)
        output = tf.layers.dense(model, VEC_SPACE_DIMENSIONS, activation=tf.nn.relu)
        output = tf.layers.dense(model, VEC_SPACE_DIMENSIONS, activation=tf.nn.tanh)

        if mode == ModeKeys.TRAIN or mode == ModeKeys.EVAL:
            loss = mean_pairwise_squared_error(labels, output)
            regularizer = tf.get_collection(tf.GraphKeys.REGULARIZATION_LOSSES)
            loss = loss + 0.25 * sum(regularizer)
        if mode == ModeKeys.TRAIN:    
            train_op = AdamOptimizer(learning_rate=0.00001).minimize(loss=loss, global_step=get_global_step())
            return EstimatorSpec(mode=mode, loss=loss, train_op=train_op)
        elif mode == ModeKeys.EVAL:
            eval_metric_ops = {'accuracy': tf.metrics.mean_cosine_distance(labels, output, 0)}
            return EstimatorSpec(mode=mode, loss=loss, eval_metric_ops=eval_metric_ops)
        elif mode == ModeKeys.PREDICT:
            return tf.estimator.EstimatorSpec(mode=mode, predictions=output)
        
        
    def reciever_fn():
        feature_spec = {
            'image': tf.FixedLenFeature([], dtype=tf.string)
        }
        
        tfexample = tf.placeholder(dtype=tf.string, name='input_image_tensor', shape=[])
        received_tensors = {'image': tfexample}
        parsed_example = tf.parse_example([tfexample], feature_spec)
        
        out = tf.image.decode_jpeg(parsed_example['image'], channels=3, try_recover_truncated=True)
        out = tf.image.resize_images(out, [height, width], align_corners=True)    
        out = {'x': out}

        return tf.estimator.export.ServingInputReceiver(out, received_tensors)

    if mode == ModeKeys.TRAIN:
        return model_fn, train_input_fn, reciever_fn
    else:
        return model_fn, infer_input_fn, reciever_fn

def ImageEmbedding(session):
    log('Starting training of image embedding.')
    model_fn, input_fn, reciever_fn = get_img2vec_fns(session)
    estimator = Estimator(model_fn, model_dir=str(get_models_home() / 'imgvecs'))
    tf.logging.set_verbosity(tf.logging.INFO)
    estimator.train(input_fn)
    estimator.export_savedmodel(str(get_models_home() / 'imgvecs'), reciever_fn)

def ImageVectors(session):
    log('Inferring image vectors of registered images.')
    model_fn, input_fn, _ = get_img2vec_fns(session, mode=ModeKeys.PREDICT)
    estimator = Estimator(model_fn, model_dir=str(get_models_home() / 'imgvecs'))
    ids = sorted([int(i) for i in os.listdir(get_data_home() / 'images')])

    for imgid, vec in tqdm(zip(ids, estimator.predict(input_fn)), unit=' vecs', desc='Image vectors', total=len(ids)):
        row = Vector(id=imgid, vec=vec)
        session.merge(row)
        if (imgid % 1800) == 0:
            session.flush()
    session.commit()