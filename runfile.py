from server import server
from query_handler import query_handler
from dns_package import DNSPack
import threading
from const import DATA_PACKAGE_SIZE

def execute_request_udp(data,addr):
    query_handler.handle_udp_query(DNSPack(data,addr))
    server.get_upt_socket().close()
    server.get_tcp_socket().close()




def udp_query_listen():
    print("start thread for udp queries")
    sock = server.get_upt_socket()
    while True:
        data, addr = sock.recvfrom(DATA_PACKAGE_SIZE)
        execute_request_udp(data, addr)


def run():
    print("server run")
    udp_thread = threading.Thread(target=udp_query_listen)
    udp_thread.start()
    #tcp_thread = threading.Thread(target=self.__get_tcp_query)

run()

