
## What's Actually at the Core of asyncio

Before prerequisites, you need to know what you're actually building. asyncio at its heart is three things composed together:

**1. A scheduler** — something that decides which coroutine runs next and when.
**2. An I/O multiplexer** — something that asks the OS "tell me when any of these file descriptors are ready" so the scheduler knows when to wake a coroutine up.
**3. A coroutine driver** — something that can pause and resume Python coroutines by interacting with the generator protocol underneath them.
Everything else (Tasks, Futures, `gather`, `sleep`, Semaphore) is built on top of these three primitives.

---

## Prerequisites — What You Need to Know First

### Layer 1: Python Generator Protocol (Non-negotiable foundation)

This is the most critical prerequisite. `async/await` is syntactic sugar over generators. You need to deeply understand:

- How `yield` suspends a function and hands control back to the caller
- The `.send(value)` method — how you push a value *into* a suspended generator
- The `.throw()` method — how exceptions propagate into generators
- `StopIteration` and how generators signal completion
- `yield from` — how it delegates to a sub-generator and handles the full send/throw/close protocol transparently

The key mental model: **a coroutine is just a generator that yields its control flow upward to whoever is driving it** — which is the event loop.

### Layer 2: How async/await Desugars

Once you understand generators, you need to see that `async def` creates a coroutine object, and `await` is essentially `yield from` with some type-checking added. If you `await` something, you're suspending the current coroutine and yielding a "I'm waiting on this" signal up to the event loop.

Read PEP 342 and PEP 492 — not for implementation details, but to see the *design decisions* and why they were made.

### Layer 3: OS I/O Concepts

This is the systems layer. You need to understand:

- **File descriptors** — in Unix, everything (network sockets, files, pipes) is a file descriptor (an integer). This is the primitive the OS uses for I/O.
- **Blocking vs non-blocking I/O** — by default a `recv()` call blocks your whole thread. Non-blocking mode makes it return immediately with "not ready yet."
- **`select` / `poll` / `epoll`** — these are OS system calls that let you give the kernel a list of file descriptors and say "wake me up when any of these are ready to read or write." This is how one thread can watch thousands of connections simultaneously. `epoll` (Linux) is the modern efficient version.
- **The event notification model** — the OS doesn't push data to your program; your program asks the OS to tell it when data is available, then goes and fetches it.

Python's `selectors` module is a cross-platform wrapper over these system calls. You'll use it in your implementation, but you need to understand what it's wrapping.

### Layer 4: The Callback Mental Model

Before coroutines existed, async I/O was done with callbacks — "call this function when the socket is ready." Understanding callback-based event loops first makes the coroutine-based version much clearer. Node.js is the canonical example. Your mini-asyncio will likely go through a callback phase before a coroutine phase.

---

## How I Would Approach the Build — Phases

### Phase 1 — The Bare Event Loop (Callbacks Only)

Build a loop that:
- Has a queue of callbacks to run ("ready queue")
- Has a selector that watches file descriptors
- On each iteration: ask the selector "what's ready?", move those callbacks to the ready queue, then run everything in the ready queue

No coroutines yet. Just understand the tick of the loop and how I/O events become function calls.

### Phase 2 — Introduce Futures

A `Future` is a box that holds a result that doesn't exist yet. It has:
- A state (pending / done)
- A stored result or exception
- A list of callbacks to call when it's resolved

This is the bridge between "an I/O event happened" and "a coroutine should wake up." The event loop resolves the Future; the Future calls its callbacks; those callbacks wake up the coroutine.

### Phase 3 — Introduce Tasks (The Coroutine Driver)

A `Task` wraps a coroutine and drives it. Its job is:
- Call `.send(None)` to start the coroutine
- When the coroutine yields a Future, attach a callback: "when this Future resolves, send the result back into the coroutine"
- When the coroutine raises `StopIteration`, it's done — resolve the Task's own Future

This is the beating heart of the whole system. A Task is how a coroutine and the event loop communicate.

### Phase 4 — Wire up I/O Primitives

Now build `async_sleep` and babasic socketsic socket read/write. These are functions that:
- Register a file descriptor or timer with the event loop
- Return a Future
- When the OS signals ready (or the timer fires), resolve the Future, which wakes the Task

### Phase 5 — Build `gather`

Now that you have Tasks and Futures, `gather` is just: create a Task for each coroutine, return a Future that resolves when all of them are done. This is where the real power becomes visible.

---

## Resources — In Order

**Start here:**
- **David Beazley — "Python Concurrency from the Ground Up" (PyCon 2015)** — the single best resource. He builds a working event loop live. Watch it multiple times.
- **David Beazley — "A Curious Course on Coroutines and Concurrency"** — goes deep on the generator protocol.

**Go deeper:**
- **"500 Lines or Less" — the asyncio web crawler chapter** (written by Guido van Rossum and Jesse Jarnagan) — directly relevant to your crawler, and explains the design rationale.
- **Brett Cannon — "How the heck does async/await work in Python 3.5?"** — best single article on the Python internals layer.
- **PEP 342** (Coroutines via Enhanced Generators) and **PEP 3156** (the asyncio spec) — read for design intent, not implementation.

**For the OS layer:**
- **"The Linux Programming Interface"** (Kerrisk) — chapters on file descriptors, `select`/`poll`/`epoll`. Dense but authoritative.
- Alternatively, Julia Evans's zines on Linux systems concepts are much faster to get intuition from.

**For reference:**
- CPython's actual `asyncio` source — specifically `base_events.py`, `futures.py`, `tasks.py`. After you build your version, reading these will feel like reading your own code but more complete.

---

## What This Project Will Actually Teach You

After this, you'll have firsthand understanding of:

- Why asyncio can't do CPU-bound work (the event loop is single-threaded — blocking the loop means nothing else runs)
- Why `await` is not magic — it's just yielding a Future up to the loop
- Why you can't call a regular blocking function inside async code (it blocks the entire loop, not just the coroutine)
- What `uvloop` does differently (replaces the Python event loop with a C one built on `libuv`)
- The real meaning of "non-blocking I/O"

The crawler was an excellent first project. This one will close the loop on *why* the crawler works the way it does.