"""Echo client"""

import asyncio

import aiohttp

from rpc_proxy import WSRPCProxy


async def echo_client():
    proxy = WSRPCProxy('http://127.0.0.1:8080')
    client = await proxy.echo(b"hello")
    try:
        while True:
            resp = await client.receive()
            if resp.tp == aiohttp.MsgType.close:
                break
            print(resp.data)
    finally:
        await client.close()
        await proxy.session.close()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(echo_client())
    finally:
        loop.close()
