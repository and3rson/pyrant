from __future__ import unicode_literals
import urllib
import urllib2
import json


class Remote(object):
    URL = 'https://www.devrant.io/api/devrant'
    APP_ID = 3

    def __init__(self):
        pass

    @classmethod
    def _request(cls, method, **kwargs):
        kwargs['app'] = Remote.APP_ID
        url = Remote.URL + '/' + method + '?' + urllib.urlencode(kwargs)
        response = urllib2.urlopen(
            url
        )
        return response.read()

    @classmethod
    def _json_request(cls, url, **kwargs):
        return json.loads(cls._request(url, **kwargs))


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

    def get_news(self):
        return News(self._request('rants')['news'])

    def get_rants(self, sort=None, skip=0):
        return [Rant(data) for data in self._json_request(
            'rants',
            sort=sort,
            skip=skip
        )['rants']]


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


class Rant(Remote, Serializable):
    PROPS = (
        'attached_image', 'created_time', 'edited', 'id',
        'num_comments', 'num_upvotes', 'num_downvotes',
        'score', 'tags',
        'text',
        'user_avatar', 'user_id', 'user_score', 'user_username',
        'vote_state'
    )
    SERIALIZED_PROPS = PROPS + ('comments',)

    def __init__(self, data=None, comments=None, id_=None):
        super(Rant, self).__init__()

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
        self.tags = [Tag(tag_data) for tag_data in self.tags]
        if self.attached_image:
            self.attached_image = Image(self.attached_image)

    def _set_comments(self, comments):
        if comments:
            self._comments = [
                Comment(comment_data) for comment_data in comments
            ]
        else:
            self._comments = None

    def update(self):
        if not self.id:
            raise Exception('Cannot update Rant with unset ID.')
        result = Rant._load(self.id)
        self._set_data(result['rant'])
        self._set_comments(result['comments'])

    @classmethod
    def _load(cls, id):
        return cls._json_request('rants/{}'.format(id))

    @classmethod
    def get(cls, id):
        data = cls._load(id)
        return Rant(data['rant'], data['comments'])

    @property
    def comments(self):
        if self._comments is None:
            # Comments not loaded yet
            self.comments = [
                Comment(comment_data) for comment_data in self._load(self.id)
            ]
        return self._comments


class Comment(Remote, Serializable):
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

    @classmethod
    def get(cls, id):
        data = cls._json_request('rants/{}'.format(id))
        return Rant(data['rant'], data['comments'])
