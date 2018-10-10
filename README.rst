.. image:: binah/apps/image_search/static/assets/logo.svg

Binah is a system for training multi-modal embeddings jointly. We develop
an image embedding and a text embedding where objects of similar abstract 
meaning are near each other in a shared vector space. With this we are 
able create image and video search using arbitrary language.

Screenshot
~~~~~~~~~~

.. image:: screenshot.png

Installation
~~~~~~~~~~~~

::

    pip install binah

Usage
~~~~~

Binah comes bundled with the etz command line tool.

To completely set up the project, simply run:

::

    etz up

This command sets up the whole Binah system de novo. It takes days to 
run since it downloads datasets and trains complicated deep learning 
models.

After "etz up" is finished you can start the image search web demo.
Simply run:

::

    etz run search

Inline documentation about other actions is available:

::

    etz -h