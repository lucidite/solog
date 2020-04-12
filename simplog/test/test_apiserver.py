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
            dict(title='Terminator', text="I'll be back", year=1984, stars=3.9),
            dict(title='StarWars', text="May the Force be with You", year=1977, stars=3.9),
            dict(title='DarkKnight', text="Why so Serious?", actor="Heath Ledger", year=2008, stars=4.3),
            dict(title='StarWars', subtitle="The Empire Strikes Back", text="I Am Your Father", year=1980, stars=4.0),
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
        self.assertIn(
            response.responseCode, [200, None],
            f'GET /groups/movie?title=StarWars should return 200 OK: result={response.responseCode}'
        )

    @inlineCallbacks
    def test_GET_log_group_Test_content_type(self):
        # Given
        # When
        response = yield self.web.get(b'groups/movie', args={'title': 'StarWars'})

        # Then
        content_type_headers = response.responseHeaders.getRawHeaders('Content-Type')
        expected_content_type_headers = ['application/json; charset=utf-8']
        self.assertEqual(
            content_type_headers, expected_content_type_headers,
            f'GET /groups/movie?title=StarWars should return content-type {expected_content_type_headers}: '
            f'result={content_type_headers}'
        )

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
    def test_GET_log_group_Test_response_data_Str_range_query(self):
        # Given
        # When
        response = yield self.web.get(b'groups/movie', args={'text': '[I:J]'})
        result = json.loads(response.written[0].decode('utf-8'))

        # Then
        expected_result = [
            self.movie_log_objects[0],
            self.movie_log_objects[3],
        ]
        self.assertListEqual(
            result['logs'], expected_result,
            'GET /groups/movie?text=[I:J] should return logs with text between I and J"'
        )

    @inlineCallbacks
    def test_GET_log_group_Test_response_data_Str_range_query_Cond_left_open(self):
        # Given
        # When
        response = yield self.web.get(b'groups/movie', args={'text': '[:W]'})
        result = json.loads(response.written[0].decode('utf-8'))

        # Then
        expected_result = [
            self.movie_log_objects[0],
            self.movie_log_objects[1],
            self.movie_log_objects[3],
        ]
        self.assertListEqual(
            result['logs'], expected_result,
            'GET /groups/movie?text=[:W] should return logs with text least than W'
        )

    @inlineCallbacks
    def test_GET_log_group_Test_response_data_Str_range_query_Cond_right_open(self):
        # Given
        # When
        response = yield self.web.get(b'groups/movie', args={'text': '[M:]'})
        result = json.loads(response.written[0].decode('utf-8'))

        # Then
        expected_result = [
            self.movie_log_objects[1],
            self.movie_log_objects[2],
        ]
        self.assertListEqual(
            result['logs'], expected_result,
            'GET /groups/movie?text=[M:] should return logs with text greater than M"'
        )

    @inlineCallbacks
    def test_GET_log_group_Test_response_data_Int_query(self):
        # Given
        # When
        response = yield self.web.get(b'groups/movie', args={'year:int': '1984'})
        result = json.loads(response.written[0].decode('utf-8'))

        # Then
        expected_result = [
            self.movie_log_objects[0],
        ]
        self.assertListEqual(
            result['logs'], expected_result,
            'GET /groups/movie?year:int=1984 should return logs with year=1984'
        )

    @inlineCallbacks
    def test_GET_log_group_Test_response_data_Int_range_query(self):
        # Given
        # When
        response = yield self.web.get(b'groups/movie', args={'year:int': '[1980:2008]'})
        result = json.loads(response.written[0].decode('utf-8'))

        # Then
        expected_result = [
            self.movie_log_objects[0],
            self.movie_log_objects[3],
        ]
        self.assertListEqual(
            result['logs'], expected_result,
            'GET /groups/movie?year:int=[1980:2008] should return logs with year in [1980,2008)'
        )

    @inlineCallbacks
    def test_GET_log_group_Test_response_data_Int_range_query_Cond_left_open(self):
        # Given
        # When
        response = yield self.web.get(b'groups/movie', args={'year:int': '[:1984]'})
        result = json.loads(response.written[0].decode('utf-8'))

        # Then
        expected_result = [
            self.movie_log_objects[1],
            self.movie_log_objects[3],
        ]
        self.assertListEqual(
            result['logs'], expected_result,
            'GET /groups/movie?year:int=[:1984] should return logs with year in [,1984)'
        )

    @inlineCallbacks
    def test_GET_log_group_Test_response_data_Int_range_query_Cond_right_open(self):
        # Given
        # When
        response = yield self.web.get(b'groups/movie', args={'year:int': '[1980:]'})
        result = json.loads(response.written[0].decode('utf-8'))

        # Then
        expected_result = [
            self.movie_log_objects[0],
            self.movie_log_objects[2],
            self.movie_log_objects[3],
        ]
        self.assertListEqual(
            result['logs'], expected_result,
            'GET /groups/movie?year:int=[1980:] should return logs with year in [1980,)'
        )

    @inlineCallbacks
    def test_GET_log_group_Test_response_data_Float_range_query(self):
        # Given
        # When
        response = yield self.web.get(b'groups/movie', args={'stars:float': '[3.5:4.0]'})
        result = json.loads(response.written[0].decode('utf-8'))

        # Then
        expected_result = [
            self.movie_log_objects[0],
            self.movie_log_objects[1],
        ]
        self.assertListEqual(
            result['logs'], expected_result,
            'GET /groups/movie?stars:float=[3.5:4.0] should return logs with stars=[3.5:4.0)'
        )

    @inlineCallbacks
    def test_GET_log_group_Test_response_data_Float_range_query_Cond_left_open(self):
        # Given
        # When
        response = yield self.web.get(b'groups/movie', args={'stars:float': '[:4.3]'})
        result = json.loads(response.written[0].decode('utf-8'))

        # Then
        expected_result = [
            self.movie_log_objects[0],
            self.movie_log_objects[1],
            self.movie_log_objects[3],
        ]
        self.assertListEqual(
            result['logs'], expected_result,
            'GET /groups/movie?stars:float=[:4.2] should return logs with stars=[:4.3)'
        )

    @inlineCallbacks
    def test_GET_log_group_Test_response_data_Float_range_query_Cond_right_open(self):
        # Given
        # When
        response = yield self.web.get(b'groups/movie', args={'stars:float': '[4.0:]'})
        result = json.loads(response.written[0].decode('utf-8'))

        # Then
        expected_result = [
            self.movie_log_objects[2],
            self.movie_log_objects[3],
        ]
        self.assertListEqual(
            result['logs'], expected_result,
            'GET /groups/movie?stars:float=[4.0:] should return logs with stars=[4.0:)'
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
        self.assertIn(
            response.responseCode, [200, None],
            f'POST /groups/movie should return 200 OK: result={response.responseCode}'
        )

    @inlineCallbacks
    def test_POST_log_group_Test_content_type(self):
        # Given
        new_logs = [
            dict(title='Frozen', message="Let It Go"),
        ]

        # When
        response = yield self.web.post(b'groups/movie', args={'data': new_logs})

        # Then
        content_type_headers = response.responseHeaders.getRawHeaders('Content-Type')
        expected_content_type_headers = ['application/json; charset=utf-8']
        self.assertEqual(
            content_type_headers, expected_content_type_headers,
            f'POST /groups/movie should return content-type {expected_content_type_headers}: '
            f'result={content_type_headers}'
        )

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
