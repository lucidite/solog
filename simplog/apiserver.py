import json
from json.decoder import JSONDecodeError

import pymongo
from twisted.internet import reactor
from twisted.web.resource import Resource, NoResource
from twisted.web.server import Site


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
        # - values are considered as string
        query = {
            k.decode('utf-8'): v[0].decode('utf-8')
            for k, v in request.args.items()
        }
        logs = [l for l in self.log_collection.find(query)]
        return json.dumps({"logs": logs}, cls=MongoDocumentEncoder).encode("utf-8")

    def render_POST(self, request):
        raw_log_data = request.content.getvalue().decode('utf-8')
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
        except KeyError as e:
            return super(MongoDocumentEncoder, self).default(o)


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
