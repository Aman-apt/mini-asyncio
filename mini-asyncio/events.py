"""
Inputs: ready/callbacks work(timers, I/O completions, scheduled callbacks
, and task/futures)
Output: executed Callbacks, resumed coroutines and Completed results(or exception) as outputs

At core an event loop is a loop that: pick ready work → run it until it yields/blocks/completes
→ update state and queues → wait (block) for new OS events or timers if nothing is ready → repeat.
this maps to a while loop pattern.
The important difference from a naïve while loop is the scheduling/dispatch infrastructure:
queues (ready queue, timer heap), an OS-level wait (epoll/kqueue/select), and the policy for microtasks vs macrotasks.
Those make it efficient and correct under concurrency demands.


At core an event loop is a loop that: pick ready work → run it until it yields/blocks/completes → update state and queues →
wait (block) for new OS events or timers if nothing is ready → repeat. This maps to a while loop pattern.
The important difference from a naïve while loop is the scheduling/dispatch infrastructure: queues (ready queue, timer heap),
an OS-level wait (epoll/kqueue/select), and the policy for microtasks vs macrotasks. Those make it efficient and correct under concurrency demands.


"""

import selectors
import collections
import heapq
from futures import Future
from task import Task


class EventLoop:
    def __init__(self):
        self._schedule = []
        self._ready = collections.deque()  # for the ready callbacks
        self._callback = []
        self._default_executor = (
            selectors.DefaultSector()
        )  # for selector.epoll(For linux based)
        self._stopping = False
        self._closed = False
        self._timer_cacelled_count = 0
        self._internal_fds = 0  # file descriptors()

    def run_forever(self):
        pass
