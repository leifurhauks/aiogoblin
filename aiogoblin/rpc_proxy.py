"""Simple rpc proxy, inpspired by Pulsar"""

import struct

import aiohttp


class WSCall:
    slots = ('_client', '_name')

    def __init__(self, client, name):
        self._client = client
        self._name = name

    def __repr__(self):
        return self._name
    __str__ = __repr__

    @property
    def url(self):
        return self._client.url

    @property
    def name(self):
        return self._name

    def __call__(self, *args, **kwargs):
        return self._client._call(self._name, *args, **kwargs)


class WSRPCProxy:

    def __init__(self, url, loop=None, **kwargs):
        self._url = url
        self._session = aiohttp.ClientSession(loop=loop)

    @property
    def url(self):
        return self._url

    @property
    def session(self):
        return self._session

    @property
    def _loop(self):
        return self._session._loop

    def makeid(self):
        '''Can be re-implemented by your own Proxy'''
        return gen_unique_id()

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, self.__url)

    def __str__(self):
        return self.__repr__()

    def __getattr__(self, name):
        return WSCall(self, name)

    async def _call(self, name, blob=b""):
        method = name.encode("utf-8")
        data = struct.pack(
            "@I%ds%ds" % (len(method), len(blob)), len(method), method, blob)
        client = await self._session.ws_connect(self._url)
        client.send_bytes(data)
        client.send_str("close")
        return client
