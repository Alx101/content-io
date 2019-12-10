# coding=utf-8
from __future__ import unicode_literals
from ..conf import settings
from collections import OrderedDict
import six
from six.moves.urllib.parse import parse_qs, urlencode, unquote_plus, quote_plus


class URI(six.text_type):

    @staticmethod
    def __new__(cls, uri=None, scheme=None, namespace=None, path=None, ext=None, version=None, query=None):
        if isinstance(uri, URI):
            return uri
        elif uri is not None:
            return URI._parse(uri)
        else:
            return URI._render(scheme, namespace, path, ext, version, query)

    @classmethod
    def _parse(cls, uri):
        base, _, version = uri.partition(settings.URI_VERSION_SEPARATOR)

        query = OrderedDict()
        if settings.URI_QUERY_SEPARATOR in base:
            _base, _, querystring = base.rpartition(settings.URI_QUERY_SEPARATOR)
            querystring = str(querystring)
            query_holder = parse_qs(querystring, keep_blank_values=True)
            if query_holder is '':
                query = OrderedDict()
            else:
                reference_parts = querystring.split('&')
                for pair in reference_parts:
                    if '=' in pair:
                        key, _, _ = pair.partition('=')
                    else:
                        key = pair
                    if key is not '':
                        value = query_holder[key]
                        if len(value) > 0:
                            query[key] = value[len(value)-1].decode('utf-8') if six.PY2 else value[len(value)-1]
                        else:
                            query[key] = []
            base = _base
        else:
            query = OrderedDict()

        scheme, _, path = base.rpartition(settings.URI_SCHEME_SEPARATOR)
        namespace, _, path = path.rpartition(settings.URI_NAMESPACE_SEPARATOR)
        _path, _, ext = path.rpartition(settings.URI_EXT_SEPARATOR)
        if '/' in ext:
            ext = ''
        else:
            path = _path

        if not path and ext:
            path, ext = ext, ''

        return cls._render(
            scheme or settings.URI_DEFAULT_SCHEME,
            namespace or None,
            path,
            ext or None,
            version or None,
            query or None
        )

    @classmethod
    def _render(cls, scheme, namespace, path, ext, version, query):
        def parts_gen():
            if scheme:
                yield scheme
                yield settings.URI_SCHEME_SEPARATOR
            if namespace:
                yield namespace
                yield settings.URI_NAMESPACE_SEPARATOR
            if path:
                yield path
                if ext:
                    yield settings.URI_EXT_SEPARATOR
                    yield ext
                if query:
                    yield settings.URI_QUERY_SEPARATOR
                    temp_query = OrderedDict()
                    for (key, item) in query.items():
                        new_key, new_item = cls._parse_query_param_pair(key, item)
                        temp_query[new_key] = new_item
                    querystring = urlencode(temp_query)
                    yield querystring
                if version:
                    yield settings.URI_VERSION_SEPARATOR
                    yield version

        uri = six.text_type.__new__(cls, ''.join(parts_gen()))
        uri.scheme = scheme
        uri.namespace = namespace
        uri.path = path
        uri.ext = ext
        uri.version = version
        uri.query = query
        return uri

    @classmethod
    def _parse_query_param_pair(cls, key, values):
        if isinstance(values, list):
            newvalues = [
                value.encode('utf-8')
                for value in values
            ]
            return key.encode('utf-8'), newvalues
        else:
            return key.encode('utf-8'), values.encode('utf-8')

    def is_absolute(self):
        """
        Validates that uri contains all parts except version
        """
        return self.namespace and self.ext and self.scheme and self.path

    def has_parts(self, *parts):
        return not any(getattr(self, part, None) is None for part in parts)

    def clone(self, **parts):
        part = lambda part: parts.get(part, getattr(self, part))
        args = (part(p) for p in ('scheme', 'namespace', 'path', 'ext', 'version', 'query'))
        return URI._render(*args)

    class Invalid(Exception):
        pass
