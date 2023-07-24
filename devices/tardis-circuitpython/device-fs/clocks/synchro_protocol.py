import functools
import json


FNV_32_PRIME: int = 0x01000193
FNV1_32_INIT: int = 0x811c9dc5
FNV_32_SIZE: int = 2 ** 32


def fnv_1a(data: bytes) -> int:
    assert isinstance(data, bytes)
    return functools.reduce(lambda fh, byte: ((fh ^ byte) * FNV_32_PRIME) % FNV_32_SIZE, data, FNV1_32_INIT)


def fnv_1a_on_str(payload) -> int:
    return fnv_1a(payload.encode("ascii"))


MESSAGE_START = '⏳'
CHECKSUM_START = '⏰'
MESSAGE_END = '⌛'


def encode(data) -> str:
    payload = json.dumps(data)
    return f'{MESSAGE_START}{payload}{CHECKSUM_START}{fnv_1a_on_str(payload)}{MESSAGE_END}'


def decode_and_verify(line: str):
    if line.startswith(MESSAGE_START) and CHECKSUM_START in line and line.endswith(MESSAGE_END):
        payload, checksum = line.lstrip(MESSAGE_START).rstrip(MESSAGE_END).split(CHECKSUM_START, 1)
        supplied_checksum = int(checksum)
        actual_checksum_of_payload = fnv_1a_on_str(payload)
        if supplied_checksum == actual_checksum_of_payload:
            return json.loads(payload)
        else:
            print(f'Checksum mismatch: {supplied_checksum} {actual_checksum_of_payload}')
    return None


test_vectors: dict[str, int] = {
    "": 0x811c9dc5,
    "a": 0xe40c292c,
    "b": 0xe70c2de5,
    "c": 0xe60c2c52,
    "d": 0xe10c2473,
    "e": 0xe00c22e0,
    "f": 0xe30c2799,
    "fo": 0x6222e842,
    "foo": 0xa9f37ed7,
    "foob": 0x3f5076ef
}

for text, h in test_vectors.items():
    actual = fnv_1a(text.encode("ascii"))
    print(actual, h)
    assert actual == h
