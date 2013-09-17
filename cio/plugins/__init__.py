from .exceptions import UnknownPlugin
from ..conf import settings
from ..utils.imports import import_class
from ..utils.uri import URI


class PluginLibrary(object):

    def __init__(self):
        self.load()

    def __iter__(self):
        return self._plugins.iterkeys()

    def load(self):
        self._plugins = {}
        for plugin_path in settings.PLUGINS:
            self.register(plugin_path)

    def register(self, plugin):
        if isinstance(plugin, basestring):
            try:
                plugin_class = import_class(plugin)
                self.register(plugin_class)
            except ImportError as e:
                raise ImportError('Could not import content-io plugin "%s" (Is it on sys.path?): %s' % (plugin, e))
        else:
            self._plugins[plugin.ext] = plugin()

    def get(self, ext):
        if not ext in self._plugins:
            raise UnknownPlugin
        return self._plugins[ext]

    def resolve(self, uri):
        uri = URI(uri)
        return self.get(uri.ext)


plugins = PluginLibrary()
