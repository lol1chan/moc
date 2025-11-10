import itertools
import csv
from collections import Counter
import zlib
import lzma
import bz2


#بِسْمِ اللهِ الرَّحْمٰنِ الرَّحِيْمِ
#CONSTANTS
ALPHABET = "абвгґдеєжзиіїйклмнопрстуфхцчшщьюя"
GRAMS = [1, 2]
MONOGRAMS = dict.fromkeys(ALPHABET, 0)
BIGRAMS = dict.fromkeys([a + b for a, b in itertools.product(ALPHABET, repeat=2)], 0)
L_Ns = [
    (10, 10000),
    (100, 10000),
    (1000, 10000),
    (10000, 1000)
]

with open("./lab2/data/franko_zbirka_cleared.txt", encoding="utf-8") as file:
    text = file.read().lower()
    text = "".join(ch for ch in text if ch in ALPHABET)
    count_chars = 0
    count_bigrams = 0
    for ch in text:
        MONOGRAMS[ch] += 1
        count_chars += 1

    for i in range(len(text) - 1):
        bigram = text[i:i+2]
        count_bigrams += 1
        BIGRAMS[bigram] += 1



SORTED_MONOGRAMS = dict(sorted(MONOGRAMS.items(), key=lambda value: value[1], reverse=True))
SORTED_BIGRAMS = dict(sorted(BIGRAMS.items(), key=lambda value: value[1], reverse=True))
MONOGRAMS_MOST_FREQUENT = list(itertools.islice(SORTED_MONOGRAMS, 5))
BIGRAMS_MOST_FREQUENT = list(itertools.islice(SORTED_BIGRAMS, 5))
print(SORTED_MONOGRAMS)
print(SORTED_BIGRAMS)


def criterion_most_frequent2_0(L_Ns, MONOGRAMS_MOST_FREQUENT, BIGRAMS_MOST_FREQUENT, output_path="./lab2/results/error_probabilities2.0.csv"):
    results = []

    for L, N in L_Ns:
        # Initialize counters
        H0_mono = [0]
        H1_mono = [0] * 6
        H0_bi = [0]
        H1_bi = [0] * 6
        total = 0

        path = f"./lab2/generated_texts/texts_L{L}_N{N}.csv"
        with open(path, encoding="utf-8") as csv_file:
            spamreader = csv.reader(csv_file, delimiter=';')
            for row in spamreader:
                if len(row) < 7:
                    continue
                total += 1

                # --- MONOGRAM CRITERION ---
                mono_flags = [False] * 7
                for i in range(7):
                    mono_flags[i] = all(monogram in row[i] for monogram in MONOGRAMS_MOST_FREQUENT)

                if mono_flags[0]:
                    H0_mono[0] += 1
                for i in range(6):
                    if mono_flags[i + 1]:
                        H1_mono[i] += 1

                # --- BIGRAM CRITERION ---
                bi_flags = [False] * 7
                for i in range(7):
                    bi_flags[i] = all(bigram in row[i] for bigram in BIGRAMS_MOST_FREQUENT)

                if bi_flags[0]:
                    H0_bi[0] += 1
                for i in range(6):
                    if bi_flags[i + 1]:
                        H1_bi[i] += 1

        if total == 0:
            print(f"L = {L}, N = {N} — No valid data found.\n")
            continue

        # --- Calculate error probabilities ---
        P_type1_mono = 1 - (H0_mono[0] / total)
        P_type2_mono = [H1_mono[i] / total for i in range(6)]

        P_type1_bi = 1 - (H0_bi[0] / total)
        P_type2_bi = [H1_bi[i] / total for i in range(6)]

        # --- Save in memory ---
        results.append([
            L, N,
            P_type1_mono, *P_type2_mono,
            P_type1_bi, *P_type2_bi
        ])

    # --- Write to CSV ---
    header = [
        "L", "N",
        "P_type1_mono",
        "P_type2_mono_1", "P_type2_mono_2", "P_type2_mono_3", "P_type2_mono_4", "P_type2_mono_5", "P_type2_mono_6",
        "P_type1_bi",
        "P_type2_bi_1", "P_type2_bi_2", "P_type2_bi_3", "P_type2_bi_4", "P_type2_bi_5", "P_type2_bi_6"
    ]

    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(header)
        writer.writerows(results)

    print(f"Criterion 2.0 results saved to: {output_path}")


def criterion_most_frequent2_1(
    L_Ns,
    MONOGRAMS_MOST_FREQUENT,
    BIGRAMS_MOST_FREQUENT,
    kf_mono=5,
    kf_bi=20,
    output_path="./lab2/results/error_probabilities2.1.csv"
):
    results = []

    for L, N in L_Ns:
        H0_mono = [0]
        H1_mono = [0] * 6
        H0_bi = [0]
        H1_bi = [0] * 6
        total = 0

        path = f"./lab2/generated_texts/texts_L{L}_N{N}.csv"
        with open(path, encoding="utf-8") as csv_file:
            spamreader = csv.reader(csv_file, delimiter=';')
            for row in spamreader:
                if len(row) < 7:
                    continue
                total += 1

                # --- MONOGRAM CRITERION 2.1 ---
                mono_flags = [False] * 7
                for i in range(7):
                    found = [m for m in MONOGRAMS_MOST_FREQUENT if m in row[i]]
                    mono_flags[i] = len(found) > kf_mono  # H0 if more than kf frequent monograms

                if mono_flags[0]:
                    H0_mono[0] += 1
                for i in range(6):
                    if mono_flags[i + 1]:
                        H1_mono[i] += 1

                # --- BIGRAM CRITERION 2.1 ---
                bi_flags = [False] * 7
                for i in range(7):
                    found = [b for b in BIGRAMS_MOST_FREQUENT if b in row[i]]
                    bi_flags[i] = len(found) > kf_bi  # H0 if more than kf frequent bigrams

                if bi_flags[0]:
                    H0_bi[0] += 1
                for i in range(6):
                    if bi_flags[i + 1]:
                        H1_bi[i] += 1

        if total == 0:
            print(f"L = {L}, N = {N} — No valid data found.\n")
            continue

        # --- Calculate probabilities of errors ---
        P_type1_mono = 1 - (H0_mono[0] / total)
        P_type2_mono = [H1_mono[i] / total for i in range(6)]

        P_type1_bi = 1 - (H0_bi[0] / total)
        P_type2_bi = [H1_bi[i] / total for i in range(6)]

        # --- Save in memory ---
        results.append([
            L, N,
            kf_mono, P_type1_mono, *P_type2_mono,
            kf_bi, P_type1_bi, *P_type2_bi
        ])

    # --- Write results to CSV ---
    header = [
        "L", "N",
        "kf_mono", "P_type1_mono",
        "P_type2_mono_1", "P_type2_mono_2", "P_type2_mono_3", "P_type2_mono_4", "P_type2_mono_5", "P_type2_mono_6",
        "kf_bi", "P_type1_bi",
        "P_type2_bi_1", "P_type2_bi_2", "P_type2_bi_3", "P_type2_bi_4", "P_type2_bi_5", "P_type2_bi_6"
    ]

    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(header)
        writer.writerows(results)

    print(f"[✓] Criterion 2.1 results saved to: {output_path}")


def criterion_most_frequent2_2(
    L_Ns,
    MONOGRAMS_MOST_FREQUENT,
    BIGRAMS_MOST_FREQUENT,
    kx_mono=2,
    kx_bi=1,
    output_path="./lab2/results/error_probabilities2.2.csv"
):
    results = []

    for L, N in L_Ns:
        H0_mono = [0]
        H1_mono = [0] * 6
        H0_bi = [0]
        H1_bi = [0] * 6
        total = 0

        path = f"./lab2/generated_texts/texts_L{L}_N{N}.csv"
        with open(path, encoding="utf-8") as csv_file:
            spamreader = csv.reader(csv_file, delimiter=';')
            for row in spamreader:
                if len(row) < 7:
                    continue
                total += 1

                # --- MONOGRAM CRITERION 2.2 ---
                mono_flags = [False] * 7
                for i in range(7):
                    text = row[i]
                    freq = Counter(text)
                    # H1: if exists monogram with frequency < kx_mono
                    if any(freq.get(m, 0) < kx_mono for m in MONOGRAMS_MOST_FREQUENT):
                        mono_flags[i] = False  # accept H1
                    else:
                        mono_flags[i] = True   # accept H0

                if mono_flags[0]:
                    H0_mono[0] += 1
                for i in range(6):
                    if mono_flags[i + 1]:
                        H1_mono[i] += 1

                # --- BIGRAM CRITERION 2.2 ---
                bi_flags = [False] * 7
                for i in range(7):
                    text = row[i]
                    bigrams = [text[j:j+2] for j in range(len(text) - 1)]
                    freq = Counter(bigrams)
                    # H1: if exists bigram with frequency < kx_bi
                    if any(freq.get(b, 0) < kx_bi for b in BIGRAMS_MOST_FREQUENT):
                        bi_flags[i] = False  # accept H1
                    else:
                        bi_flags[i] = True   # accept H0

                if bi_flags[0]:
                    H0_bi[0] += 1
                for i in range(6):
                    if bi_flags[i + 1]:
                        H1_bi[i] += 1

        if total == 0:
            print(f"L = {L}, N = {N} — No valid data found.\n")
            continue

        # --- Calculate probabilities of errors ---
        P_type1_mono = 1 - (H0_mono[0] / total)
        P_type2_mono = [H1_mono[i] / total for i in range(6)]

        P_type1_bi = 1 - (H0_bi[0] / total)
        P_type2_bi = [H1_bi[i] / total for i in range(6)]

        # --- Save in memory ---
        results.append([
            L, N,
            kx_mono, P_type1_mono, *P_type2_mono,
            kx_bi, P_type1_bi, *P_type2_bi
        ])

    # --- Write to CSV ---
    header = [
        "L", "N",
        "kx_mono", "P_type1_mono",
        "P_type2_mono_1", "P_type2_mono_2", "P_type2_mono_3", "P_type2_mono_4", "P_type2_mono_5", "P_type2_mono_6",
        "kx_bi", "P_type1_bi",
        "P_type2_bi_1", "P_type2_bi_2", "P_type2_bi_3", "P_type2_bi_4", "P_type2_bi_5", "P_type2_bi_6"
    ]

    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(header)
        writer.writerows(results)

    print(f"[✓] Criterion 2.2 results saved to: {output_path}")

def criterion_most_frequent2_3(
    L_Ns,
    MONOGRAMS_MOST_FREQUENT,
    BIGRAMS_MOST_FREQUENT,
    kx_mono=1,
    kx_bi=1,
    output_path="./lab2/results/error_probabilities2.3.csv"
):
    results = []

    for L, N in L_Ns:
        H0_mono = [0]
        H1_mono = [0] * 6
        H0_bi = [0]
        H1_bi = [0] * 6
        total = 0

        path = f"./lab2/generated_texts/texts_L{L}_N{N}.csv"
        with open(path, encoding="utf-8") as csv_file:
            spamreader = csv.reader(csv_file, delimiter=';')
            for row in spamreader:
                if len(row) < 7:
                    continue
                total += 1

                # --- MONOGRAM CRITERION 2.3 ---
                mono_flags = [False] * 7
                for i in range(7):
                    text = row[i]
                    freq = Counter(text)
                    Ff = sum(freq.get(m, 0) for m in MONOGRAMS_MOST_FREQUENT)
                    Kf = kx_mono * len(MONOGRAMS_MOST_FREQUENT)
                    mono_flags[i] = Ff >= Kf  # True = H0, False = H1

                if mono_flags[0]:
                    H0_mono[0] += 1
                for i in range(6):
                    if mono_flags[i + 1]:
                        H1_mono[i] += 1

                # --- BIGRAM CRITERION 2.3 ---
                bi_flags = [False] * 7
                for i in range(7):
                    text = row[i]
                    bigrams = [text[j:j+2] for j in range(len(text) - 1)]
                    freq = Counter(bigrams)
                    Ff = sum(freq.get(b, 0) for b in BIGRAMS_MOST_FREQUENT)
                    Kf = kx_bi * len(BIGRAMS_MOST_FREQUENT)
                    bi_flags[i] = Ff >= Kf  # True = H0, False = H1

                if bi_flags[0]:
                    H0_bi[0] += 1
                for i in range(6):
                    if bi_flags[i + 1]:
                        H1_bi[i] += 1

        if total == 0:
            print(f"L = {L}, N = {N} — No valid data found.\n")
            continue

        # --- Calculate probabilities of errors ---
        P_type1_mono = 1 - (H0_mono[0] / total)
        P_type2_mono = [H1_mono[i] / total for i in range(6)]

        P_type1_bi = 1 - (H0_bi[0] / total)
        P_type2_bi = [H1_bi[i] / total for i in range(6)]

        # --- Save in memory ---
        results.append([
            L, N,
            kx_mono, P_type1_mono, *P_type2_mono,
            kx_bi, P_type1_bi, *P_type2_bi
        ])

    # --- Write to CSV ---
    header = [
        "L", "N",
        "kx_mono", "P_type1_mono",
        "P_type2_mono_1", "P_type2_mono_2", "P_type2_mono_3", "P_type2_mono_4", "P_type2_mono_5", "P_type2_mono_6",
        "kx_bi", "P_type1_bi",
        "P_type2_bi_1", "P_type2_bi_2", "P_type2_bi_3", "P_type2_bi_4", "P_type2_bi_5", "P_type2_bi_6"
    ]

    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(header)
        writer.writerows(results)

    print(f"Criterion 2.3 results saved to: {output_path}")

def index_of_coincidence(text, l=1):
    """
    Розрахунок індексу відповідності Il для тексту.
    """
    if l == 1:
        grams = text
    else:
        grams = [text[i:i+l] for i in range(len(text)-l+1)]
    freq = Counter(grams)
    L = len(grams)
    if L < 2:
        return 0
    Il = sum(c*(c-1) for c in freq.values()) / (L*(L-1))
    return Il

def criterion_index_of_coincidence(L_Ns, l=1, kI=0.01, output_path="./lab2/results/error_probabilities4.0.csv"):
    results = []

    for L, N in L_Ns:
        H0 = 0  # число випадків, коли Il у межах [Il-kI, Il+kI]
        H1 = [0] * 6  # для 6 спотворених варіантів
        total = 0

        path = f"./lab2/generated_texts/texts_L{L}_N{N}.csv"
        with open(path, encoding="utf-8") as csv_file:
            spamreader = csv.reader(csv_file, delimiter=';')
            for row in spamreader:
                if len(row) < 7:
                    continue
                total += 1

                # Індекс відповідності для оригінального тексту
                Il_original = index_of_coincidence(row[0], l)

                # Перевірка H0
                if abs(Il_original - Il_original) <= kI:
                    H0 += 1

                # Перевірка H1 для спотворених текстів
                for i in range(6):
                    Il_variant = index_of_coincidence(row[i+1], l)
                    if abs(Il_original - Il_variant) > kI:
                        H1[i] += 1

        if total == 0:
            print(f"L = {L}, N = {N} — No valid data found.\n")
            continue

        P_type1 = 1 - (H0 / total)
        P_type2 = [H1[i] / total for i in range(6)]

        results.append([L, N, P_type1, *P_type2])

    # --- Write to CSV ---
    header = ["L", "N", "P_type1", "P_type2_1", "P_type2_2", "P_type2_3", "P_type2_4", "P_type2_5", "P_type2_6"]
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(header)
        writer.writerows(results)

    print(f"[✓] Criterion 4.0 results saved to: {output_path}")


def criterion_empty_boxes5_0(
    L_Ns,
    SORTED_MONOGRAMS,
    SORTED_BIGRAMS,
    j_values_mono=[50],
    j_values_bi=[50, 100, 200],
    kempt_mono=5,
    kempt_bi=20,
    output_path="./lab2/results/error_probabilities5.0.csv"
):
    results = []

    for L, N in L_Ns:
        total = 0

        H0_mono = {j: 0 for j in j_values_mono}
        H1_mono = {j: [0] * 6 for j in j_values_mono}
        H0_bi = {j: 0 for j in j_values_bi}
        H1_bi = {j: [0] * 6 for j in j_values_bi}

        path = f"./lab2/generated_texts/texts_L{L}_N{N}.csv"
        with open(path, encoding="utf-8") as csv_file:
            spamreader = csv.reader(csv_file, delimiter=';')
            for row in spamreader:
                if len(row) < 7:
                    continue
                total += 1

                for j in j_values_mono:
                    rare_mono = list(SORTED_MONOGRAMS.keys())[-j:]  
                    for i in range(7):
                        text = row[i]
                        freq = Counter(text)
                        fempt = sum(1 for m in rare_mono if freq.get(m, 0) == 0)
                        if fempt <= kempt_mono:
                            if i == 0:
                                H0_mono[j] += 1
                            else:
                                H1_mono[j][i - 1] += 1

                for j in j_values_bi:
                    rare_bi = list(SORTED_BIGRAMS.keys())[-j:]  
                    for i in range(7):
                        text = row[i]
                        bigrams = [text[k:k+2] for k in range(len(text) - 1)]
                        freq = Counter(bigrams)
                        fempt = sum(1 for b in rare_bi if freq.get(b, 0) == 0)
                        if fempt <= kempt_bi:
                            if i == 0:
                                H0_bi[j] += 1
                            else:
                                H1_bi[j][i - 1] += 1

        if total == 0:
            print(f"L = {L}, N = {N} — No valid data found.")
            continue

        for j in j_values_mono:
            P_type1_mono = 1 - (H0_mono[j] / total)
            P_type2_mono = [H1_mono[j][i] / total for i in range(6)]
            results.append([L, N, "mono", j, kempt_mono, P_type1_mono, *P_type2_mono])

        for j in j_values_bi:
            P_type1_bi = 1 - (H0_bi[j] / total)
            P_type2_bi = [H1_bi[j][i] / total for i in range(6)]
            results.append([L, N, "bi", j, kempt_bi, P_type1_bi, *P_type2_bi])

    header = [
        "L", "N", "type", "j", "kempt",
        "P_type1",
        "P_type2_1", "P_type2_2", "P_type2_3", "P_type2_4", "P_type2_5", "P_type2_6"
    ]

    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(header)
        writer.writerows(results)

    print(f"[✓] Criterion 5.0 results saved to: {output_path}")


def compress_ratio(data: bytes, compressed: bytes):
    """Обчислення коефіцієнта стиснення."""
    if len(data) == 0:
        return 1.0
    return len(compressed) / len(data)


def criterion_compression6_0(
    L_Ns,
    compression_algorithms=("lzma", "deflate", "bwt"),
    threshold=0.8,
    output_path="./lab2/results/error_probabilities6.0.csv"
):
    """
    Критерій 6.0: стиснення тексту як ознака осмисленості.
    - LZMA, DEFLATE, BWT
    - threshold: якщо коеф. стиснення < threshold — вважаємо текст осмисленим (H0)
    """

    results = []

    for L, N in L_Ns:
        total = 0

        # Лічильники для кожного алгоритму
        stats = {
            alg: {"H0": 0, "H1": [0] * 6}
            for alg in compression_algorithms
        }

        path = f"./lab2/generated_texts/texts_L{L}_N{N}.csv"
        with open(path, encoding="utf-8") as csv_file:
            reader = csv.reader(csv_file, delimiter=';')
            for row in reader:
                if len(row) < 7:
                    continue
                total += 1

                for alg in compression_algorithms:
                    for i in range(7):
                        text = row[i].encode("utf-8")

                        # --- Стиснення ---
                        if alg == "lzma":
                            comp = lzma.compress(text)
                        elif alg == "deflate":
                            comp = zlib.compress(text, level=9)
                        elif alg == "bwt":
                            comp = bz2.compress(text)
                        else:
                            raise ValueError(f"Unknown algorithm: {alg}")

                        ratio = compress_ratio(text, comp)

                        # --- Критерій: менше threshold → осмислений (H0)
                        if ratio < threshold:
                            if i == 0:
                                stats[alg]["H0"] += 1
                            else:
                                stats[alg]["H1"][i - 1] += 1

        if total == 0:
            print(f"[!] L={L}, N={N} — no data found")
            continue

        # --- Обчислення ймовірностей помилок ---
        for alg in compression_algorithms:
            P_type1 = 1 - (stats[alg]["H0"] / total)
            P_type2 = [stats[alg]["H1"][i] / total for i in range(6)]
            results.append([L, N, alg, threshold, P_type1, *P_type2])

    # --- Запис результатів ---
    header = [
        "L", "N", "algorithm", "threshold",
        "P_type1",
        "P_type2_1", "P_type2_2", "P_type2_3", "P_type2_4", "P_type2_5", "P_type2_6"
    ]
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(header)
        writer.writerows(results)

    print(f"[✓] Criterion 6.0 (compression) results saved to: {output_path}")





criterion_most_frequent2_0(L_Ns=L_Ns, MONOGRAMS_MOST_FREQUENT=MONOGRAMS_MOST_FREQUENT, BIGRAMS_MOST_FREQUENT=BIGRAMS_MOST_FREQUENT)
criterion_most_frequent2_1(L_Ns=L_Ns, MONOGRAMS_MOST_FREQUENT=MONOGRAMS_MOST_FREQUENT, BIGRAMS_MOST_FREQUENT=BIGRAMS_MOST_FREQUENT)
criterion_most_frequent2_2(
    L_Ns=L_Ns,
    MONOGRAMS_MOST_FREQUENT=MONOGRAMS_MOST_FREQUENT,
    BIGRAMS_MOST_FREQUENT=BIGRAMS_MOST_FREQUENT,
    kx_mono=2,   # мінімальна кількість появ для монограм
    kx_bi=1      # мінімальна кількість появ для біграм
)
criterion_most_frequent2_3(
    L_Ns=L_Ns,
    MONOGRAMS_MOST_FREQUENT=MONOGRAMS_MOST_FREQUENT,
    BIGRAMS_MOST_FREQUENT=BIGRAMS_MOST_FREQUENT,
    kx_mono=1,
    kx_bi=1
)
criterion_index_of_coincidence(L_Ns=L_Ns, l=1, kI=0.01)

criterion_empty_boxes5_0(
    L_Ns=L_Ns,
    SORTED_MONOGRAMS=SORTED_MONOGRAMS,
    SORTED_BIGRAMS=SORTED_BIGRAMS,
    j_values_mono=[30, 50],
    j_values_bi=[50, 100, 200],
    kempt_mono=3,
    kempt_bi=10
)

criterion_compression6_0(
    L_Ns=L_Ns,
    compression_algorithms=("lzma", "deflate", "bwt"),
    threshold=0.8
)
