import unittest
from flask_jwt_extended.exceptions import NoAuthorizationError
import requests
from api import db
from io import StringIO
from models import Materie
import env_var
import sys
from unittest.mock import patch


def get_request_without_token_scenario():
    try:
        requests.get('http://127.0.0.1:5000/users')
    except NoAuthorizationError as error:
        print(error)
        sys.exit(1)


class TestDB(unittest.TestCase):

    def test_add_subject_DB(self):
        materie = Materie(descriere='TEST ADD SUBJECT',
                          id_profesor=1, nume='TEST SUBJECT NAME')
        db.session.add(materie)
        db.session.commit()
        search_materie = Materie.query.filter(
            Materie.nume == 'TEST SUBJECT NAME').first()
        self.assertIsNotNone(search_materie)
        self.assertEqual(search_materie.descriere, 'TEST ADD SUBJECT')
        self.assertEqual(search_materie.nume, 'TEST SUBJECT NAME')
        print('Test1 completed!')


class TestApi(unittest.TestCase):

    def test_get_route(self):
        """
        Test a route with token
        """
        login_body = {
            "email": "ian@gmail.com",
            "password": "123"
        }
        response_login = requests.post(
            'http://127.0.0.1:5000/login', json=login_body)
        token = response_login.json()['access_token']
        response = requests.get('http://127.0.0.1:5000/users',
                                headers={'Authorization': "Bearer {}".format(token)})
        self.assertEqual(response.status_code, 200)
        print('Test2 completed!')

    def test_route_without_token(self):
        response = requests.get(env_var.BACKEND_PATH + '/materii')
        self.assertEqual(response.status_code, 200)
        print('Test3 completed!')

    @patch('sys.exit')
    @patch('sys.stdout', new_callable=StringIO)
    @patch('requests.get')
    def test_fetch_request_withot_token(self, mock_get, mock_stdout,
                                        mock_exit):
        mock_get.side_effect = NoAuthorizationError
        get_request_without_token_scenario()
        mock_exit.assert_called_once_with(1)
        self.assertIsNotNone(mock_stdout.getvalue())


if __name__ == '__main__':
    unittest.main()
