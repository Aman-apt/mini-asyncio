# Futures.py
# Futures is the underlying 

class Future:
    def __init__(self):
        self._result = None
        self._done = False
        self._callback = []

    def set_result(self, value):
        if self._done:
            raise Exception("Future already done")
        self._result = value
        self._done = True

        # Notifies the coroutine that futures has finished
        for callback in self._callback:
            callback(self)

    def result(self):
        if not self._done:
            raise Exception("Not ready yet")
        return self._result

    def add_done_callback(self, fn):
        if self._done: # fire all the callbacks immediately
            fn(self)
        else:
            self._callback.append(fn)

    def done(self):
        return self._done

    def __await__(self):
        if not self._done:
            yield self
        return self._result

f = Future()

# def on_done(future):
#     print(f"Callback fired! Result {future.result()}")
#
# f.add_done_callback(on_done)
# print(f"Done before set_result: {f.done()}")
# f.set_result(230)
# f.set_result(32)
# print(f"Done after the set_result {f.done()}")
# print(f"Result: {f.result()}")

async def my_coro():
    f = Future()

    # Simulate something filling the future after the coro parks
    import threading
    def fill_it():
        import time
        time.sleep(0.5)
        f.set_result("Hello")
    threading.Thread(target=fill_it).start()
    result = await f
    print(f"Cor got: {result}")

coro = my_coro()
try:
    yielded = coro.send(None)
    print(f"Coro Pause, yielded: {yielded}")

    # wait for the future ot be done(in real life the loop does this)
    import time
    while not yielded.done():
        time.sleep(0.5)
    coro.send(None)
except StopIteration:
    pass


