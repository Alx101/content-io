# coding=utf-8
from __future__ import unicode_literals

from cio.conf import settings
from cio.node import Node


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

    def _load(self, node):
        """
        Return plugin data and modify for raw node
        """
        # if isinstance(node, Node):

        node.content = self.load(node.content)
        node = self._render(node)
        # else:
        #     source = node.pop('content')
        #     node['data'] = self.load(source)
        #     node = self._render(node)
        return node

    def save(self, data):
        """
        Persist external plugin resources and return content string for plugin data
        """
        return data

    def _save(self, node):
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

    def _delete(self, node):
        """
        Delete external plugin resources
        """
        self.delete(node.content)

    def render(self, data):
        """
        Render plugin
        """
        return data

    def _render(self, node):
        """
        Prepares node for render
        """
        #if isinstance(node, Node):
        node.content = self.render(node.content)
        return node
        # else:
        #     node['content'] = self.render(node['data'])
        #     return node
