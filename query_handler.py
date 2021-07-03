from server import server


class QueryHandler:
    def handle_udp_query(self,pack):
        if pack.is_query:
            if pack.is_all_information_in_pack:  # вся информация в пакете
                if pack.get_opcode() == 0:  # стандартный запрос
                    if pack.get_count_query_sectiones() == 0:  # случай ошибки запрос отстутствует
                        pass
                    elif pack.get_count_query_sectiones() == 1:  # 1 секция запросов
                        section = pack.get_query_sectiones()[0]
                        if section['class'] == 1:  # клас IN
                            if section['type'] == 1:  # тип А
                                if server.domain_in_blacklist(section['domain']):
                                    self.__send_default_answer(pack)
                            else:  # остальные типы
                                pass
                        else:  # клас не IN
                            pass
                    else:  # несколько секций запросов
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





query_handler = QueryHandler()