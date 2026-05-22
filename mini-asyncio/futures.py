
#Note: Not a proper implementation just a rough example. 
# Things to improve:
# Add a proper Exception handling, Logging and make it robuts to handle edge cases

class Future:
    """
    Future Class that is responsible for handling the coroutine object
    and yield the future out
    """
    _loop = None

    def __init__(self, loop=None):
        self._result = None
        self._done = False
        self._callbacks = []
    
    def get_loop(self):
        """Return the event loop the future is bound to"""
        loop = self._loop
        if loop is None:
            raise RuntimeError("Future object is Not initialized")
        return loop

    def set_result(self, value):
        """
        set the callback as a result
        """
        self._result = value
        self._done = True
        for cb in self._callbacks: #fire everyone waiting(sheduling)
            cb(self)
    
    def add_done_callbacks(self, fn):
        self._callbacks.append(fn)
    
    def result(self):
        return self._result
    