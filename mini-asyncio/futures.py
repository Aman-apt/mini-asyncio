"""
futures.py — The bedrock of mini-asyncio.

A Future represents a value that doesn't exist yet.  It is the rendezvous point between a *producer* (whoever resolves the result) and a *consumer*
(the coroutine that awaits it).

CPython asyncio design note
───────────────────────────
For Context Everything is insipired by the Cpython/lib/asyncio.
"""

from ast import Call
from tkinter import image_names
from typing import Generic, Callable, Any, Generator, Literal
import enum


class FutureState(enum.Enum):
    PENDING = "PENDING"
    CANCELLED = "CANCELLED"
    FINISHED = "FINISHED"


class CancelledError(BaseException):
    """Raise inside a couroutine where task driving it is cancelled"""


class InvalidStateError(Exception):
    """Raise Error when the future operation is not a valid state"""


class Future:
    """Future is a low-level awaitble that holds a pending result"""

    _loop: "EventLoop | None" = None  # set eventloop at creation time

    def __init__(self, loop: "EventLoop | None" = None) -> None:
        self._state: FutureState = FutureState.PENDING
        self._exception: BaseException = None
        self._result: Any = None
        self._callback: Callable = []
        self._loop = loop

    def done(self) -> bool:
        return self._state is not FutureState.PENDING

    def cancelled(self) -> bool:
        return self._state is FutureState.CANCELLED

    def result(self) -> Any:
        if self._state is FutureState.CANCELLED:
            raise CancelledError("Future has been cancelled")
        if self._state is not FutureState.FINISHED:
            raise InvalidStateError("Future is still pending")
        return self._result

    # Mutations for states, excepitons, result and cancel

    def set_result(self, value: Any) -> None:
        if self._state is not FutureState.PENDING:
            raise InvalidStateError(f"set_result() was called on {
                                    self._state.value} Future")

        self._result = value
        self._state = FutureState.FINISHED
        self.schedule_callback

    def set_exception(self, exc: BaseException) -> None:
        if self._state is not FutureState.PENDING:
            raise InvalidStateError(f"set_exception() was called on {
                                    self._state.value} Future")

        if isinstance(exc, type):
            exc = exc()
        if isinstance(exc, StopIteration):
            raise TypeError("Cannot call stopIteration on the set_Exception")

        self._exception = exc
        self._state = FutureState.FINISHED
        self.schedule_callback()

    def cancel(self) -> Literal[True]:
        if self._state is not FutureState.PENDING:
            raise InvalidStateError("Future either finshed or got cancelled")
        self._state = FutureState.CANCELLED
        self._schedule_callback()
        return True

    # Callback implemenatations

    def add_done_callback(self, cb: Callable) -> None:
        """Register a callback of _wakeup that is waiting of currently waiting future"""
        if self._state is not FutureState.PENDING:
            if self.done():
                cb(self)
            else:
                self._callback.append(cb)

    def remove_done_callback(self, cb: Callable) -> int:
        before = len(self._callback)
        self._callback = [x for x in self._callback if f != cb]
        return before - len(self._callback)

    def schedule_callback(self, cb: callable) -> None:
        """Schedule the callback for that waiting future"""
        callback, self._callback = self._callback, []
        if not callback:
            return
        for cb in self._callback:
            if self.done():
                cb(self)
            else:
                cb(self)

    # __awaitable protocl ___
    def __await__(self) -> Generator[Any]:
        """A protocol to connect the bridge between Task and Coroutine."""
        if not self.done():
            yield self
        return self._result

    def __repr__(self) -> str:
        pass

if __name__ == "__main__":

    def on_done(future):
        import time
        f = Future()
        result = f.set_result(232)
        time.sleep(2)
        print(f"set_result {future.result()}, {result}")
    
    f = Future()
    on_done(f)
    f.add_done_callback(on_done)
    f.set_result(23)
    print(f.result())
