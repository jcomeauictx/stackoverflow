#!/usr/bin/python3 -OO
'''
test multiple server queries for single client query

try using replay: flow.is_replay can be None, "request", or "response"; it
cannot be "both".

try using urllib.request.urlopen: it returns an http.client.HTTPResponse
object which can then be .read().
'''
import time, logging  # pylint: disable=multiple-imports
try:
    from mitmproxy import http, ctx
except (ImportError, ModuleNotFoundError):  # for doctests
    logging.warning('simulating mitmproxy for doctests')
    # pylint: disable=invalid-name
    http = type('', (), {'HTTPFlow': None})
    ctx = type('', (), {})

# pylint: disable=consider-using-f-string
def request(flow: http.HTTPFlow):
    '''
    filter requests
    '''
    logging.warning('request for path: %s, replay: %s',
                  flow.request.path, flow.is_replay)
    logging.warning('flow: %s', oneline(flow))

def response(flow: http.HTTPFlow):
    '''
    filter responses
    '''
    logging.warning('response for path: %s, replay: %s',
                  flow.request.path, flow.is_replay)
    logging.warning('flow: %s', oneline(flow))
    if len(flow.response.content.rstrip()) > 1:
        logging.warning('returning response %s to client', oneline(flow))
        # remove timestamp
        flow.request.path = timestamp(flow.request.path, remove=True)
        # pylint: disable=fixme
        ctx.master.shutdown()  # FIXME: just during testing
    else:
        copy = flow.copy()
        copy.response = None
        if 'view' in ctx.master.addons:
            logging.warning('duplicating flow in view')
            ctx.master.commands.call('views.flows.duplicate', [copy])
        copy.request.path = timestamp(copy.request.path)
        ctx.master.commands.call('replay.client', [copy])
        logging.warning('killing flow for "wrong" answer')
        flow.kill()

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
