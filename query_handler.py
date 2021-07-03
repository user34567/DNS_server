from server import server
import socket
from const import DATA_PACKAGE_SIZE, SERVER_PORT


class QueryHandler:
    def handle_udp_query(self,pack):
        if pack.is_query:
            if pack.is_all_information_in_pack:  # вся информация в пакете
                if pack.get_opcode() == 0:  # стандартный запрос
                    if pack.get_count_query_sectiones() == 0:  # случай ошибки, запрос отстутствует
                        pass
                    elif pack.get_count_query_sectiones() == 1:  # 1 секция запросов
                        section = pack.get_query_sectiones()[0]
                        if section['class'] == 1:  # клас IN
                            if section['type'] == 1:  # тип А
                                if server.domain_in_blacklist(section['domain']):  # случай когда домен в blacklist
                                    self.__send_default_answer(pack)
                                else: # случай когда домен не в blacklist
                                    self.__redirect_to_upstreamserver_udp(pack)
                            else:  # остальные типы
                                pass
                        else:  # клас не IN
                            pass
                    else:  # несколько секций запросов
                        sections = pack.get_query_sectiones()
                        class_set = set()
                        type_set = set()
                        for section in sections:
                            class_set.add(section['class'])
                            type_set.add(section['type'])
                        if len(class_set) == 1 and len(type_set) == 1:  # во всех один тип и один класс
                            if class_set.pop() == 1:
                                if type_set.pop() == 1:
                                    domains_in_black_list_id_arr = []
                                    domains_not_in_black_list_id_arr = []
                                    i = 0
                                    for section in sections:
                                        if server.domain_in_blacklist(section['domain']):
                                            domains_in_black_list_id_arr.append(i)
                                        else:
                                            domains_not_in_black_list_id_arr.append(i)
                                        i = i + 1
                                    if len(domains_in_black_list_id_arr) == 0:  # нет доменов в blacklist
                                        self.__redirect_to_upstreamserver_udp(pack)
                                    elif len(domains_not_in_black_list_id_arr) == 0:  # все домены в blacklist
                                        self.__send_default_answer(pack)
                                    else: # домены частично в blacklist
                                        pass
                                else:  # тип не А
                                    pass
                            else:  # класс не IN
                                pass
                        else:  # несколько класов или типов
                            pass

                elif pack.get_opcode() == 1:  # инверсный запрос
                    pass
                elif pack.get_opcode() == 2:  # запрос статуса сервера
                    pass
                else:  # случай ошибки неизвесный opcode
                    pass
            else: #  вся информаци не пометилась в 512 біт
                pass
        else:
            pass # пришел ответ

    def __send_default_answer(self, pack):
        server.send_udp_pack(pack.create_default_pack(), pack.addr)

    def __redirect_to_upstreamserver_udp(self, pack):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(pack.data, (server.get_upstreamserver_ip(), SERVER_PORT))
        server.send_udp_pack(sock.recv(DATA_PACKAGE_SIZE), pack.addr)

query_handler = QueryHandler()