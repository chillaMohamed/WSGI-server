import socket


def parse_http(http):
    try:
        http = http.decode('utf-8')
    except UnicodeDecodeError:
        raise ValueError("Invalid encoding")

    try:
        http_req, *headers, _, body = http.split('\r\n')
        method, path, protocol = http_req.split()
        headers = dict(
            line.split(': ', maxsplit=1) for line in headers
        )
    except ValueError:
        raise ValueError("Malformed HTTP request")


    return method, path, protocol, headers, body

def process_response(status, response):

    return (
        f'HTTP/1.1 {status}\r\n'.encode()
        +f'Content-Length: {len(response)}\r\n'.encode()
        +b'Content-Type: text/plain\r\n'
        +b'\r\n'
        +response.encode()
        +b'\r\n'
    )

def to_environ(method, path, protocol, headers, body):
    environ['REQUEST_METHOD'] = method
    environ['PATH_INFO'] = path
    environ['SERVER_PROTOCOL'] = protocol
    environ['CONTENT_LENGTH'] = headers.get('Content-Length', '0')
    environ['CONTENT_TYPE'] = headers.get(
        'Content-Type', 'application/octet-stream'
    )
    environ['wsgi.input'] = body
    return environ

def start_response(status, headers):
    conn.sendall(f'HTTP/1.1 {status}\r\n'.encode())
    for header in headers.items():
        conn.sendall(f'{header[0]}: {header[1]}\r\n'.encode())
    conn.sendall(b'\r\n')

def application(environ, start_response):
    response, status_code = view(environ)
    start_response(status_code, environ)
    return response

def view(environ):
    return "Hello World! i am a view ....", "200 OK"

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind(('localhost', 8000))
    s.listen()
    print('Listening on http://localhost:8000')

    while True:
        conn, addr = s.accept()
        with conn:
            http_request = conn.recv(1024)
            try:
                request = parse_http(http_request)  # Parse the request
                environ  = to_environ(*request)
                response_data = application(environ, start_response)
                for data in response_data:
                    conn.sendall(data.encode())
            except Exception as e:
                http_response = process_response("400 Bad Request", str(e))

            print(http_request.decode('utf-8'))
