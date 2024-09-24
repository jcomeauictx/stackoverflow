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
from mitmproxy import http

# NOTE: using anything lower than WARNING level in logging will not work
# with mitmproxy, unless further configuration is done
COMMAND = os.path.splitext(os.path.basename(sys.argv[0]))[0]
logging.warning('COMMAND: %s', COMMAND)
STRATEGIES = ['request', 'redirect']
INDEX = 0

# pylint: disable=consider-using-f-string
def request(flow: http.HTTPFlow):
    '''
    filter requests
    '''
    strategy = STRATEGIES[INDEX]
    logging.warning('request for path: %s, replay: %s, strategy: %s',
                  flow.request.path, flow.is_replay, strategy)
    logging.warning('flow: %s', oneline(flow))

def response(flow: http.HTTPFlow):
    '''
    filter responses
    '''
    strategy = STRATEGIES[INDEX]
    logging.warning('response for path: %s, replay: %s, strategy: %s',
                  flow.request.path, flow.is_replay, strategy)
    logging.warning('flow: %s', oneline(flow))
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
