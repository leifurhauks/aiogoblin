import asyncio
import logging

import aiohttp
from aiohttp import web

import zmq
from zmq.asyncio import Context, ZMQEventLoop

from rpc import WSRPCHandler

logger = logging.getLogger('server')


class RPC(WSRPCHandler):
    """Application RPC. RPC methods should start with the `rpc_` prefix"""

    def __init__(self, loop=None):
        if loop is None:
            loop = asyncio.get_event_loop()
        self._loop = loop
        self._context = Context()

    async def rpc_echo(self, ws, method, blob):
        ws.send_bytes(blob)

    async def rpc_echo_worker(self, ws, method, blob):
        logger.debug('in rpc_echo_worker')
        socket = self._context.socket(zmq.DEALER)
        socket.connect('tcp://localhost:5559')
        logger.debug('socket: %s', socket)
        await socket.send_multipart([b'', blob])
        logger.debug('sent blob: %s', blob)

        message = await socket.recv_multipart()
        logger.debug('got message from socket: %s', message)
        assert message[-1] == blob, '%s does not equal %s' % (
            message[-1], blob)
        ws.send_bytes(message[-1])

        # Echo worker streams `closing` after echoing
        message = await socket.recv_multipart()
        assert message[-1] == b'closing', '%s does not equal %s' % (
            message[-1], 'closing')
        ws.send_bytes(message[-1])


# CLI
def init_function(argv):
    rpc = RPC()
    app = web.Application()
    # Pass the websocket handler to the router, not the rpc method...
    app.router.add_route('GET', '/', rpc.websocket_handler)
    return app


async def init(loop):
    rpc = RPC(loop=loop)
    app = web.Application(loop=loop)
    app.router.add_route('GET', '/', rpc.websocket_handler)
    handler = app.make_handler()
    srv = await loop.create_server(handler, '127.0.0.1', 8080)
    print('Server started at http://127.0.0.1:8080')
    return srv, handler


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    loop = ZMQEventLoop()
    asyncio.set_event_loop(loop)
    srv, handler = loop.run_until_complete(init(loop))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        loop.run_until_complete(handler.finish_connections())
