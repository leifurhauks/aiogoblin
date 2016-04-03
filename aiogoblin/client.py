"""Echo client"""

import asyncio

import aiohttp

from rpc_proxy import WSRPCProxy


async def echo_client():
    proxy = WSRPCProxy('http://127.0.0.1:8080')
    phrase = b'hello'
    client = await proxy.echo(phrase)
    try:
        while True:
            resp = await client.receive()
            if resp.tp == aiohttp.MsgType.close:
                break
            assert resp.data == phrase, "%s does not equal %s" % (resp.data,
                                                                  phrase)
            print(resp.data)
    finally:
        await client.close()
        await proxy.session.close()


async def echo_worker_client():
    proxy = WSRPCProxy('http://127.0.0.1:8080')
    phrase = b'world'
    client = await proxy.echo_worker(phrase)
    try:
        while True:
            resp = await client.receive()
            if resp.tp == aiohttp.MsgType.close:
                break
            assert resp.data == phrase, "%s does not equal %s" % (resp.data,
                                                                  phrase)
            print(resp.data)
    finally:
        await client.close()
        await proxy.session.close()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(echo_client())
        loop.run_until_complete(echo_worker_client())
    finally:
        loop.close()
