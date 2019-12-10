# coding=utf-8
from __future__ import unicode_literals
from ..conf import settings
from collections import OrderedDict
import six
from six.moves.urllib.parse import parse_qs, urlencode, unquote, quote


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
        scheme, _, path = base.rpartition(settings.URI_SCHEME_SEPARATOR)
        namespace, _, path = path.rpartition(settings.URI_NAMESPACE_SEPARATOR)
        _path, _, ext = path.rpartition(settings.URI_EXT_SEPARATOR)
        query = OrderedDict()
        if '/' in ext:
            ext = ''
        else:
            if '?' in ext:
                _ext, _, querystring = ext.rpartition(settings.URI_QUERY_SEPARATOR)
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
                            if len(value) == 1:
                                query[key] = value[0]
                            else:
                                query[key] = value
                ext = _ext
            else:
                query = OrderedDict()
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
                if version:
                    yield settings.URI_VERSION_SEPARATOR
                    yield version
                if query:
                    yield settings.URI_QUERY_SEPARATOR
                    temp_query = OrderedDict()
                    for (key, item) in query.items():
                        new_key, new_item = cls._parse_query_param_pair(key, item)
                        temp_query[new_key] = new_item
                    querystring = unquote(urlencode(temp_query, True))
                    if six.PY2:
                        yield querystring.decode('utf-8')
                    else:
                        yield querystring

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
