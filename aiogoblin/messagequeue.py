import asyncio
import sys

import zmq
from zmq.asyncio import Context, Poller, ZMQEventLoop


async def run_broker(context):
    # Prepare our context and sockets
    frontend = context.socket(zmq.ROUTER)
    backend = context.socket(zmq.ROUTER)
    frontend.bind("tcp://*:5559")
    backend.bind("tcp://*:5560")
    # Initialize poll set
    poller = Poller()
    poller.register(frontend, zmq.POLLIN)
    poller.register(backend, zmq.POLLIN)
    # Switch messages between sockets
    while True:
        socks = await poller.poll()
        socks = dict(socks)

        if socks.get(frontend) == zmq.POLLIN:
            frames = await frontend.recv_multipart()
            print('received from frontend: {}'.format(frames))
            # Add the worker ident to the envelope - simplified for example.
            frames.insert(0, b'Worker1')
            await backend.send_multipart(frames)

        if socks.get(backend) == zmq.POLLIN:
            frames = await backend.recv_multipart()
            msg = frames[1:]  # Slice off worker ident
            print('received from backend: {}'.format(frames))
            await frontend.send_multipart(msg)


async def run(loop):
    context = Context()
    await run_broker(context)


def main():
    args = sys.argv[1:]
    if len(args) != 0:
        sys.exit(__doc__)
    try:
        loop = ZMQEventLoop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(run(loop))
    except KeyboardInterrupt:
        print('\nFinished (interrupted)')


if __name__ == '__main__':
    main()
