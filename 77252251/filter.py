#!/usr/bin/python3 -OO
'''
test multiple server queries for single client query

try using replay: flow.is_replay can be None, "request", or "response"; it
cannot be "both".

try using urllib.request.urlopen: it returns an http.client.HTTPResponse
object which can then be .read().
'''
import time, logging  # pylint: disable=multiple-imports
from http import HTTPStatus
from urllib.request import urlopen
try:
    from mitmproxy import http, ctx
#   from mitmproxy.script import concurrent
except (ImportError, ModuleNotFoundError):  # for doctests
    logging.warning('simulating mitmproxy for doctests')
    # pylint: disable=invalid-name
    http = type('', (), {'HTTPFlow': None})
    ctx = type('', (), {})
    def concurrent(function):  # pylint: disable=unused-argument
        'simulated decorator'
        return None

STRATEGIES = ['request', 'redirect', 'copyflow']
INDEX = 0

# pylint: disable=consider-using-f-string
def request(flow: http.HTTPFlow):
    '''
    filter requests
    '''
    logging.warning('request for path: %s, replay: %s, strategy: %s',
                  flow.request.path, flow.is_replay, STRATEGIES[INDEX])
    logging.warning('flow: %s', oneline(flow))

#@concurrent  # needed only for copyflow, but hopefully won't break others
def response(flow: http.HTTPFlow):
    '''
    filter responses
    '''
    logging.warning('response for path: %s, replay: %s, strategy: %s',
                  flow.request.path, flow.is_replay, STRATEGIES[INDEX])
    logging.warning('flow: %s', oneline(flow))
    strategy = STRATEGIES[INDEX]
    if len(flow.response.content.rstrip()) > 1:
        logging.warning('returning response %s to client', oneline(flow))
        # remove timestamp
        flow.request.path = timestamp(flow.request.path, remove=True)
        next_strategy()
        return
    match strategy:
        case 'redirect':
            redirect = timestamp(flow.request.path)
            flow.response = http.Response.make(
                HTTPStatus.FOUND,
                '<a href="%s">%s</a>' % (redirect, redirect),
                {'content-type': 'text/html', 'location': redirect}
            )
        case 'request':
            # use Python standard library urllib.request.urlopen
            answer = flow.response.content
            while len(answer.rstrip()) < 2:
                flow.request.path = timestamp(flow.request.path)
                with urlopen(flow.request.url) as instream:
                    answer = instream.read()
            flow.response.content = answer
            next_strategy()
        case 'copyflow':
            copy = flow.copy()
            copy.response = None
            if 'view' in ctx.master.addons:
                logging.warning('duplicating flow in view')
                ctx.master.commands.call('views.flows.duplicate', [copy])
            copy.request.path = timestamp(copy.request.path)
            ctx.master.commands.call('replay.client', [copy])
            # killing flow at this point will cause client to shut down.
            # we could instead try `.intercept()`
            flow.intercept()
    return

def timestamp(path, remove=False):
    '''
    append (or discard) timestamp to path for helping to troubleshoot
    '''
    path = path.split('?')[0]
    if not remove:
        path += '?timestamp=%.3f' % time.time()
    return path

def oneline(something):
    '''
    return potentially-multiline string as a single line
    '''
    string = str(something)
    return string.replace('\n', '').replace('\r', '')

def next_strategy():
    '''
    try another strategy to see if it works
    '''
    global INDEX  # pylint: disable=global-statement
    INDEX = (INDEX + 1) % len(STRATEGIES)
