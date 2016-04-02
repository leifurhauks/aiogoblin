import aiohttp
from aiohttp import web
from aiogoblin.rpc import WSRPCHandler


class RPC(WSRPCHandler):
    """Application RPC. RPC methods should start with the `rpc_` prefix"""

    async def rpc_echo(self, ws, method, blob):
        ws.send_bytes(blob)


def init(argv):
    rpc = RPC()
    app = web.Application()
    # Pass the websocket handler to the router, not the rpc method...
    app.router.add_route('GET', '/', rpc.websocket_handler)
    return app
