from argparse import ArgumentParser

def do_up(parse, parser):
    from binah.model import get_config_single_host
    from binah.blueprints import Coco, TextVectors, ImageVectors, ImageEmbedding, Neighborhood, Thumbnails
    session = get_config_single_host(initialize=True)
    Coco(session)
    Thumbnails(session)
    TextVectors(session)
    ImageEmbedding(session)
    ImageVectors(session)
    Neighborhood(session)

def do_grow(parse, parser):
    if not parse.options:
        parser.error('Blueprint name required: etz grow <build_name1,build_name2>')
    import binah.blueprints
    from binah.model import get_config_single_host
    session = get_config_single_host(initialize=True)
    options = parse.options.split(',')
    #pylint gets confused by this line
    #pylint: disable=E1101
    for option in options:
        try:
            blueprint = binah.blueprints.__getattribute__(option)
        except AttributeError:
            avail_blueprints = ", ".join([blueprint for blueprint in dir(binah.blueprints) if blueprint[0].isupper()])
            parser.error(f'No blueprint found for "{option}". Available blueprints: {avail_blueprints}')
        blueprint(session)

def do_run(parse, parser):
    if not parse.options:
        parser.error('App name required: etz run <app_name>')
    if parse.options == 'search':
        from binah.apps.image_search.__main__ import main
        main()
    

def main():
    parser = ArgumentParser()
    parser.add_argument('action', help='The action to take. The actions "up", "run" and "grow" are supported.')
    parser.add_argument('options', nargs='?', help='Any parameters needed by an action.')
    parse = parser.parse_args()
    if parse.action == 'up':
        do_up(parse, parser)
    elif parse.action == 'run':
        do_run(parse, parser)
    elif parse.action == 'grow':
        do_grow(parse, parser)
    else:
        parser.error(f'Unsupported action "{parse.action}".')

if __name__ == '__main__':
    main()