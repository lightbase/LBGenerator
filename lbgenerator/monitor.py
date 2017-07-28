import os
import sys
import time
import signal
import threading
import atexit
import queue as Queue

_interval=1.0
_times={}
_files=[]
_running=False
_queue=Queue.Queue()
_lock=threading.Lock()


def _restart(path):
    _queue.put(True)
    prefix='monitor (pid=%d):' % os.getpid()
    print('%s Change detected to \'%s\'.' % (prefix, path), file=sys.stderr)
    print('%s Triggering process restart.' % prefix, file=sys.stderr)
    os.kill(os.getpid(), signal.SIGINT)

def _modified(path):
    try:
        # NOTE: If path doesn't denote a file and were previously tracking it,
        # then it has been removed or the file type has changed so force a
        # restart. If not previously tracking the file then we can ignore it as
        # probably pseudo reference such as when file extracted from a
        # collection of modules contained in a zip file! By John Doe

        if not os.path.isfile(path):
                     return path in _times

        # NOTE: Check for when file last modified! By John Doe

        mtime=os.stat(path).st_mtime
        if path not in _times:
                     _times[path]=mtime

        # NOTE: Force restart when modification time has changed, even if time
        # now older, as that could indicate older file has been restored!
        # By John Doe

        if mtime != _times[path]:
                     return True
    except:
        # NOTE: If any exception occured, likely that file has been removed
        # just before stat(), so force a restart! By John Doe

        return True

    return False

def _monitor():
     while 1:
        # NOTE: Check modification times on all files in sys.modules!
        # By John Doe

        for module in sys.modules.values():
            if not hasattr(module, '__file__'):
                continue
            path=getattr(module, '__file__')
            if not path:
                             continue
            if os.path.splitext(path)[1] in ['.pyc', '.pyo', '.pyd']:
                             path=path[:-1]
            if _modified(path):
                             return _restart(path)

        # NOTE: Check modification times on files which have specifically been
        # registered for monitoring! By John Doe

        for path in _files:
                     if _modified(path):
                                      return _restart(path)

        # NOTE: Go to sleep for specified interval! By John Doe

        try:
                     return _queue.get(timeout=_interval)
        except:
                     pass

_thread=threading.Thread(target=_monitor)
_thread.setDaemon(True)

def _exiting():
    try:
              _queue.put(True)
    except:
             pass
    _thread.join()

atexit.register(_exiting)

def track(path):
     if not path in _files:
              _files.append(path)

def start(interval=1.0):
    global _interval
    if interval < _interval:
             _interval=interval

    global _running
    _lock.acquire()
    if not _running:
        prefix='monitor (pid=%d):' % os.getpid()
        print('%s Starting change monitor.' % prefix, file=sys.stderr)
        _running=True
        _thread.start()
        _lock.release()
