#!/usr/bin/python3 -OO
'''
test multiple server queries for single client query
'''
import logging
try:
    from mitmproxy import http, ctx
except (ImportError, ModuleNotFoundError):  # for doctests
    http = type('', (), {'HTTPFlow': None})  # pylint: disable=invalid-name
SAVED = {
    'request': None,
    'response': None,
    'count': 0
}
COPIES = 5

# pylint: disable=consider-using-f-string
def request(flow: http.HTTPFlow):
    '''
    filter requests; send COPIES more upstream for every one received
    '''
    logging.debug('request for path: %s, replay: %s',
                  flow.request.path, flow.is_replay)
    if SAVED['request'] is None:
        SAVED['request'] = flow.copy()
        for index in range(COPIES):
            copy = SAVED['request'].copy()
            if 'view' in ctx.master.addons:
                ctx.master.commands.call('views.flows.duplicate', [copy])
            copy.request.path += ('?copy=%d' % (index + 1))
            ctx.master.commands.call('replay.client', [copy])

def response(flow: http.HTTPFlow):
    '''
    filter responses
    '''
    logging.debug('response for path: %s, replay: %s',
                  flow.request.path, flow.is_replay)
    if SAVED['response'] is None:
        SAVED['response'] = flow
    else:
        SAVED['response'].response.content += flow.response.content
        SAVED['count'] += 1
    if SAVED['count'] == COPIES:
        flow.response = SAVED['response']
        logging.debug('returning response to client')
    else:
        logging.debug('killing flow at count %d', SAVED['count'])
        flow.kill()
