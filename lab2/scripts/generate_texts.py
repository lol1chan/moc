import csv
import random
import math

# constants
ALPHABET = "абвгґдеєжзиіїйклмнопрстуфхцчшщьюя"
L_Ns = [
    (10, 10000),
    (100, 10000),
    (1000, 10000),
    (10000, 1000)
]
zbirka = "./lab2/data/franko_zbirka_cleared.txt"

def vigenere_encrypt(text: str, key: str) -> str:
    enc_text = []
    for i in range(len(text)):
        t_index = ALPHABET.index(text[i])
        k_index = ALPHABET.index(key[i % len(key)])
        enc_char = ALPHABET[(t_index + k_index) % len(ALPHABET)]
        enc_text.append(enc_char)
    return "".join(enc_text)

def affine_encrypt(text: str, key_a: int, key_b: int) -> str:
    m = len(ALPHABET)
    enc_text = []
    for i in range(len(text)):
        t_index = ALPHABET.index(text[i])
        enc_char = ALPHABET[(t_index * key_a + key_b) % m]
        enc_text.append(enc_char)
    return "".join(enc_text)

def uniform_distribution(l: int) -> str:
    return "".join(random.choice(ALPHABET) for _ in range(l))

def recursive_distribution(l: int) -> str:
    m = len(ALPHABET)
    s0 = random.randint(0, m - 1)
    s1 = random.randint(0, m - 1)
    seq = [s0, s1]
    for _ in range(2, l):
        seq.append((seq[-1] + seq[-2]) % m)
    return "".join(ALPHABET[i] for i in seq)

def coprime_with_m(m):
    while True:
        a = random.randint(1, m - 1)
        if math.gcd(a, m) == 1:
            return a

# main logic
with open(zbirka, encoding="utf-8") as f:
    content = f.read()

for l, n in L_Ns:
    with open(f"./lab2/generated_texts/texts_L{l}_N{n}.csv", "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile, delimiter=';')
        writer.writerow(["X", "Vigenere_r1", "Vigenere_r5", "Vigenere_r10", "Affine", "Uniform", "Recursive"])

        for i in range(n):
            text = content[l * i : l * (i + 1)]
            if len(text) < l:
                break

            # Vigenère with r = 1, 5, 10
            v1 = vigenere_encrypt(text, "".join(random.choice(ALPHABET) for _ in range(1)))
            v5 = vigenere_encrypt(text, "".join(random.choice(ALPHABET) for _ in range(5)))
            v10 = vigenere_encrypt(text, "".join(random.choice(ALPHABET) for _ in range(10)))

            # Affine cipher
            a = coprime_with_m(len(ALPHABET))
            b = random.randint(0, len(ALPHABET) - 1)
            aff = affine_encrypt(text, a, b)

            # Uniform random text
            uni = uniform_distribution(l)

            # Recursive modular text
            rec = recursive_distribution(l)

            writer.writerow([text, v1, v5, v10, aff, uni, rec])
