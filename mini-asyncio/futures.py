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
        return self._result()

f = Future()

def on_done(future):
    print(f"Callback fired! Result {future.result()}")
#paste what you get. Don't move on until this works — every single thing we build after this sits on top of
f.add_done_callback(on_done)
print(f"Done before set_result: {f.done()}")
f.set_result(230)
f.set_result(32)
print(f"Done after the set_result {f.done()}")
print(f"Result: {f.result()}")

