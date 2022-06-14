import os
import line_profiler
import functools
import inspect
import linecache
import collections
from flask import current_app
from flask.globals import _request_ctx_stack


functions_to_profile = []


def line_profile(f):
    functions_to_profile.append(f)
    return f


def process_line_stats(line_stats):
    profile_results = []

    if not line_stats:
        return profile_results

    multiplier = line_stats.unit / 1e-3

    for key, timings in sorted(line_stats.timings.items()):
        if not timings:
            continue

        filename, start_lineno, func_name = key

        all_lines = linecache.getlines(filename)
        sublines = inspect.getblock(all_lines[start_lineno-1:])
        end_lineno = start_lineno + len(sublines)

        line_to_timing = collections.defaultdict(lambda: (-1, 0))

        for (lineno, nhits, time) in timings:
            line_to_timing[lineno] = (nhits, time)

        padded_timings = []

        for lineno in range(start_lineno, end_lineno):
            nhits, time = line_to_timing[lineno]
            padded_timings.append( (lineno, nhits, time) )

        profile_results.append({
            'filename': filename,
            'start_lineno': start_lineno,
            'func_name': func_name,
            'timings': [
                (
                    lineno,
                    unicode(all_lines[lineno - 1].decode("utf8")),
                    time * multiplier,
                    nhits,
                ) for (lineno, nhits, time) in padded_timings
            ],
            'total_time': sum([time for _, _, time in timings]) * multiplier
        })

    return profile_results


class DebugTool(object):
    def __init__(self, app=None, cache=None):
        self.app = app
        self.cache = cache
        if app is not None:
            self.init_app(app, cache)

    def init_app(self, app, cache=None):
        if not self.cache and cache:
            self.cache = cache
        if not self.cache:
            raise RuntimeError("The Flask-DebugToolbar requires the cache ext")

        if not app.config['DEBUG_TB_ENABLED']:
            return

        app.before_request(self.process_request)
        app.after_request(self.process_response)
        app.teardown_request(self.teardown_request)
        app.dispatch_request = self.dispatch_request

    def dispatch_request(self):
        req = _request_ctx_stack.top.request
        app = current_app

        if req.routing_exception is not None:
            app.raise_routing_exception(req)

        rule = req.url_rule

        if getattr(rule, 'provide_automatic_options', False) \
           and req.method == 'OPTIONS':
            return app.make_default_options_response()

        view_func = app.view_functions[rule.endpoint]
        view_func = self.process_view(view_func, req.view_args)

        return view_func(**req.view_args)

    def process_request(self):
        self.profiler = line_profiler.LineProfiler()

        for f in functions_to_profile:
            self.profiler.add_function(f)

        self.stats = None

    def process_view(self, view_func, view_kwargs):
        return functools.partial(self.profiler.runcall, view_func)


    def process_response(self, response):
        self.stats = self.profiler.get_stats()
        processed_line_stats = process_line_stats(self.stats)
        if self.cache and processed_line_stats:
            self.cache.set(self.app.config["DEBUG_TOOL_CACHE"], processed_line_stats)
        return response

    def teardown_request(self, exc):
        pass
