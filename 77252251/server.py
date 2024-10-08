#!/usr/bin/python3
'''
simple webserver for testing mitmproxy
'''
import os, io, logging  # pylint: disable=multiple-imports
from http.server import SimpleHTTPRequestHandler, HTTPStatus, test as serve
logging.basicConfig(level=logging.DEBUG if __debug__ else logging.WARNING)

DATA = {
    'countdown': ['5', '4', '3', '2', '1', 'BOOM!'],
    'count': 0
}

class CountdownHTTPRequestHandler(SimpleHTTPRequestHandler):
    '''
    subclass request handler for testing
    '''
    def list_directory(self, path):
        '''
        usurp list_directory to provide countdown for requests for '/'
        '''
        logging.debug('handling request %d', DATA['count'])
        response = (DATA['countdown'][DATA['count']] + os.linesep).encode()
        DATA['count'] = (DATA['count'] + 1) % len(DATA['countdown'])
        self.send_response(HTTPStatus.OK, 'counting down')
        self.send_header('content-type', 'text/plain')
        self.send_header('content-length', str(len(response)))
        self.end_headers()
        return io.BytesIO(response)

if __name__ == '__main__':
    serve(HandlerClass=CountdownHTTPRequestHandler)
