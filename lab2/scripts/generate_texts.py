import csv
import random


ALPHABET = "абвгдеєжзиіїйклмнопрстуфхцчшщьюя"

L_N = [
    (10, 10000),
    (100, 10000),
    (1000, 10000),
    (10000, 1000)
]


def vigenere_encrypt(text: str, key: str) -> str:
    enc_text = []
    for i in range(len(text)):
        t_index = ALPHABET.index(text[i])
        k_index = ALPHABET.index(key[i % len(key)])
        enc_char = ALPHABET[(t_index + k_index) % len(ALPHABET)]
        enc_text.append(enc_char)
    return "".join(enc_text)


def affine_encrypt(text: str, key_a: int, key_b: int) -> str:
    enc_text = []
    for i in range(len(text)):
        t_index = ALPHABET.index(text[i])
        enc_char = ALPHABET[(t_index * key_a + key_b) % len(ALPHABET)]
        enc_text.append(enc_char)
    return "".join(enc_text)


def uniform_distribution(l: int) -> str:
    text = []
    for i in range(l):
        text.append(ALPHABET[random.randint(0, len(ALPHABET) - 1)])
    return "".join(text)


def one_more_distribution(l: int) -> str:
    s_0 = ALPHABET[random.randint(0, len(ALPHABET) - 1)]
    s_1 = ALPHABET[random.randint(0, len(ALPHABET) - 1)]
    text = [ALPHABET.index((ALPHABET.index(s_1) + ALPHABET.index(s_0)) % len(ALPHABET))]
    for i in range(l):
        s_0 = s_1
        s_1 = ALPHABET[random.randint(0, len(ALPHABET) - 1)]
        text.append(ALPHABET.index((ALPHABET.index(s_1) + ALPHABET.index(s_0)) % len(ALPHABET)))
    return "".join(text)


# with open("franko_zbirka_cleared.txt") as f:
