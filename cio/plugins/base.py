# coding=utf-8
from __future__ import unicode_literals

from cio.conf import settings


class BasePlugin(object):

    ext = None

    @property
    def settings(self):
        return settings.get(self.ext.upper(), {})

    def load(self, content):
        """
        Return plugin data for content string
        """
        return content

    def loads(self, node):
        """
        Return plugin data and modify for raw node
        """
        source = node.pop('content')
        data = node['data'] = self.load(source)
        node['content'] = self.render(data)
        return node

    def save(self, data):
        """
        Persist external plugin resources and return content string for plugin data
        """
        return data

    def saves(self, node):
        """
        Perform action on node, persist external plugin resources and return content string for plugin data
        """
        node.content = self.save(node.content)
        return node

    def publish(self, node):
        """
        Perform actions on publish and return node to persist
        """
        return node

    def delete(self, data):
        """
        Delete external plugin resources
        """
        pass

    def render(self, data):
        """
        Render plugin
        """
        return data
