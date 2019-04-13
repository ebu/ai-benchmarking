"""
Make benchmarkstt available through a rudimentary JSON-RPC_ interfacea

Only supported for Python versions 3.6 and above

.. _JSON-RPC: https://www.jsonrpc.org

"""

import jsonrpcserver
from flask import Flask, request, Response, render_template
from benchmarkstt.docblock import format_docs, parse, process_rst
from .jsonrpc import get_methods


def argparser(parser):
    """
    Adds the help and arguments specific to this module
    """

    parser.add_argument('--debug', action='store_true',
                        help='run in debug mode')
    parser.add_argument('--host',
                        help='hostname or ip to serve api')
    parser.add_argument('--port', type=int, default=8080,
                        help='port used by the server')
    parser.add_argument('--entrypoint', default='/api',
                        help='the jsonrpc api address')
    parser.add_argument('--list-methods', action='store_true',
                        help='list the available jsonrpc methods')
    parser.add_argument('--with-explorer', action='store_true',
                        help='also create the explorer to test api calls with, '
                             'this is a rudimentary feature currently '
                             'only meant for testing and debugging')
    return parser


def create_app(entrypoint: str = None, with_explorer: bool = None):
    """
    Create the Flask app

    :param str entrypoint: The HTTP path on which the api will be served
    :param bool with_explorer: Whether to also serve the JSON-RPC API explorer
    :return:
    """

    app = Flask(__name__)

    if entrypoint is None:
        entrypoint = '/api'

    methods = get_methods()

    @app.route(entrypoint, methods=["POST"])
    def jsonrpc():
        req = request.get_data().decode()
        response = jsonrpcserver.dispatch(req, methods=methods, debug=True, convert_camel_case=False)
        return Response(str(response), response.http_status, mimetype="application/json")

    if with_explorer:  # pragma: nocover
        app.template_filter('parse_rst')(process_rst)

        @app.route(entrypoint, methods=['GET'])
        def explorer():
            split_methods = {}
            individual_methods = []
            for name, func in methods.items.items():
                id_ = name.replace('.', '-')
                cat = 'METHODS'
                splitted = name.split('.', 1)
                if len(splitted) == 2:
                    cat = splitted[0]
                item = dict(id=id_, name=name, details=parse(func))
                individual_methods.append(item)

                if cat not in split_methods:
                    split_methods[cat] = []

                split_methods[cat].append(item)
            return render_template('api-explorer.html', grouped_methods=split_methods, methods=individual_methods)

    return app


def main(parser, args):
    if args.list_methods:
        methods = get_methods()
        for name, func in methods.items.items():
            print('%s\n%s' % (name, '-' * len(name)))
            print('')
            print(format_docs(func.__doc__))
            print('')
    else:

        app = create_app(args.entrypoint, args.with_explorer)
        app.run(host=args.host, port=args.port, debug=args.debug)
