# File:   notehub.py
# Author: Sean Watson
# Date:   18 January 2014
#
# A simple wrapper for the Notehub.org API.
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

__doc__ = """A simple wrapper for the Notehub.org api.

A wrapper for the Notehub.org api that simplifies much of the work needed to
make a call. The wrapper handles the work of adding necessary parameters,
hashing passwords, generating signatures, encoding the data and checking
response codes.

*************************************************************
***You will need a PID and PSK from http://notehub.org/api***
***in order to use the create_note and update_note methods.**
*************************************************************

Example use:

    from notehub import Notehub
    from notehub import NotehubError

    PID = 'example_pid' # Replace with your PID
    PSK = 'example_psk' # Replace with your PSK

    nh = Notehub(PID, PSK)

    # get_note
    try:
        note = nh.get_note('2014 1 18 test-7')
        print(note)
    except NotehubError as e:
        print(e)

    # create_note
    note_text = 'Test note 123.'
    try:
        note = nh.create_note(note_text)
        print(note)
    except NotehubError as e:
        print(e)

    # create_note with password
    note_text = 'Test note 123.'
    password = 'abc123'
    try:
        note = nh.create_note(note_text, password)
        print(note)
    except NotehubError as e:
        print(e)

    # update_note
    note_id = '2014 1 18 test-7'
    new_note_text = 'New note text.'
    password = 'abc123'
    try:
        note = nh.update_note(note_id, new_note_text, password)
        print(note)
    except NotehubError as e:
        print(e)

"""

__author__ = 'Sean Watson'
__date__ = '18 January 2014'


from hashlib import md5
import json
import requests
import sys


class NotehubError(Exception):
    """Exception thrown by Notehub methods when an error occurs.
    """
    pass

class Notehub(object):
    """A wrapper for the Notehub.org api.

    Attributes:
        pid: The publisher ID received from Notehub.org.
        psk: The publisher secret key received from Notehub.org. 
        version: The api version to use. (Default: '1.1').
    """

    BASE_URL = 'http://notehub.org/api/note'

    def __init__(self, pid, psk, version='1.1'):
        """Constructor for Notehub object.

        Args:
            pid: The publisher ID received from Notehub.org.
            psk: The publisher secret key received from Notehub.org.
            version: Optional. Default '1.1'. Which version of the API to use.
        """
        self.pid = pid
        self.psk = psk
        self.version = version
    
    def _request(self, method, params={}, data={}):
        """Private. Preforms operations common to all API calls.

        Preforms the operations common to all API calls such as contructing the
        URL, making the HTTP request, and checking the response codes. A dictionary
        should be passed in either as "params" or "data". If "data" is provided then
        an HTTP POST request will be used.

        Args:
            method: The HTTP method to use, GET, POST or PUT
            params: HTTP GET parameters
            data: HTTP POST data

        Returns:
            A dict populated from the JSON response from the server. The "status"
            object is removed since error checking is handled here.

        Raises:
            NotehubError: There was a problem making the API call. The message
                contains a string explaining what went wrong.
        """

        try:
            # Make the request
            if method == 'GET':
                req = requests.get(self.BASE_URL, params=params)
            elif method == 'POST':
                req = requests.post(self.BASE_URL, data=data)
            else: # PUT
                req = requests.put(self.BASE_URL, data=data)

            # Check the response code
            if req.status_code != requests.codes.ok:
                raise NotehubError('Server returned non-200 response code: '
                                    + str(req.status_code))

            # Parse the response
            resp = req.json()

            # Check the status
            if resp['status']['success'] != True:
                raise NotehubError(
                    'Non successful status: ' + resp['status']['message'])
                
            del resp['status']
        except (IOError, KeyError, ValueError) as e:
            # If there is an error opening the connection or deleting the key
            # wrap the error in a NotehubError and re-raise it.
            raise NotehubError(str(e))
        return resp

    def _get_signature(self, text):
        """Private. Generates a Notehub.org signature with the given text.

        Args:
            text: The text to be included in the signature.
        """
        full_text = self.pid + self.psk + text
        return md5(full_text.encode('utf-8')).hexdigest()


    def get_note(self, note_id):
        """Retreives the text of a note on Notehub.org.

        Makes a call to Notehub.org's GET NOTE api. This returns
        the text of a note from a given note ID. It also returns
        some URLs that link to the note and some statistics about it.

        Args:
            note_id: The ID of the note to request.

        Returns:
            A dict populated from the JSON response of the API call.

        Raises:
            NotehubError: There was a problem making the call. Check the
                message.
        """
        params = {'noteID': note_id,
                  'version': self.version,
            }
        return self._request('GET', params=params)

    def create_note(self, note_text, password=''):
        """Creates a note on Notehub.org with the given text.

        Makes a call to Notehub.orgs CREATE NOTE api. To edit a note later
        a password must be given. If successful the note's ID and some URLs
        linking too it will be returned.

        Args:
            note_text: The ID of the note to request.
            password: Optional. A password to allow for updating the note.

        Returns:
            A dict populated from the JSON response of the API call.

        Raises:
            NotehubError: There was a problem making the call. Check the
                message.
        """
        data = {'note': note_text,
                'pid': self.pid,
                'signature': self._get_signature(note_text),
                'version': self.version,
            }
        if password:
            data['password'] = md5(password.encode('utf-8')).hexdigest()
        return self._request('POST', data=data)

    def update_note(self, note_id, new_note_text, password):
        """Edits a note on Notehub.org.

        Makes a call to Notehub.org's UPDATE NOTE api. The note must have
        been originally created with a password to allow updating. If
        successful some URLs that link to the note will be returned.

        Args:
            note_id: The ID of the note to request.
            new_note_text: The text to replace the existing text with.
            password: The password the note was created with.

        Returns:
            A dict populated from the JSON response of the API call.

        Raises:
            NotehubError: There was a problem making the call. Check the
                message.
        """
        encoded_password = md5(password.encode('utf-8')).hexdigest()
        data = {'noteId': note_id,
                'note': new_note_text,
                'pid': self.pid,
                'signature': self._get_signature(
                    note_id + new_note_text + encoded_password),
                'password': encoded_password,
                'version': self.version,
            }
        return self._request('PUT', data=data)

