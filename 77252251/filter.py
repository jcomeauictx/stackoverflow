#!/usr/bin/python3 -OO
'''
test multiple server queries for single client query
'''
import logging
try:
    from mitmproxy import http
except (ImportError, ModuleNotFoundError):  # for doctests
    http = type('', (), {'HTTPFlow': None})  # pylint: disable=invalid-name

def request(flow: http.HTTPFlow):
    '''
    filter requests
    '''
    logging.debug('request: %s', flow.request)

def response(flow: http.HTTPFlow):
    '''
    filter responses
    '''
    logging.debug('response: %s', flow.response)
