"""Echo client"""

import asyncio

import aiohttp

from rpc_proxy import WSRPCProxy


@asyncio.coroutine
def echo_client():
    proxy = WSRPCProxy('http://127.0.0.1:8080')
    client = yield from proxy.echo(b"hello")
    try:
        while True:
            resp = yield from client.receive()
            if not resp.data:
                break
            print(resp.data)
    finally:
        yield from client.close()
        yield from proxy.session.close()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(echo_client())
    finally:
        loop.close()
