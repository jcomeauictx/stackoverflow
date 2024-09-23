#!/usr/bin/python3 -OO
'''
test multiple server queries for single client query
'''
import logging
try:
    from mitmproxy import http, ctx
    from mitmproxy.script import concurrent
except (ImportError, ModuleNotFoundError):  # for doctests
    logging.warning('simulating mitmproxy for doctests')
    # pylint: disable=invalid-name
    http = type('', (), {'HTTPFlow': None})
    ctx = type('', (), {})
    def concurrent(function):  # pylint: disable=unused-argument
        'simulated decorator'
        return None
SAVED = {
    'request': None,
    'response': None,
    'count': 0
}
COPIES = 5

# pylint: disable=consider-using-f-string
@concurrent
def request(flow: http.HTTPFlow):
    '''
    filter requests; send COPIES more upstream for every one received
    '''
    logging.warning('request for path: %s, replay: %s',
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
    logging.warning('response for path: %s, replay: %s',
                  flow.request.path, flow.is_replay)
    if SAVED['response'] is None:
        SAVED['response'] = flow
    else:
        SAVED['response'].response.content += flow.response.content
        SAVED['count'] += 1
    if SAVED['count'] == COPIES:
        flow = SAVED['response']
        logging.warning('returning response %s to client', flow)
    else:
        logging.warning('killing flow at count %d', SAVED['count'])
        flow.kill()
