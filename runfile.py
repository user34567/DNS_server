import socket

from server import server
from query_handler import query_handler
from dns_package import DNSPack
import threading
from const import DATA_PACKAGE_SIZE, QUEUE_SOCKET_SIZE, TCP_PACK_SIZE


def execute_request_udp(data, addr):
    query_handler.handle_query(DNSPack(data, addr, True))


def execute_request_tcp(data, addr, clientsocket):
    query_handler.handle_query(DNSPack(data, addr, False, clientsocket))


def udp_query_listen():
    print("start thread for udp queries")
    sock = server.get_upt_socket()
    while True:
        data, addr = sock.recvfrom(DATA_PACKAGE_SIZE)
        server.get_pool().submit(execute_request_udp, data, addr)


def tcp_query_listen():
    print("start thread for udp queries")
    sock = server.get_tcp_socket()
    sock.listen(QUEUE_SOCKET_SIZE)
    while True:
        clientsocket, address = sock.accept()
        data, addr = clientsocket.recvfrom(TCP_PACK_SIZE)
        server.get_pool().submit(execute_request_tcp, data, addr,clientsocket)

def run():
    print("server run")
    udp_thread = threading.Thread(target=udp_query_listen)
    tcp_thread = threading.Thread(target=tcp_query_listen)
    udp_thread.start()
    tcp_thread.start()

run()


