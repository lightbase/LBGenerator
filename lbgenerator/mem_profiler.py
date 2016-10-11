"""
This module defines the MemProfiler class and the WSGI 
Middleware (ProfilerMiddleware).
"""

import logging

from pyramid.events import subscriber
from pyramid.events import NewRequest, NewResponse

from pympler import muppy
from pympler import summary
from pympler import tracker
from pympler import refbrowser
from pympler import web

class MemProfiler:
    """ A singleton class that records and logs memory usage using the Pympler library """
    class __MemProfiler:
        """ Inner class used for the singleton pattern """
        def __init__(self):
            self.on = False
            self.logger = logging.getLogger("memprofiler")
            self.tracker = tracker.SummaryTracker()


        def _format_diff(self, diff, limit=15, sort='size', order='descending'):
            return "\n" + "\n".join(summary.format_(diff, limit=limit, sort=sort, order=order))

        def log_diff(self, msg=None):
            """ 
            Calculates memory usage diff between now and the last time this
            function was called. It logs the result to a file and returns it as 
            a string. The string in the 'msg' parameter is included at the top of
            the results.
            """
            if self.on:
                diff = self.tracker.diff()
                formatted_diff = self._format_diff(diff)
                if msg is not None:
                    self.logger.debug(msg + '\n' + formatted_diff)
                else:
                    self.logger.debug(formatted_diff)
                return diff
        
        def log_diff_req(self, req):
            """
            Same as log_diff, but receives a pyramid request 'req' and prints
            it along with the results to identify which request was called.
            """
            if self.on:
                msg = 'Request: %s %s\nBody: %s' % \
                    (req.method, req.path_qs, req.body if req.body else '(EMPTY)')
                self.log_diff(msg)

        def log_diff_res(self, req, res):
            """
            Same as log_diff, but receives a pyramid request 'req' and a 
            pyramid response 'res' and prints them along with the results
            to identify which request was called.
            """
            msg = 'Request: %s %s\nBody: %s\nResponse: %s - %s' % \
                (req.method, req.path_qs, req.body, res.status, res.body)
            self.log_diff(msg)

        def log_summary(self, msg=None):
            """
            Generates a summary of all memory used. The summary is returned as
            a string and logged to a file
            """
            if self.on:
                all_objs = muppy.get_objects()
                all_summ = summary.summarize(all_objs)
                formatted_summ = "\n".join(summary.format_(all_summ, limit=15, sort='size', order='descending'))
                if msg is not None:
                    self.logger.debug('Full Summary:\n' + msg + '\n' + formatted_summ)
                else:
                    self.logger.debug('Full Summary:\n' + formatted_summ)
                return formatted_summ

        def print_diff(self):
            """ Same as log_diff, but prints to console instead of a log file """
            if self.on:
                self.tracker.print_diff()

        def start_web_interface(self):
            """ Starts the web interface thread. It listens at port 8080 """
            if not self.on:
                self.on = True
            self.web_thread = web.start_in_background(host='0.0.0.0', port=8080)


    instance = None

    def __init__(self):
        """
        Returns the singleton instance of the MemProfiler class. It creates
        the object only on the first time it's called.
        """
        if not MemProfiler.instance:
            MemProfiler.instance = MemProfiler.__MemProfiler()

    def __getattr__(self, attr):
        """ Overridden to access inner class's attributes instead """
        return getattr(self.instance, attr)

    def __setattr__(self, attr, value):
        """ Overridden to access inner class's attributes instead """
        return setattr(self.instance, attr, value)

class ProfilerMiddleware:
    """ WSGI Middleware that exposes MemProfiler Commands """
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        if environ.get("PATH_INFO") == "/__memprofiler_dump":
            mem_profiler = MemProfiler()
            if mem_profiler.on:
                diff = mem_profiler.log_diff()
                content = str(diff)
            else:
                content = "Memory Profiler P is OFF.\n\nTo turn it on: GET /__memprofiler_on\nTo turn it off: GET /__memprofiler_off"
            start_response("200 OK", [('Content-Type', 'text/plain')])
            return [ content.encode('utf-8') ]

        if environ.get("PATH_INFO") == "/__objref":
            mem_profiler = MemProfiler()
            if mem_profiler.on:
                from .model import BASES
                cb = refbrowser.ConsoleBrowser(BASES, maxdepth=2, 
                    str_func=lambda o: str(type(o)))
                tree = cb.get_tree()
                content = str(tree)
            else:
                content = "Memory Profiler P is OFF.\n\nTo turn it on: GET /__memprofiler_on\nTo turn it off: GET /__memprofiler_off"
            start_response("200 OK", [('Content-Type', 'text/plain')])
            return [ content.encode('utf-8') ]


        if environ.get("PATH_INFO") == "/__memprofiler_on":
            MemProfiler().on = True
            # TODO: log 
            start_response("200 OK",[('Content-type' , 'text/html')])
            return [ b"Memory Profiler P is ON.\n\nTo turn it off: GET /__memprofiler_off" ]
            
        if environ.get("PATH_INFO") == "/__memprofiler_off":
            MemProfiler().on = False
            # TODO: log 
            start_response("200 OK",[('Content-type' , 'text/html')])
            return [ b"Memory Profiler P is OFF.\n\nTo turn it off: GET /__memprofiler_on" ]

        if environ.get("PATH_INFO") == "/__memprofiler_web":
            MemProfiler().start_web_interface()
            start_response("200 OK",[('Content-type' , 'text/html')])
            return [ b"Memory Profiler's Web Interface is now running on port: 8080" ]

        return self.app(environ, start_response)

# This function is called by Pyramid before and after every request
@subscriber(NewRequest, NewResponse)
def ProfilerEventListener(event):
    mem_profiler = MemProfiler()
    if mem_profiler.on:
        if isinstance(event, NewRequest):
            req = event.request
            msg = 'Request: %s %s\nBody: %s' % \
                (req.method, req.path_qs, req.body if req.body else '(EMPTY)')
            mem_profiler.log_diff(msg)
        elif isinstance(event, NewResponse):
            req = event.request
            res = event.response
            msg = 'Request: %s %s\nBody: %s\nResponse: %s - %s' % \
                (req.method, req.path_qs, req.body, res.status, res.body)
            mem_profiler.log_diff(msg)
            mem_profiler.log_summary(msg)
