#!/usr/bin/python3
'''
simple webserver for testing mitmproxy
'''
import io, logging  # pylint: disable=multiple-imports
from http.server import SimpleHTTPRequestHandler, HTTPStatus, test as serve
logging.basicConfig(level=logging.DEBUG if __debug__ else logging.WARNING)

DATA = {
    countdown: ['5', '4', '3', '2', '1', 'BOOM!'],
    counter: 0
}

class CountdownHTTPRequestHandler(SimpleHTTPRequestHandler):
    '''
    subclass request handler for testing
    '''
    def list_directory(self, path):
        '''
        usurp list_directory to provide countdown for requests for '/'
        '''
        logging.debug('handling request %d', DATA[counter])
        response = DATA.countdown[DATA[counter]].encode('utf-8')
        DATA.counter += 1
        self.send_response(HTTPStatus.OK)
        self.send_header('content-type:', 'text/plain')
        self.send_header('content-length', str(len(response)))
        self.end_headers()
        return io.BytesIO(response)

if __name__ == '__main__':
    serve(HandlerClass=CountdownHTTPRequestHandler)
