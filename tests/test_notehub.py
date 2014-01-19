# File:   notehub_test.py
# Author: Sean Watson
# Date:   19 January 2014
#
# Unit tests for notehub.py. These are written to be run with Python2. Python3
# may not work.
#
# License:
# The MIT License (MIT)
#
# Copyright (c) 2014 Sean Watson
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
#    The above copyright notice and this permission notice shall be included in all
#    copies or substantial portions of the Software.
#
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
#    FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
#    COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
#    IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
#    CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from copy import deepcopy
import json
import notehub
import unittest
from mock import Mock

# If set to True and a PID and PSK are provided the tests will make actual HTTP
# requests to Notehub.org. If it isn't necessary to test with real responses set
# this to False and sample server responses will be used.
TEST_AGAINST_LIVE = False

PID = '' # Fill in your PID here to test against the live site
PSK = '' # Fill in your PSK here to test against the live site

SAMPLE_GET_NOTE = {u'title': u'Test',
                   u'statistics': {u'published': u'Sat Jan 18 21:56:58 UTC 2014',
                                   u'edited': None,
                                   u'views': u'34',
                                   u'publisher': None},
                   u'publisher': None,
                   u'note': u'#Test\r\n\r\nThis is a test note\r\n\r\n## Test Header 2',
                   u'longURL': u'http://notehub.org/2014/1/18/test-7',
                   u'shortURL': u'http://notehub.org/jk007',
                   u'status': {u'success': True,
                               u'message': ''},
                   }

SAMPLE_CREATE_NOTE = {u'longURL': u'http://notehub.org/2014/1/19/some-test-text-4',
                      u'shortURL': u'http://notehub.org/uzdmy',
                      u'noteID': u'2014 1 19 some-test-text-4',
                      u'status': {u'success': True,
                                  u'message': ''},
                      }

SAMPLE_UPDATE_NOTE = {u'longURL': u'http://notehub.org/2014/1/18/test-7',
                      u'shortURL': u'http://notehub.org/',
                      u'status': {u'success': True,
                                  u'message': ''}
                      }

class TestNotehub(unittest.TestCase):

    def setUp(self):
        self.nh = notehub.Notehub(PID,PSK)
        self.real_requests = notehub.requests

    def tearDown(self):
        notehub.requests = self.real_requests

    def test_get_note(self):
        # If you don't want to test against live just have the request call
        # return a mock with a 200 response code and the sample json
        if not TEST_AGAINST_LIVE:
            mock_response = Mock(status_code=200,
                                 json=lambda: deepcopy(SAMPLE_GET_NOTE))
            notehub.requests.get = Mock(return_value=mock_response)
        note = self.nh.get_note('2014 1 18 test-7')
        expected_note = deepcopy(SAMPLE_GET_NOTE)
        del expected_note['status']
        # Views are subject to change so omit them from the check
        del note['statistics']['views']
        del expected_note['statistics']['views']
        self.assertEqual(expected_note, note)

    def test_get_note_with_bad_note_id(self):
        bad_get_note_response = deepcopy(SAMPLE_GET_NOTE)
        bad_get_note_response['status'] = {'success': False,
                                           'message': 'Bad noteID.'}
        # If you don't want to test against live just have the request call
        # return a mock with a 200 response code and the sample json
        if not TEST_AGAINST_LIVE:
            mock_response = Mock(status_code=200,
                                 json=lambda: bad_get_note_response)
            notehub.requests.get = Mock(return_value=mock_response)
        with self.assertRaises(notehub.NotehubError):
            self.nh.get_note('not a real noteId')

    def test_create_note(self):
        # If you don't want to test against live just have the request call
        # return a mock with a 200 response code and the sample json
        if not (TEST_AGAINST_LIVE and PID and PSK):
            mock_response = Mock(status_code=200,
                                 json=lambda: deepcopy(SAMPLE_CREATE_NOTE))
            notehub.requests.post = Mock(return_value=mock_response)
        note = self.nh.create_note('some test text')
        # Since the date and ID change, just check that a URL comes back
        self.assertEqual('http://notehub.org/', note['longURL'][:19])
        self.assertIn('some-test-text', note['longURL'])
        self.assertEqual('http://notehub.org/', note['shortURL'][:19])
        self.assertIn('some-test-text', note['noteID'])

    def test_create_note_with_password(self):
        # If you don't want to test against live just have the request call
        # return a mock with a 200 response code and the sample json
        if not (TEST_AGAINST_LIVE and PID and PSK):
            mock_response = Mock(status_code=200,
                                 json=lambda: deepcopy(SAMPLE_CREATE_NOTE))
            notehub.requests.post = Mock(return_value=mock_response)
        note = self.nh.create_note('some test text', 'abc123')
        # Since the date and ID change, just check that a URL comes back
        self.assertEqual('http://notehub.org/', note['longURL'][:19])
        self.assertIn('some-test-text', note['longURL'])
        self.assertEqual('http://notehub.org/', note['shortURL'][:19])
        self.assertIn('some-test-text', note['noteID'])

    def test_update_note(self):
        # If you don't want to test against live just have the request call
        # return a mock with a 200 response code and the sample json
        if not (TEST_AGAINST_LIVE and PID and PSK):
            mock_response = Mock(status_code=200,
                                 json=lambda: deepcopy(SAMPLE_UPDATE_NOTE))
            notehub.requests.put = Mock(return_value=mock_response)
        note = self.nh.update_note('2014 1 18 test-7', 'the new text',
                                   'abc123')
        expected_note = deepcopy(SAMPLE_UPDATE_NOTE)
        del expected_note['status']
        self.assertEqual(expected_note, note)

    def test_bad_pid(self):
        bad_create_note_response = deepcopy(SAMPLE_CREATE_NOTE)
        bad_create_note_response['status'] = {'success': False,
                                              'message': 'Bad PID.'}
        # If you don't want to test against live just have the request call
        # return a mock with a 200 response code and the sample json
        if not TEST_AGAINST_LIVE:
            mock_response = Mock(status_code=200,
                                 json=lambda: bad_create_note_response)
            notehub.requests.post = Mock(return_value=mock_response)
        self.nh.pid = 'example of not a pid'
        with self.assertRaises(notehub.NotehubError):
            self.nh.create_note('some test text')
        

    def test_bad_psk(self):
        bad_create_note_response = deepcopy(SAMPLE_CREATE_NOTE)
        bad_create_note_response['status'] = {'success': False,
                                              'message': 'Bad PID.'}
        # If you don't want to test against live just have the request call
        # return a mock with a 200 response code and the sample json
        if not TEST_AGAINST_LIVE:
            mock_response = Mock(status_code=200,
                                 json=lambda: bad_create_note_response)
            notehub.requests.post = Mock(return_value=mock_response)
        self.nh.psk = 'example of not a psk'
        with self.assertRaises(notehub.NotehubError):
            self.nh.create_note('some test text')


if __name__ == '__main__':
    unittest.main()
