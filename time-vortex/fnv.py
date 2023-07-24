import functools

# 32 bit FNV_prime = 2^24 + 2^8 + 0x93 = 16777619
# 32 bit offset_basis = 2166136261

FNV_32_PRIME: int = 0x01000193
FNV1_32_INIT: int = 0x811c9dc5
FNV_32_SIZE: int = 2 ** 32


def fnv_1a(data: bytes) -> int:
    assert isinstance(data, bytes)
    return functools.reduce(lambda hval, byte: ((hval ^ byte) * FNV_32_PRIME) % FNV_32_SIZE, data, FNV1_32_INIT)


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

# fnv_test_str[0]: 0x811c9dc5,
# fnv_test_str[1]: 0xe40c292c,
# fnv_test_str[2]: 0xe70c2de5,
# fnv_test_str[3]: 0xe60c2c52,
# fnv_test_str[4]: 0xe10c2473,
# fnv_test_str[5]: 0xe00c22e0,
# fnv_test_str[6]: 0xe30c2799,
# fnv_test_str[7]: 0x6222e842,
# fnv_test_str[8]: 0xa9f37ed7,
# fnv_test_str[9]: 0x3f5076ef,

#
# TEST(""),
# TEST("a"),
# TEST("b"),
# TEST("c"),
# TEST("d"),
# TEST("e"),
# TEST("f"),
# TEST("fo"),
# TEST("foo"),
# TEST("foob"),
# TEST("fooba"),
# TEST("foobar"),
#
