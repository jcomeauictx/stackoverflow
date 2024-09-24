#!/usr/bin/python3 -OO
'''
test multiple server queries for single client query

try using replay: flow.is_replay can be None, "request", or "response"; it
cannot be "both".

try using urllib.request.urlopen: it returns an http.client.HTTPResponse
object which can then be .read().
'''
import sys, os, time, logging  # pylint: disable=multiple-imports
from http import HTTPStatus
from urllib.request import urlopen
from mitmproxy import http, ctx
from mitmproxy.script import concurrent

# NOTE: using anything lower than WARNING level in logging will not work
# with mitmproxy, unless further configuration is done
COMMAND = os.path.splitext(os.path.basename(sys.argv[0]))[0]
logging.warning('COMMAND: %s', COMMAND)
STRATEGIES = ['request', 'redirect', 'copyflow']
INDEX = 0

# pylint: disable=consider-using-f-string
# concurrent needed only for copyflow, but hopefully won't break others
try:
    @concurrent
    def request(flow: http.HTTPFlow):
        '''
        filter requests
        '''
        logging.warning('request for path: %s, replay: %s, strategy: %s',
                      flow.request.path, flow.is_replay, STRATEGIES[INDEX])
        logging.warning('flow: %s', oneline(flow))
        if STRATEGIES[INDEX] == 'copyflow':
            # queue another request in case this one's response is unsuitable
            copy = flow.copy()
            if 'view' in ctx.master.addons:
                logging.warning('duplicating flow in view')
                ctx.master.commands.call('views.flows.duplicate', [copy])
            copy.request.path = timestamp(copy.request.path)
            ctx.master.commands.call('replay.client', [copy])
except NotImplementedError:
    if COMMAND == 'doctest':
        logging.error('concurrent decorator not supported during doctests')
    else:
        raise

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
                ('<a href="%s">%s</a>' % (redirect, redirect)).encode(),
                {'content-type': 'text/html', 'location': redirect}
            )
        case 'request':
            # use Python standard library urllib.request.urlopen
            answer = flow.response.content
            while len(answer.rstrip()) < 2:
                flow.request.path = timestamp(flow.request.path)
                logging.warning('making followup request to %s',
                                flow.request.path)
                with urlopen(flow.request.url) as instream:
                    answer = instream.read()
            flow.response.content = answer
            next_strategy()
        case 'copyflow':
            logging.warning('ignoring response %r during copyflow strategy',
                            flow.response.content)
            flow.response = http.Response.make(
                HTTPStatus.PARTIAL_CONTENT,
                b'',
                {'content-type': 'text/plain'}
            )
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
