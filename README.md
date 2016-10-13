# PyRant

This is an unofficial Python client library for DevRant.

# Dependencies

None

# Usage example

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

# Roadmap

- Authentication
- Test coverage
- Profile
- Creating/editing rants
- Notifications

# License

MIT

# Contribution

Feel free to ping me at andrew /at/ dun.ai or create a github issue.
