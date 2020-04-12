import json
from json.decoder import JSONDecodeError

import pymongo
from twisted.internet import reactor
from twisted.web.resource import Resource, NoResource
from twisted.web.server import Site

_content_type_key = 'Content-Type'
_content_type_value = 'application/json; charset=utf-8'
_value_type_postfix = {
    ':int': int,
    ':float': float,
}


class SimplogHome(Resource):
    def __init__(self, db_connection):
        super().__init__()
        self.db_connection = db_connection

    def getChild(self, path, request):
        path = path.decode('utf-8')
        if path == 'groups':
            return LogGroupsPage(self.db_connection)
        else:
            return NoResource()


class LogGroupsPage(Resource):
    def __init__(self, db_connection, ):
        super().__init__()
        self.log_db = db_connection.logs

    def getChild(self, path, request):
        group_name = path.decode('utf-8')
        return LogGroupPage(self.log_db, group_name)


class LogGroupPage(Resource):
    isLeaf = True

    def __init__(self, db, group_name):
        super().__init__()
        self.log_collection = db[group_name]

    def render_GET(self, request):
        # constraints:
        # - only one value for each key is allowed now
        request.setHeader(_content_type_key, _content_type_value)
        query = {
            field: condition for field, condition
            in (decode_query_argument(k, v) for k, v in request.args.items())
        }
        logs = [l for l in self.log_collection.find(query)]
        return json.dumps({"logs": logs}, cls=MongoDocumentEncoder).encode("utf-8")

    def render_POST(self, request):
        raw_log_data = request.content.getvalue().decode('utf-8')
        request.setHeader(_content_type_key, _content_type_value)
        try:
            logs = json.loads(raw_log_data)
            log_ids = self.log_collection.insert_many(logs).inserted_ids
            result = {
                'success': True,
                'id': [str(log_id) for log_id in log_ids],
            }
        except JSONDecodeError as e:
            result = {
                'success': False,
                "error": repr(e),
            }
        return json.dumps(result).encode("utf-8")


class MongoDocumentEncoder(json.JSONEncoder):
    def default(self, o):
        try:
            return str(o)
        except KeyError:
            return super(MongoDocumentEncoder, self).default(o)


def decode_arg_key(arg_key):
    arg_key = arg_key.decode('utf-8')
    for postfix, value_type in _value_type_postfix.items():
        if arg_key.endswith(postfix):
            def convert(value_str):
                return value_type(value_str) if value_str else ''
            return arg_key[:-len(postfix)], convert
    return arg_key, str     # default


def decode_query_argument(arg_key, arg_values):
    arg_key, convert = decode_arg_key(arg_key)
    arg_value = arg_values[0].decode('utf-8')
    if arg_value.startswith('[') and arg_value.endswith(']'):
        range_segments = arg_value[1:-1].split(":")
        if len(range_segments) == 2:
            try:
                range_dict = {
                    '$gte': convert(range_segments[0]),
                    '$lt': convert(range_segments[1]),
                }
                return arg_key, {k: v for k, v in range_dict.items() if v}
            except ValueError:
                raise
    return arg_key, convert(arg_value)


if __name__ == '__main__':
    mongo_host = 'mongo'
    connection = pymongo.MongoClient(f'mongodb://{mongo_host}')
    print(f'simplog > connect to database...')

    root = SimplogHome(connection)
    site_factory = Site(root)
    server_port = 8080
    reactor.listenTCP(server_port, site_factory)
    print(f'simplog > listening {server_port}...')
    reactor.run()
