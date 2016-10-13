#!/usr/bin/env python2

from pyrant import Client
import json

pyrant = Client()


def test_get_rants():
    # Retrieve rants from feed
    for rant in pyrant.get_rants():
        print '*** @{}:'.format(rant.user_username)
        print rant.text, rant.id


def test_get_rant():
    # Get rant by ID
    rant = pyrant.get_rant(id=231448)

    # Get rant image
    assert rant.attached_image.url

    # Update rant from server
    rant.update()


def test_dump_rant():
    # Dump rant data, useful for checking out the available attributes
    rant = pyrant.get_rant(id=231448)
    assert json.dumps(rant.serialize(), indent=4)


def test_login():
    # Log in
    assert pyrant.log_in('tester', 'tester')


def test_vote():
    # Find a rant
    rant = pyrant.get_rant(id=231448)

    # Vote for a rant
    rant.vote(up=1)

    # Unvote for a rant
    rant.vote(up=0)
