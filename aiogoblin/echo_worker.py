import asyncio
import sys
import zmq
from zmq.asyncio import Context, ZMQEventLoop


async def run_worker(context):
    worker = context.socket(zmq.DEALER)
    identity = "Worker1"  # This is just for a convenient example
    identity = identity.encode('utf-8')
    worker.setsockopt(zmq.IDENTITY, identity)
    worker.connect("tcp://localhost:5560")
    while True:
        message = await worker.recv_multipart()
        address = message[0]
        print("Received request: %s" % message)
        await worker.send_multipart(message)

        # Illustrate the streaming functionality
        await worker.send_multipart([address, b'', b'closing'])
        print("Sent reply: {}".format(message))


async def run(loop):
    context = Context()
    await run_worker(context)


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
