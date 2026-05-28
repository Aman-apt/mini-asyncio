from futures import Future


class Task(Future):
    """Task wraps the future to drive the coroutine to it's completion.
    Also because task becomes awaitbale itself. so we can await task
    """

    def __init__(self, coro):
        super().__init__()
        self._coro = coro
        self._step()  # call step immediately

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

    def done(self):
        pass

    def cancel(self):
        pass


async def my_corob():
    f = Future()
    import threading, time

    threading.Thread(target=lambda: (time.sleep(0.3), f.set_result(99))).start()
    result = await f
    print(f"Coro got: {result}")
    return "done"


t = Task(my_corob())
import time

time.sleep(0.5)
print(f"Task Result: {t.result()}")
