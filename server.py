import socket
from const import *
import configparser
from concurrent.futures import ProcessPoolExecutor
from binary_functiones import get_bytes_from_10


class Server:
    def __init__(self):
        self.__init_sockets()
        self.__pool = ProcessPoolExecutor(THREADS_COUNT)
        self.__get_data_from_config()

    def __init_sockets(self):
        sock_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock_udp.bind((SERVER_IP, SERVER_PORT))
        sock_tcp.bind((SERVER_IP, SERVER_PORT))
        self.__socket_tcp = sock_tcp
        self.__socket_udp = sock_udp

    def __get_data_from_config(self):
        config = configparser.ConfigParser()
        config.read(CONFIG_FILE_NAME)
        self.__blacklist_set = set((config["blacklist"]['list']).split("\n"))
        self.__upstreamserver_ip_str = config["upstreamserver"]["ip"]
        self.__cretate_end_answer_section(bytes(config["answer"]['text'], 'utf-8'))


    def get_upstreamserver_ip(self):
        return self.__upstreamserver_ip_str

    def __cretate_end_answer_section(self,answer_bytes):
        self.end_answer_section =  bytearray([0, 16, 0, 1]) + get_bytes_from_10(TTL,4) + get_bytes_from_10(len(answer_bytes) + 1,2) +\
               bytearray([len(answer_bytes)]) + answer_bytes

    def send_udp_pack(self,data,addr):
        print(data)
        print(addr)
        print('----')
        for i in data:
            print(i)
        print('----')
        self.__socket_udp.sendto(data, addr)

    def domain_in_blacklist(self, domen):
        return domen in self.__blacklist_set

    def get_upt_socket(self):
        return self.__socket_udp

    def get_tcp_socket(self):
        return self.__socket_tcp





server = Server()