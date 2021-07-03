from binary_functiones import get_bits_from_10, get_byte_from_bits, get_bytes_from_10
from server import server

class DNSPack:
    def __init__(self, data, addr):
        self.data = data
        self.addr = addr
        self.ptr_for_sectiones_query = []

    def is_query(self):
        return get_bits_from_10(self.data[2],8)[0] == '0'

    def get_opcode(self):
        return get_byte_from_bits(get_bits_from_10(self.data[2],8)[1:5])

    def is_all_information_in_pack(self):
        return get_bits_from_10(self.data[2],8)[6] == '0'

    def get_count_query_sectiones(self):
        return self.data[4] * 256 + self.data[5]

    def __get_name_in_section(self,ptr):
        self.ptr_for_sectiones_query.append(ptr)
        text_arr = []
        while self.data[ptr] != 0:
            label = get_bits_from_10(self.data[ptr],8)
            if label[0] == '0' and label[1] == '0':
                len = get_byte_from_bits(label[2:])
                ptr = ptr + 1
                text_arr.append(str(self.data[ptr:ptr+len], 'utf-8'))
                ptr = ptr + len
            else:
                ptr = ptr + 1
                ptr_read = get_byte_from_bits(label[2:] + get_bits_from_10(self.data[ptr],8))
                while self.data[ptr_read] != 0:
                    label = get_bits_from_10(self.data[ptr_read], 8)
                    len = get_byte_from_bits(label[2:])
                    ptr_read = ptr_read + 1
                    text_arr.append(str(self.data[ptr_read:ptr_read + len], 'utf-8'))
                    ptr_read = ptr_read + len
                return '.'.join(text_arr), ptr + 1
        return '.'.join(text_arr), ptr + 1

    def __set_count_answers(self, count):
        self.data = self.data[:6] + get_bytes_from_10(count, 2) + self.data[8:]

    def __set_answer_flag(self):
        self.data = self.data[:2] + bytearray([self.data[2] + 128]) + self.data[3:]

    def create_default_pack(self):
        count_answers = self.get_count_query_sectiones()
        self.__set_answer_flag()
        self.__set_count_answers(count_answers)
        i = 0
        answers = bytearray()
        while i != count_answers:
            bits = ('11' + get_bits_from_10(self.ptr_for_sectiones_query[0],14))
            answers = answers + bytearray([get_byte_from_bits(bits[:8]),get_byte_from_bits(bits[8:])]) + server.end_answer_section
            i = i + 1
        self.data = self.data[:self.__ptr_on_first_answer_section] + answers + self.data[self.__ptr_on_first_answer_section:]
        return self.data

    def get_query_sectiones(self):
        ptr = 12
        sectiones = []
        for i in range(self.get_count_query_sectiones()):
            text, ptr = self.__get_name_in_section(ptr)
            sectiones.append({
                'domain':text,
                'type':self.data[ptr] * 256 + self.data[ptr+1],
                'class':self.data[ptr + 2] * 256 + self.data[ptr + 3]
            })
            ptr = ptr + 4
        self.__ptr_on_first_answer_section = ptr
        return sectiones



# data =  b'\x16\x08\x01 \x00\x01\x00\x00\x00\x00\x00\x01\x06google\x03com\x00\x00\x01\x00\x01\x00\x00)\x10\x00\x00\x00\x00\x00\x00\x0c\x00\n\x00\x08\xc4\x9d\x18\xfe\xd8\xdc\x96^'
# d = DNSPack(data,11,True)
# d.get_query_sectiones()
# a = d.create_default_pack()
# print(a)
# print("-------------------")
# for i in a :
#     print(i)
# print("-------------------")

