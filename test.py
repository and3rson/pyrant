#!/usr/bin/env python2

from pyrant import Client, Rant
import json

pyrant = Client()
for rant in pyrant.get_rants():
    print '*** @{}:'.format(rant.user_username)
    print rant.text, rant.id

# Get rant by ID
rant = Rant.get(id=231448)

# Get rant image
print rant.attached_image.url

# Update rant from server
rant.update()

# Dump rant data, useful for checking out the available attributes
print json.dumps(rant.serialize(), indent=4)
