"""Echo client"""

import asyncio
import logging

import aiohttp

from rpc_proxy import WSRPCProxy

logger = logging.getLogger('client')


async def echo_client():
    logger.debug('in echo client')
    proxy = WSRPCProxy('http://127.0.0.1:8080')
    phrase = b'hello'
    client = await proxy.echo(phrase)
    try:
        while True:
            resp = await client.receive()
            if resp.tp == aiohttp.MsgType.close:
                break
            print(resp.data)
    finally:
        await client.close()
        await proxy.session.close()


async def echo_worker_client():
    logger.debug('in echo_worker_client')
    proxy = WSRPCProxy('http://127.0.0.1:8080')
    phrase = b'world'
    client = await proxy.echo_worker(phrase)
    logger.debug('echo_worker_client sent request')
    try:
        while True:
            resp = await client.receive()
            logger.debug('got resp: %s', resp)
            if resp.tp == aiohttp.MsgType.close:
                break
            print(resp.data)
    finally:
        await client.close()
        await proxy.session.close()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(echo_client())
        logger.debug('ran echo_client')
        loop.run_until_complete(echo_worker_client())
    finally:
        loop.close()
