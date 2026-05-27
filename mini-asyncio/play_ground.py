

# How do i start even making this things
# Phase 1 — The Bare Event Loop (Callbacks Only)
"""
Build a loop that:
- Has a queue of callbacks to run ("ready queue")
- Has a selector that watches file descriptors
- On each iteration: ask the selector "what's ready?", move those callbacks to the ready queue, then run everything in the ready queue
No coroutines yet. Just understand the tick of the loop and how I/O events become function calls.
"""

from collections impor deque

callbacks = deque()

class EventLoop:
    def __init__(self, func):
        pass

    def run(self):
        while True:
            pass


