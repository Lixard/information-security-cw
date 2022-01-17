from math import sin, floor
from enum import Enum
import struct
from typing import Union, Tuple
from bitarray import bitarray

from logger import Logger


class MD5Buffer(Enum):
    A = 0x67452301
    B = 0xEFCDAB89
    C = 0x98BADCFE
    D = 0x10325476


_logger = Logger()


class MD5:
    @classmethod
    def from_str(cls, input: str) -> Tuple[str, str]:
        return (cls._hash(input), _logger.get_and_clear())

    @classmethod
    def from_path(cls, filepath: str) -> Tuple[str, str]:
        with open(filepath, "rb") as f:
            _logger.log(f"Открывается файл {filepath}")
            bytes = f.read()
        return (cls._hash(bytes), _logger.get_and_clear())

    @classmethod
    def _hash(cls, input: str):
        bit_array = cls._to_bit_array(input)
        aligned_array = cls._align(bit_array)  # step 1
        extended_array = cls._extend(input, aligned_array)  # step 2
        buffers = cls._init_buffers()  # step 3
        cls._loop_calcs(extended_array, buffers)  # step 4 (main calculations)
        return cls._finalize(buffers)

    @classmethod
    def _to_bit_array(cls, input: Union[str, bytes]) -> bitarray:
        """
        Converts input string to bit array.

        Args:
            input (str): input string

        Returns:
            bitarray: bit array
        """
        bit_array = bitarray(endian="big")
        if isinstance(input, str):
            bit_array.frombytes(input.encode("utf-8"))
        elif isinstance(input, bytes):
            bit_array.frombytes(input)
        _logger.log("Входные данные преобразуются в битовый массив")
        return bit_array

    @classmethod
    def _align(cls, bit_array: bitarray) -> bitarray:
        """
        Step 1.
        Aligns the stream. To the end of stream appends a single bit.
        Then appends zeros bits as much as the new stream length makes equal with 446 modulo 512.

        Alignment occurs in any case, even if the length of the original stream is already equals with 448.

        Args:
            bit_array (bitarray): bit array

        Returns:
            bitarray: aligned bit array
        """
        _logger.log("К битовому массиву добавляем битовую 1")
        bit_array.append(1)

        _logger.log(
            "Добавляем битовые нули пока длина битового массива не будет при делении на 512 в остатке давать 448"
        )
        counter = 0
        while len(bit_array) % 512 != 448:
            bit_array.append(0)
            counter += 1
        _logger.log(f"Было добавлено {counter} нулей")

        return bitarray(bit_array, endian="little")

    @classmethod
    def _extend(cls, input: str, aligned_array: bitarray) -> bitarray:
        """
        Step 2.
        At the end of stream appends input length in bit representation in little-endian format with length of 64 bits.
        If the length more than 2^64 - 1, then appends only low-order bits.
        After that, the stream length will be multiple of 512.

        Args:
            input (str): input string
            aligned_array (bitarray): aligned array

        Returns:
            bitarray: extended array
        """
        len_in_bits = len(input) * 8
        length = len_in_bits % pow(2, 64)

        length_bit_array = bitarray(endian="little")
        length_bit_array.frombytes(struct.pack("<Q", length))

        _logger.log(
            f"В конец сообщения дописываем 64 битное представление длины данных. Битовая длина сообщения равняется - {len_in_bits}"
        )
        extended_array = aligned_array.copy()
        extended_array.extend(length_bit_array)
        return extended_array

    @classmethod
    def _init_buffers(cls) -> dict:
        """
        Step 3.
        For the following calculations, four 32-bit buffers are initialized.
        Initial values of which are given in hexadecimal numbers.

        Returns:
            dict: dictionary where key is buffer and value is initial hexadecimal number
        """
        _logger.log("Инициализируем буфферы значениями по умолчанию")
        return {i: i.value for i in MD5Buffer}

    @classmethod
    def _loop_calcs(cls, extended_array: bitarray, buffers: dict) -> None:
        # Define functions for rounds
        F = lambda x, y, z: (x & y) | (~x & z)
        G = lambda x, y, z: (x & z) | (y & ~z)
        H = lambda x, y, z: x ^ y ^ z
        I = lambda x, y, z: y ^ (x | ~z)

        # Define the left rotation function, which rotates `x` left `n` bits.
        rotate_left = lambda x, n: (x << n) | (x >> (32 - n))

        # Define a function for modular addition.
        modular_add = lambda a, b: (a + b) % pow(2, 32)

        # Compute the T table from the sine function. Note that the
        # RFC starts at index 1, but we start at index 0.
        T = [floor(pow(2, 32) * abs(sin(i + 1))) for i in range(64)]
        _logger.log(f"Определяем таблицу констант T: {T}")

        N = len(extended_array) // 32

        # Process chunks of 512 bits.
        _logger.log("Начинаем вычисления для 512-битных блоков")
        for chunk_index in range(N // 16):

            # Break the chunk into 16 words of 32 bits in list X.
            start = chunk_index * 512
            X = [
                extended_array[start + (x * 32) : start + (x * 32) + 32]
                for x in range(16)
            ]

            X = [int.from_bytes(word.tobytes(), byteorder="little") for word in X]

            # Make shorthands for the buffers A, B, C, D.
            A = buffers[MD5Buffer.A]
            B = buffers[MD5Buffer.B]
            C = buffers[MD5Buffer.C]
            D = buffers[MD5Buffer.D]

            # Execute the four rounds with 16 operations each.
            for i in range(4 * 16):
                if 0 <= i <= 15:
                    k = i
                    s = [7, 12, 17, 22]
                    temp = F(B, C, D)
                elif 16 <= i <= 31:
                    k = ((5 * i) + 1) % 16
                    s = [5, 9, 14, 20]
                    temp = G(B, C, D)
                elif 32 <= i <= 47:
                    k = ((3 * i) + 5) % 16
                    s = [4, 11, 16, 23]
                    temp = H(B, C, D)
                elif 48 <= i <= 63:
                    k = (7 * i) % 16
                    s = [6, 10, 15, 21]
                    temp = I(B, C, D)

                # The MD5 algorithm uses modular addition. Note that we need a
                # temporary variable here. If we would put the result in `A`, then
                # the expression `A = D` below would overwrite it. We also cannot
                # move `A = D` lower because the original `D` would already have
                # been overwritten by the `D = C` expression.
                temp = modular_add(temp, X[k])
                temp = modular_add(temp, T[i])
                temp = modular_add(temp, A)
                temp = rotate_left(temp, s[i % 4])
                temp = modular_add(temp, B)

                # Swap the registers for the next operation.
                A = D
                D = C
                C = B
                B = temp

            _logger.log(f"{chunk_index + 1} из {N // 16} блоков посчитаны")
            # Update the buffers with the results from this chunk.
            buffers[MD5Buffer.A] = modular_add(buffers[MD5Buffer.A], A)
            buffers[MD5Buffer.B] = modular_add(buffers[MD5Buffer.B], B)
            buffers[MD5Buffer.C] = modular_add(buffers[MD5Buffer.C], C)
            buffers[MD5Buffer.D] = modular_add(buffers[MD5Buffer.D], D)
            _logger.log(
                f"Сохраняем результаты в буфферы: A = {A}, B = {B}, C = {C}, D = {D}"
            )

    @classmethod
    def _finalize(cls, buffers: dict) -> str:
        A = struct.unpack("<I", struct.pack(">I", buffers[MD5Buffer.A]))[0]
        B = struct.unpack("<I", struct.pack(">I", buffers[MD5Buffer.B]))[0]
        C = struct.unpack("<I", struct.pack(">I", buffers[MD5Buffer.C]))[0]
        D = struct.unpack("<I", struct.pack(">I", buffers[MD5Buffer.D]))[0]

        hash = (
            f"{format(A, '08x')}{format(B, '08x')}{format(C, '08x')}{format(D, '08x')}"
        )
        _logger.log(
            f"Формируем вывод. Выводим побайтово из буфферов, начиная с младшего байта первого буфера и заканчивая старшим байтом последнего: {hash}"
        )
        return hash
