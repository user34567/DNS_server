from server import server
import socket
from const import DATA_PACKAGE_SIZE, SERVER_PORT
from dns_package import DNSPack
from const import TYPES
from binary_functiones import get_bits_from_10, get_bytes_from_10, get_byte_from_bits


class QueryHandler:

    def handle_query(self, pack):
        if pack.is_query:
            if pack.is_all_information_in_pack:  # вся информация в пакете
                if pack.get_opcode() == 0:  # стандартный запрос
                    if pack.get_count_query_sectiones() == 0:  # случай ошибки, запрос отстутствует
                        server.rcode(pack, 1)
                    elif pack.get_count_query_sectiones() == 1:  # 1 секция запросов
                        section = pack.get_query_sectiones()[0]
                        if section['class'] == 1:  # клас IN
                            if section['type'] == 1:  # тип А
                                if server.domain_in_blacklist(section['domain']):  # случай когда домен в blacklist
                                    self.__send_default_answer(pack)
                                else:  # случай когда домен не в blacklist
                                    self.__redirect_to_upstreamserver(pack)
                            else:  # остальные типы
                                server.rcode(pack, 4)
                        else:  # клас не IN
                            server.rcode(pack, 4)
                    else:  # несколько секций запросов
                        sections = pack.get_query_sectiones()
                        class_set = set()
                        type_set = set()
                        for section in sections:
                            class_set.add(section['class'])
                            type_set.add(section['type'])
                        if len(class_set) == 1 and len(type_set) == 1:  # во всех один тип и один класс
                            if class_set.pop() == 1:
                                if type_set.pop() in TYPES:
                                    domains_in_black_list_sectiones_arr = []
                                    domains_not_in_black_list_sectiones_arr = []
                                    for section in sections:
                                        if server.domain_in_blacklist(section['domain']):
                                            domains_in_black_list_sectiones_arr.append(section)
                                        else:
                                            domains_not_in_black_list_sectiones_arr.append(section)
                                    if len(domains_in_black_list_sectiones_arr) == 0:  # нет доменов в blacklist
                                        self.__redirect_to_upstreamserver(pack)
                                    elif len(domains_not_in_black_list_sectiones_arr) == 0:  # все домены в blacklist
                                        self.__send_default_answer(pack)
                                    else:  # домены частично в blacklist
                                        self.__send_comb_answer(pack, domains_in_black_list_sectiones_arr, domains_not_in_black_list_sectiones_arr)
                                else:  # тип не А
                                    server.rcode(pack, 4)
                            else:  # класс не IN
                                server.rcode(pack, 4)
                        else:  # несколько класов или типов
                            server.rcode(pack, 4)

                elif pack.get_opcode() == 1:  # инверсный запрос
                    server.rcode(pack, 4)
                elif pack.get_opcode() == 2:  # запрос статуса сервера
                    pass
                else:  # случай ошибки неизвесный opcode
                    server.rcode(pack, 1)
            else:  # вся информаци не пометилась в 512 біт
                server.rcode(pack, 5)
                return
        else:
            server.rcode(pack, 1)
            return

    def __get_pack_answer_thet_not_in_blacklist(self, pack, sections):
        new_data = pack.data[:4] + get_bytes_from_10(len(sections), 2) + pack.data[6:12]
        for section in sections:
            new_data = new_data + section['bytes']
        new_data = new_data + pack.data[pack.get_ptr_on_first_answer_section():]
        if pack.udp:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        else:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.sendto(new_data, (server.get_upstreamserver_ip(), SERVER_PORT))
        return DNSPack(sock.recv(DATA_PACKAGE_SIZE), None, pack.udp)

    def __send_comb_answer(self, pack, sectiones_in_blacklist, sectiones_not_in_blacklist):
        upstreamserwer_pack = self.__get_pack_answer_thet_not_in_blacklist(pack, sectiones_not_in_blacklist)
        data_not_resolved_queries_sections = bytearray()
        for section in sectiones_in_blacklist:
            data_not_resolved_queris_sectiones = data_not_resolved_queries_sections + section['bytes']
        count_answers_upstreamserver = upstreamserwer_pack.data[6] * 256 + upstreamserwer_pack.data[7]
        count_queries_in2_bytes = get_bytes_from_10(len(sectiones_in_blacklist)+len(sectiones_not_in_blacklist), 2)
        count_answers_in2_bytes = get_bytes_from_10(count_answers_upstreamserver+len(sectiones_in_blacklist), 2)
        new_data_header = upstreamserwer_pack.data[0:4] + count_queries_in2_bytes + count_answers_in2_bytes + upstreamserwer_pack.data[8:12]
        upstreamserwer_pack.get_query_sectiones()
        ptr = upstreamserwer_pack.get_ptr_on_first_answer_section()
        ptr_copy = ptr
        new_data_questions = data_not_resolved_queris_sectiones + upstreamserwer_pack.data[12:ptr]
        len_add_bytes_to_querys = len(data_not_resolved_queris_sectiones)
        other = pack.data[pack.get_ptr_on_first_answer_section():]
        i = 0
        standart_label = True
        while i != count_answers_upstreamserver:
            if upstreamserwer_pack.data[ptr] == 0:
                i = i + 1
                if standart_label:
                    ptr = ptr + 1  # c нуля на тип
                type_answer = upstreamserwer_pack.data[ptr] * 256 + upstreamserwer_pack.data[ptr+1]
                ptr = ptr + 2  # с типа на клас
                ptr = ptr + 2  # c класа на ттл
                ptr = ptr + 4  # на RDLENGTH
                len_rdata = upstreamserwer_pack.data[ptr] * 256 + upstreamserwer_pack.data[ptr+1]
                ptr = ptr + 2  # на секции RDATA
                if type_answer in {1}:
                    ptr = ptr + len_rdata # на сладующей секции или указывает на 1 больше длинны отвтов
                else:
                    j = 0
                    while j != len_rdata:
                        label = get_bits_from_10(upstreamserwer_pack.data[ptr+j], 8)
                        if label[0] == '0' and label[1] == '0':
                            j = j + get_byte_from_bits(label[2:]) + 1
                        elif label[0] == '1' and label[1] == '1':
                            new_label = get_bytes_from_10( upstreamserwer_pack.data[ptr+j]*256+ upstreamserwer_pack.data[ptr+j+1]+len_add_bytes_to_querys,2)
                            upstreamserwer_pack.data = upstreamserwer_pack.data[:ptr+j] + new_label + upstreamserwer_pack.data[ptr+j+2:]
                            j = j + 2
                        else:
                            server.rcode(pack, 1)
                            return
                #ptr = ptr + len_rdata  # на сладующей секции или указывает на 1 больше длинны отвeтов
            else:
                label = get_bits_from_10(upstreamserwer_pack.data[ptr], 8)
                if label[0] == '0' and label[1] == '0':
                    standart_label = True
                    ptr = ptr + get_byte_from_bits(label[2:]) + 1
                elif label[0] == '1' and label[1] == '1':
                    standart_label = False
                    new_label = get_bytes_from_10(upstreamserwer_pack.data[ptr] * 256 + upstreamserwer_pack.data[ ptr + 1] + len_add_bytes_to_querys, 2)
                    upstreamserwer_pack.data = upstreamserwer_pack.data[:ptr] + new_label + upstreamserwer_pack.data[ptr + 2:]
                    ptr = ptr + 2
                else:
                    server.rcode(pack, 1)
                    return
        upstreamserwer_answers = upstreamserwer_pack.data[ptr_copy:ptr]
        i = 0
        blacklist_answers = bytearray()
        ptr_for_sections_query = 12
        for section in sectiones_in_blacklist:
            bits = ('11' + get_bits_from_10(ptr_for_sections_query, 14))
            blacklist_answers = blacklist_answers + bytearray([get_byte_from_bits(bits[:8]), get_byte_from_bits(bits[8:])]) + server.end_answer_section
            ptr_for_sections_query = ptr_for_sections_query + len(section['bytes'])
        new_answers = blacklist_answers + upstreamserwer_answers
        new_data = new_data_header + new_data_questions + new_answers + other
        if pack.udp:
            server.send_udp_pack(new_data, pack.addr)
        else:
            server.send_tcp_pack(new_data, pack.addr)

    def __send_default_answer(self, pack):
        if pack.udp:
            server.send_udp_pack(pack.create_default_pack(), pack.addr)
        else:
            server.send_tcp_pack(pack.create_default_pack(), pack.addr)

    def __redirect_to_upstreamserver(self, pack):
        if pack.udp:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        else:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(pack.data, (server.get_upstreamserver_ip(), SERVER_PORT))
        if pack.udp:
            server.send_udp_pack(sock.recv(DATA_PACKAGE_SIZE), pack.addr)
        else:
            server.send_tcp_pack(sock.recv(DATA_PACKAGE_SIZE), pack.addr)


query_handler = QueryHandler()