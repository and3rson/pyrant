from __future__ import unicode_literals
import urllib
import urllib2
import json
import requests
from weakref import proxy


class Remote(object):
    URL = 'https://www.devrant.io/api'

    def __init__(self):
        # self.opener = urllib2.build_opener(urllib2.HTTPHandler)
        self.extra = {}

    def add_extra(self, key, value):
        self.extra[key] = value

    def _request(self, endpoint, method, **kwargs):
        kwargs.update(self.extra)
        # if method in ('POST', 'PUT', 'PATCH'):
        #     url = Remote.URL + '/' + endpoint
        #     request = urllib2.Request(url, data=json.dumps(kwargs))
        # else:
        #     url = Remote.URL + '/' + endpoint + '?' + urllib.urlencode(kwargs)
        #     request = urllib2.Request(url)

        # # request.add_header('Content-type', 'application/json')
        # request.get_method = lambda: method

        # response = self.opener.open(request)
        # return response.read()

        opener = getattr(requests, method.lower())

        if method in ('POST', 'PUT', 'PATCH'):
            url = Remote.URL + '/' + endpoint
            response = opener(url, data=kwargs)
        else:
            url = Remote.URL + '/' + endpoint + '?' + urllib.urlencode(kwargs)
            response = opener(url)

        return response.content

    def _json_request(self, endpoint, method='GET', **kwargs):
        return json.loads(self._request(endpoint, method, **kwargs))


class Serializable(object):
    def serialize(self):
        return {
            prop_name: prop_value.serialize()
            if isinstance(prop_value, Serializable)
            else [x.serialize() for x in prop_value]
            if isinstance(prop_value, (list, tuple))
            else prop_value
            for prop_name, prop_value
            in map(lambda prop_name: (prop_name, getattr(self, prop_name)), self.SERIALIZED_PROPS)
        }


class Client(Remote):
    def __init__(self):
        super(Client, self).__init__()
        self.add_extra('app', 3)
        self._is_authorized = False

    def get_news(self):
        return News(self._request('devrant/rants')['news'])

    def get_rants(self, sort=None, skip=0):
        return [Rant(self, data) for data in self._json_request(
            'devrant/rants',
            sort=sort,
            skip=skip
        )['rants']]

    def get_rant(self, id):
        return Rant.get(self, id)

    def log_in(self, username, password, raise_exception=True):
        response = self._json_request(
            'users/auth-token',
            'POST',
            username=username,
            password=password
        )
        if response['success']:
            data = response['auth_token']
            self.add_extra('token_key', data['key'])
            self.add_extra('token_id', data['id'])
            self.add_extra('user_id', data['user_id'])
            self._is_authorized = True
            return True
        else:
            if raise_exception:
                raise Exception('Auth failed, reason: {}'.format(response['error']))
            return False

    @property
    def is_authorized(self):
        return self._is_authorized


class News(Serializable):
    PROPS = (
        'action', 'body', 'footer', 'headline', 'height', 'id', 'type'
    )

    SERIALIZED_PROPS = PROPS

    def __init__(self, data):
        for key in self.PROPS:
            setattr(self, key, data[key])

    def __repr__(self):
        return u'<Image url="{}" size={}x{}>'.format(
            self.url,
            self.width,
            self.height
        )


class Image(Serializable):
    PROPS = (
        'url', 'width', 'height'
    )

    SERIALIZED_PROPS = PROPS

    def __init__(self, data):
        for key in self.PROPS:
            setattr(self, key, data[key])

    def __repr__(self):
        return u'<Image url="{}" size={}x{}>'.format(
            self.url,
            self.width,
            self.height
        )


class Tag(Serializable):
    def __init__(self, value):
        self.value = value

    def serialize(self):
        return self.value

    def __repr__(self):
        return u'<Tag "{}">'.format(self.value)


class Rant(Serializable):
    PROPS = (
        'attached_image', 'created_time', 'edited', 'id',
        'num_comments', 'num_upvotes', 'num_downvotes',
        'score', 'tags',
        'text',
        'user_avatar', 'user_id', 'user_score', 'user_username',
        'vote_state'
    )
    SERIALIZED_PROPS = PROPS + ('comments',)

    def __init__(self, client, data=None, comments=None, id_=None):
        super(Rant, self).__init__()
        self.client = proxy(client)

        for key in self.PROPS:
            setattr(self, key, None)

        self._set_data(data)
        self._set_id(id_)
        self._set_comments(comments)

    def __repr__(self):
        return u'<Rant id={} author="{}">'.format(
            self.id,
            self.user_username
        )

    def _set_id(self, id_):
        if id_:
            self.id = id_

    def _set_data(self, data):
        for key in Rant.PROPS:
            if data:
                setattr(self, key, data[key])
        if self.tags:
            self.tags = [Tag(tag_data) for tag_data in self.tags]
        if self.attached_image:
            self.attached_image = Image(self.attached_image)

    def _set_comments(self, comments):
        if comments:
            self._comments = [
                Comment(comment_data) for comment_data in comments
            ]

    def update(self):
        if not self.id:
            raise Exception('Cannot update Rant with unset ID.')
        result = Rant._load(self.client, self.id)
        self._set_data(result['rant'])
        self._set_comments(result['comments'])

    @classmethod
    def _load(cls, client, id):
        return client._json_request('devrant/rants/{}'.format(id))

    @classmethod
    def get(cls, client, id):
        data = cls._load(client, id)
        return Rant(client, data['rant'], data['comments'])

    @property
    def comments(self):
        if self._comments is None:
            # Comments not loaded yet
            self.comments = [
                Comment(comment_data) for comment_data in self._load(self.id)
            ]
        return self._comments

    def vote(self, up=True):
        # TODO: Make this assert a decorator instead.
        assert self.client.is_authorized, 'You must be authorized to perform this request.'

        # TODO: And this.
        if not self.id:
            raise Exception('Cannot update Rant with unset ID.')

        result = self.client._json_request(
            'devrant/rants/{}/vote'.format(self.id),
            'POST',
            vote=1 if up else 0
        )
        if result['success']:
            self._set_data(result['rant'])
        else:
            raise Exception('Failed to vote for rant, error was: {}'.format(result['error']))


class Comment(Serializable):
    PROPS = (
        'id', 'rant_id', 'body',
        'num_upvotes', 'num_downvotes',
        'score', 'created_time',
        'vote_state',
        'user_id', 'user_username', 'user_score', 'user_avatar',
    )

    SERIALIZED_PROPS = PROPS

    def __init__(self, data):
        super(Comment, self).__init__()

        for key in self.PROPS:
            setattr(self, key, data[key])

    def __repr__(self):
        return u'<Comment id={} rant_id={} author="{}">'.format(
            self.id,
            self.rant_id,
            self.user_username
        )
