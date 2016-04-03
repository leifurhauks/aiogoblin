#!/usr/bin/env python
# BORROWED FROM ZEROMQ BOOK EXAMPLES
# Simple echo worker
"""
synopsis:
    Request-reply service in Python
    Connects REP socket to tcp://localhost:5560
    Expects "Hello" from client, replies with "World"
    Modified for async/ioloop: Dave Kuhlman <dkuhlman(at)davekuhlman(dot)org>
usage:
    python rrworker.py
notes:
    To run this, start rrbroker.py, any number of instances of rrworker.py,
    and rrclient.py.
"""

import sys
import zmq
from zmq.asyncio import Context, ZMQEventLoop
import asyncio


@asyncio.coroutine
def run_worker(context):
    socket = context.socket(zmq.REP)
    socket.connect("tcp://localhost:5560")
    while True:
        message = yield from socket.recv()
        print("Received request: %s" % message)
        yield from socket.send(message)
        print("Sent reply: {}".format(message))


@asyncio.coroutine
def run(loop):
    context = Context()
    yield from run_worker(context)


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
