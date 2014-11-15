import asyncio
import time


@asyncio.coroutine
def yielding_consumer_func(package, sleep_time=5):
    if package is not None:
        print('Yielding: Consuming {}'.format(package.payload))
    else:
        print('Yielding: The queue is empty')

    for i in range(1, sleep_time+1):
        print('Yielding: Sleeping',i)
        yield from asyncio.sleep(1)

    print('Done consuming')


def blocking_consumer_func(package):
    if package is not None:
        print('Blocking: Consuming {}'.format(package.payload))
    else:
        print('Blocking: The queue is empty')

    print('Blocking: Done consuming')
