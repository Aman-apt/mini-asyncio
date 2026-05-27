
from futures import Future


class Task(Future):
    """Task wraps the future to drive the coroutine to it's completion.
    Also because task becomes awaitbale itself. so we can await task
    """
    def __init__(self, coro):
        super().__init__()
        self._coro = coro
        self._step = _step()

    def _step(self):
        # Push coroutine one step forward 
        try:
            # Start the coroutine and Register a callback on the coroutine
            yeilded = self._coro.send(None)
            yeilded.add_done_callback(self._wakeup)
        except StopIteration as e:
            self._set_result(e.value)

    def _wakeup(self, future):
        try:
            yielded = self._coro.send(future.result())
            
            # if coroutine has another future register it .
            yielded.add_done_callack(self._wakeup)
        except StopIteration as e:
            self._set_result(e.value)

    def done(self):
        pass

    def cancel(self):
        pass
