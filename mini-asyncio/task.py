import asyncio

from futures import Future


class Task(Future):
    """Task wraps the future to drive the coroutine to it's completion.
    Also because task becomes awaitbale itself. so we can await task
    """

    def __init__(self, coro):
        super().__init__()
        self._coro = coro
        self._running = False
        self._done = False

    def _step(self):
        # Push coroutine one step forward
        try:
            # Start the coroutine and Register a callback on the coroutine
            yeilded = self._coro.send(None)
            yeilded.add_done_callback(self._wakeup)
        except StopIteration as e:
            self.set_result(e.value)

    def _wakeup(self, future):
        try:
            yielded = self._coro.send(future.result())

            # if coroutine has andistribution'sother future register it .
            yielded.add_done_callback(self._wakeup)
        except StopIteration as e:
            self.set_result(e.value)

async def c1():
    f = Future()
    result = await f 
    print(f"Result of Future: {result}")
    return(f"StopIteraton of Task: {result.result()}")

async def main():
    t1 = c1
   
    task = Task(t1)
    task.set_result("Hello kya chal rha hai")
    task.add_done_callback(task._wakeup()) 
    print(task.result())

asyncio.run(main())
