import json

import mongomock
from twisted.internet.defer import inlineCallbacks
from twisted.trial import unittest

from simplog.apiserver import SimplogHome
from simplog.test.dummy import DummySite


class SimplogTestCase(unittest.TestCase):
    def setUp(self):
        connection = mongomock.MongoClient('mongodb://127.0.0.1:27017')
        self.log_db = connection.logs
        movie_group_collection = self.log_db.movie
        self.movie_log_objects = [
            dict(title='Terminator', text="I'll be back"),
            dict(title='StarWars', message="May the Force be with You"),
            dict(title='DarkKnight', message="Why so Serious?", actor="Heath Ledger", note="Joker"),
            dict(title='StarWars', message="I Am Your Father", note="Darth Vader"),
        ]
        for log_object in self.movie_log_objects:
            # inserted_id returns ObjectId,
            # the ObjectId is converted to str to be compared with _id field(str) in the written data
            log_object['_id'] = str(movie_group_collection.insert_one(log_object).inserted_id)

        self.web = DummySite(SimplogHome(connection))

    def get_logs(self, collection_name):
        return [
            {k: str(v) if k == '_id' else v for k, v in log.items()}
            for log in self.log_db[collection_name].find()
        ]

    @inlineCallbacks
    def test_GET_log_group_Test_response_code(self):
        # Given
        # When
        response = yield self.web.get(b'groups/movie', args={'title': 'StarWars'})

        # Then
        self.assertIn(response.responseCode, [200, None], 'GET /groups/movie?title=StarWars should return 200 OK')

    @inlineCallbacks
    def test_GET_log_group_Test_response_data(self):
        # Given
        # When
        response = yield self.web.get(b'groups/movie', args={'title': 'StarWars'})
        result = json.loads(response.written[0].decode('utf-8'))

        # Then
        expected_result = [
            self.movie_log_objects[1],
            self.movie_log_objects[3],
        ]
        self.assertListEqual(
            result['logs'], expected_result,
            'GET /groups/movie?title=StarWars should return logs with title "StarWars"'
        )

    @inlineCallbacks
    def test_POST_log_group_Test_response_code(self):
        # Given
        new_logs = [
            dict(title='Frozen', message="Let It Go"),
        ]

        # When
        response = yield self.web.post(b'groups/movie', args={'data': new_logs})

        # Then
        self.assertIn(response.responseCode, [200, None], 'POST /groups/movie should return 200 OK')

    @inlineCallbacks
    def test_POST_log_group_Test_response_data(self):
        # Given
        new_logs = [
            dict(title='JurassicPark', message="Life finds a Way", director="Steven Spielberg"),
            dict(title='3Idiots', message="Aal izz well", country="India"),
        ]

        # When
        response = yield self.web.post(b'groups/movie', args={'data': new_logs})

        # Then
        response_data = response.written[0].decode('utf-8')
        result = json.loads(response_data)
        self.assertTrue(result['success'], 'POST /groups/movie should return success')
        self.assertEqual(len(result['id']), 2, 'POST /groups/movie should return 2 ids')

    @inlineCallbacks
    def test_POST_log_group_Test_db_data(self):
        # Given
        new_logs = [
            dict(title='Frozen', message="Let It Go"),
            dict(title='JurassicPark', message="Life finds a Way", director="Steven Spielberg"),
            dict(title='3Idiots', message="Aal izz well", country="India"),
        ]

        # When
        response = yield self.web.post(b'groups/movie', args={'data': new_logs})
        response_data = response.written[0].decode('utf-8')
        result = json.loads(response_data)
        for i, inserted_id in enumerate(result['id']):
            new_logs[i]['_id'] = inserted_id

        # Then
        expected_logs = self.movie_log_objects + new_logs
        self.assertListEqual(
            self.get_logs('movie'), expected_logs,
            'POST /groups/movie should store logs in request data into movie collection',
        )

    @inlineCallbacks
    def test_POST_log_group_Test_new_group_logs(self):
        # Given
        new_logs = [
            dict(title="SuperMario", text="It's-a me! Mario!", country="Japan"),
            dict(title="StarCraft", text="My Life for Aiur", company="Blizzard"),
        ]

        # When
        response = yield self.web.post(b'groups/game', args={'data': new_logs})
        response_data = response.written[0].decode('utf-8')
        result = json.loads(response_data)
        for i, inserted_id in enumerate(result['id']):
            new_logs[i]['_id'] = inserted_id

        # Then
        self.assertListEqual(
            self.get_logs('game'), new_logs,
            'POST /groups/game should store logs in request data into game collection',
        )
        self.assertListEqual(
            self.get_logs('movie'), self.movie_log_objects,
            'POST /groups/game should not change data in movie collection',
        )
