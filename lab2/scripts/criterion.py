import itertools

#بِسْمِ اللهِ الرَّحْمٰنِ الرَّحِيْمِ
#CONSTANTS
ALPHABET = "абвгґдеєжзиіїйклмнопрстуфхцчшщьюя"
GRAMS = [1, 2]
MONOGRAMS = dict.fromkeys(ALPHABET, 0)
BIGRAMS = dict.fromkeys([a + b for a, b in itertools.product(ALPHABET, repeat=2)], 0)


with open("./lab2/data/another_zbirka_cleared.txt", encoding="utf-8") as file:
    text = file.read().lower()
    text = "".join(ch for ch in text if ch in ALPHABET)

    for ch in text:
        MONOGRAMS[ch] += 1

    for i in range(len(text) - 1):
        bigram = text[i:i+2]
        BIGRAMS[bigram] += 1

