from bitstring import BitArray


def get_byte_from_bits(bits):
    return BitArray(bin=bits).uint


def get_bits_from_10(number, count_bits):
    return bin(number)[2:].zfill(count_bits)


def get_bytes_from_10(number, count_bytes):
    bytes_arr = bytearray([])
    bits = get_bits_from_10(number, count_bytes * 8)
    i = 0
    while i != count_bytes:
        bytes_arr = bytes_arr + bytearray([get_byte_from_bits(bits[i * 8:i * 8 + 8])])
        i = i + 1
    return bytes_arr




