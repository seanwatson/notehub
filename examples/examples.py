# File:   examples.py
# Author: Sean Watson
# Date:   18 January 2014
#
# Some basic examples of how to use the notehub wrapper.
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

from notehub import Notehub
from notehub import NotehubError

# You must request your own PID and PSK from http://notehub.org/api
# If you don't have a PID and PSK only the get_note method will work.
PID = 'example_pid' # Replace with your PID
PSK = 'example_psk' # Replace with your PSK

def main():
    nh = Notehub(PID, PSK)

    # get_note
    try:
        note = nh.get_note('2014/1/26/test')
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
        note = nh.create_note(note_text, password=password)
        print(note)
    except NotehubError as e:
        print(e)

    # create_note with specific theme and fonts
    note_text = 'Test note 123.'
    theme = 'solarized-light'
    text_font = 'Alegreya Sans SC'
    header_font = 'Chau Philomene One'
    try:
        note = nh.create_note(note_text, theme=theme, text_font=text_font,
                              header_font=header_font)
        print(note)
    except NotehubError as e:
        print(e)

    # update_note
    note_id = '2014/1/26/test-note-123-1'
    new_note_text = 'Test note 123.'
    password = 'abc123'
    try:
        note = nh.update_note(note_id, new_note_text, password)
        print(note)
    except NotehubError as e:
        print(e)


if __name__ == '__main__':
    main()
