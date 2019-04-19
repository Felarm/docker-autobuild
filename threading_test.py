import asyncio

@asyncio.coroutine
def slow():
    yield from asyncio.sleep(1)

    return 'slow done'

def moreslow():
    yield from asyncio.sleep(10)
    return 'moreslow done'

def got_result(future):
    print(future.result())

loop = asyncio.get_event_loop()

task1 = loop.create_task(slow())
task1.add_done_callback(got_result)
task2 = loop.create_task(moreslow())
task2.add_done_callback(got_result)

loop.run_until_complete(task1)
loop.run_until_complete(task2)