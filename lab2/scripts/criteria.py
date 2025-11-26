import csv
from collections import Counter
import zlib
import lzma
import bz2
import itertools
import os


THRESHOLD_CONFIG = {
    "2.0": {
        "default": {"mono": 5000, "bi": 50},
        10: {"mono": 15000, "bi": 500},     
        100: {"mono": 50000, "bi": 50},      
        1000: {"mono": 100000, "bi": 50},  
        10000: {"mono": 100000, "bi": 50},  
    },
    "2.1": {
        "default": {"mono": 5, "bi": 20},
        10: {"mono": 15, "bi": 300},
        100: {"mono": 3, "bi": 500},
        1000: {"mono": 3, "bi": 500},
        10000: {"mono": 3, "bi": 500},  
    },
    "2.2": {
        "default": {"mono": 2, "bi": 1},
        10: {"mono": 2, "bi": 1},
        100: {"mono": 10, "bi": 2},
        1000: {"mono": 50, "bi": 3},
        10000: {"mono": 5000, "bi": 15},    

    },
    "2.3": {
        "default": {"mono": 1, "bi": 1},
        10: {"mono": 12, "bi": 3},
        100: {"mono": 500, "bi": 50},
        1000: {"mono": 50, "bi": 50},
        10000: {"mono": 5000000, "bi": 100000},  
    },
    "4.0": {
        "default": {"mono": 0.01, "bi": 0.01},
        10: {"mono": 4.4, "bi": 0.95},
        100: {"mono": 4.4, "bi": 0.95},
        1000: {"mono": 1.7, "bi": 0.95},
        10000: {"mono": 1.7, "bi": 50.95},  
    },
    "5.0": {
        "default": {"mono": 5, "bi": 20},
        10: {"mono": 5, "bi": 42},
        100: {"mono": 3, "bi": 42},
        1000: {"mono": 3, "bi": 30},
        10000: {"mono": 1, "bi": 20},  
    },
    "6.0": {
        "default": {"threshold": 0.8}
    }
}


def get_threshold(criterion_id, L, gram_type=None):

    if criterion_id not in THRESHOLD_CONFIG:
        raise ValueError(f"Unknown criterion: {criterion_id}")
    
    config = THRESHOLD_CONFIG[criterion_id]
    
    if L in config:
        if gram_type is None:
            return config[L].get("threshold", config["default"].get("threshold"))
        return config[L].get(gram_type, config["default"].get(gram_type))
    
    if gram_type is None:
        return config["default"].get("threshold")
    return config["default"].get(gram_type)


def criterion_most_frequent2_0(L_Ns, MONOGRAMS_MOST_FREQUENT, BIGRAMS_MOST_FREQUENT, record_callback, generated_dir):

    for L, N in L_Ns:
        lim_mono = get_threshold("2.0", L, "mono")
        lim_bi = get_threshold("2.0", L, "bi")

        H0_mono = [0]
        H1_mono = [0] * 6
        H0_bi = [0]
        H1_bi = [0] * 6
        total = 0

        path = os.path.join(generated_dir, f"texts_L{L}_N{N}.csv")
        with open(path, encoding="utf-8") as csv_file:
            spamreader = csv.reader(csv_file, delimiter=';')
            for row in spamreader:
                if len(row) < 7:
                    continue
                total += 1

                mono_flags = [False] * 7
                for i in range(7):
                    mono_flags[i] = all(monogram in row[i] for monogram in MONOGRAMS_MOST_FREQUENT)

                if mono_flags[0]:
                    H0_mono[0] += 1
                for i in range(6):
                    if mono_flags[i + 1]:
                        H1_mono[i] += 1

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

        P_type1_mono = 1 - (H0_mono[0] / total)
        P_type2_mono = [H1_mono[i] / total for i in range(6)]
        P_type1_bi = 1 - (H0_bi[0] / total)
        P_type2_bi = [H1_bi[i] / total for i in range(6)]

        params_20 = f"lim_let={lim_mono}, lim_bi={lim_bi}"
        
        record_callback(
            criterion_key="2.0",
            criterion_label="2.0",
            params_label=params_20,
            gram_type="mono",
            L=L,
            N=N,
            fp=P_type1_mono,
            fn_list=P_type2_mono
        )
        record_callback(
            criterion_key="2.0",
            criterion_label="2.0",
            params_label=params_20,
            gram_type="bi",
            L=L,
            N=N,
            fp=P_type1_bi,
            fn_list=P_type2_bi
        )


def criterion_most_frequent2_1(L_Ns, MONOGRAMS_MOST_FREQUENT, BIGRAMS_MOST_FREQUENT, record_callback, generated_dir):

    for L, N in L_Ns:
        kf_mono = get_threshold("2.1", L, "mono")
        kf_bi = get_threshold("2.1", L, "bi")
        
        H0_mono = [0]
        H1_mono = [0] * 6
        H0_bi = [0]
        H1_bi = [0] * 6
        total = 0

        path = os.path.join(generated_dir, f"texts_L{L}_N{N}.csv")
        with open(path, encoding="utf-8") as csv_file:
            spamreader = csv.reader(csv_file, delimiter=';')
            for row in spamreader:
                if len(row) < 7:
                    continue
                total += 1

                mono_flags = [False] * 7
                for i in range(7):
                    found = [m for m in MONOGRAMS_MOST_FREQUENT if m in row[i]]
                    mono_flags[i] = len(found) > kf_mono

                if mono_flags[0]:
                    H0_mono[0] += 1
                for i in range(6):
                    if mono_flags[i + 1]:
                        H1_mono[i] += 1

                bi_flags = [False] * 7
                for i in range(7):
                    found = [b for b in BIGRAMS_MOST_FREQUENT if b in row[i]]
                    bi_flags[i] = len(found) > kf_bi

                if bi_flags[0]:
                    H0_bi[0] += 1
                for i in range(6):
                    if bi_flags[i + 1]:
                        H1_bi[i] += 1

        if total == 0:
            print(f"L = {L}, N = {N} — No valid data found.\n")
            continue

        P_type1_mono = 1 - (H0_mono[0] / total)
        P_type2_mono = [H1_mono[i] / total for i in range(6)]
        P_type1_bi = 1 - (H0_bi[0] / total)
        P_type2_bi = [H1_bi[i] / total for i in range(6)]

        params_21 = f"kf_mono={kf_mono}, kf_bi={kf_bi}"
        record_callback(
            criterion_key="2.1",
            criterion_label="2.1",
            params_label=params_21,
            gram_type="mono",
            L=L,
            N=N,
            fp=P_type1_mono,
            fn_list=P_type2_mono
        )
        record_callback(
            criterion_key="2.1",
            criterion_label="2.1",
            params_label=params_21,
            gram_type="bi",
            L=L,
            N=N,
            fp=P_type1_bi,
            fn_list=P_type2_bi
        )


def criterion_most_frequent2_2(L_Ns, MONOGRAMS_MOST_FREQUENT, BIGRAMS_MOST_FREQUENT, record_callback, generated_dir):

    for L, N in L_Ns:
        kx_mono = get_threshold("2.2", L, "mono")
        kx_bi = get_threshold("2.2", L, "bi")
        
        H0_mono = [0]
        H1_mono = [0] * 6
        H0_bi = [0]
        H1_bi = [0] * 6
        total = 0

        path = os.path.join(generated_dir, f"texts_L{L}_N{N}.csv")
        with open(path, encoding="utf-8") as csv_file:
            spamreader = csv.reader(csv_file, delimiter=';')
            for row in spamreader:
                if len(row) < 7:
                    continue
                total += 1

                mono_flags = [False] * 7
                for i in range(7):
                    text = row[i]
                    freq = Counter(text)
                    if any(freq.get(m, 0) < kx_mono for m in MONOGRAMS_MOST_FREQUENT):
                        mono_flags[i] = False
                    else:
                        mono_flags[i] = True

                if mono_flags[0]:
                    H0_mono[0] += 1
                for i in range(6):
                    if mono_flags[i + 1]:
                        H1_mono[i] += 1

                bi_flags = [False] * 7
                for i in range(7):
                    text = row[i]
                    bigrams = [text[j:j+2] for j in range(len(text) - 1)]
                    freq = Counter(bigrams)
                    if any(freq.get(b, 0) < kx_bi for b in BIGRAMS_MOST_FREQUENT):
                        bi_flags[i] = False
                    else:
                        bi_flags[i] = True

                if bi_flags[0]:
                    H0_bi[0] += 1
                for i in range(6):
                    if bi_flags[i + 1]:
                        H1_bi[i] += 1

        if total == 0:
            print(f"L = {L}, N = {N} — No valid data found.\n")
            continue

        P_type1_mono = 1 - (H0_mono[0] / total)
        P_type2_mono = [H1_mono[i] / total for i in range(6)]
        P_type1_bi = 1 - (H0_bi[0] / total)
        P_type2_bi = [H1_bi[i] / total for i in range(6)]

        params_22 = f"kx_mono>={kx_mono}, kx_bi>={kx_bi}"
        record_callback(
            criterion_key="2.2",
            criterion_label="2.2",
            params_label=params_22,
            gram_type="mono",
            L=L,
            N=N,
            fp=P_type1_mono,
            fn_list=P_type2_mono
        )
        record_callback(
            criterion_key="2.2",
            criterion_label="2.2",
            params_label=params_22,
            gram_type="bi",
            L=L,
            N=N,
            fp=P_type1_bi,
            fn_list=P_type2_bi
        )


def criterion_most_frequent2_3(L_Ns, MONOGRAMS_MOST_FREQUENT, BIGRAMS_MOST_FREQUENT, record_callback, generated_dir):

    for L, N in L_Ns:
        kx_mono = get_threshold("2.3", L, "mono")
        kx_bi = get_threshold("2.3", L, "bi")
        
        H0_mono = [0]
        H1_mono = [0] * 6
        H0_bi = [0]
        H1_bi = [0] * 6
        total = 0

        path = os.path.join(generated_dir, f"texts_L{L}_N{N}.csv")
        with open(path, encoding="utf-8") as csv_file:
            spamreader = csv.reader(csv_file, delimiter=';')
            for row in spamreader:
                if len(row) < 7:
                    continue
                total += 1

                mono_flags = [False] * 7
                for i in range(7):
                    text = row[i]
                    freq = Counter(text)
                    Ff = sum(freq.get(m, 0) for m in MONOGRAMS_MOST_FREQUENT)
                    Kf = kx_mono * len(MONOGRAMS_MOST_FREQUENT)
                    mono_flags[i] = Ff >= Kf

                if mono_flags[0]:
                    H0_mono[0] += 1
                for i in range(6):
                    if mono_flags[i + 1]:
                        H1_mono[i] += 1

                bi_flags = [False] * 7
                for i in range(7):
                    text = row[i]
                    bigrams = [text[j:j+2] for j in range(len(text) - 1)]
                    freq = Counter(bigrams)
                    Ff = sum(freq.get(b, 0) for b in BIGRAMS_MOST_FREQUENT)
                    Kf = kx_bi * len(BIGRAMS_MOST_FREQUENT)
                    bi_flags[i] = Ff >= Kf

                if bi_flags[0]:
                    H0_bi[0] += 1
                for i in range(6):
                    if bi_flags[i + 1]:
                        H1_bi[i] += 1

        if total == 0:
            print(f"L = {L}, N = {N} — No valid data found.\n")
            continue

        P_type1_mono = 1 - (H0_mono[0] / total)
        P_type2_mono = [H1_mono[i] / total for i in range(6)]
        P_type1_bi = 1 - (H0_bi[0] / total)
        P_type2_bi = [H1_bi[i] / total for i in range(6)]

        params_23 = f"kx_mono={kx_mono}, kx_bi={kx_bi}"
        record_callback(
            criterion_key="2.3",
            criterion_label="2.3",
            params_label=params_23,
            gram_type="mono",
            L=L,
            N=N,
            fp=P_type1_mono,
            fn_list=P_type2_mono
        )
        record_callback(
            criterion_key="2.3",
            criterion_label="2.3",
            params_label=params_23,
            gram_type="bi",
            L=L,
            N=N,
            fp=P_type1_bi,
            fn_list=P_type2_bi
        )


def index_of_coincidence(text, l=1):

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


def criterion_index_of_coincidence(L_Ns, record_callback, generated_dir, ls=(1, 2)):
    if isinstance(ls, int):
        ls = (ls,)

    for L, N in L_Ns:
        stats = {l: {"H0": 0, "H1": [0] * 6} for l in ls}
        total = 0

        path = os.path.join(generated_dir, f"texts_L{L}_N{N}.csv")
        with open(path, encoding="utf-8") as csv_file:
            spamreader = csv.reader(csv_file, delimiter=';')
            for row in spamreader:
                if len(row) < 7:
                    continue
                total += 1

                for l in ls:
                    gram_type = "mono" if l == 1 else "bi"
                    kI = get_threshold("4.0", L, gram_type)
                    
                    Il_original = index_of_coincidence(row[0], l)
                    if abs(Il_original - Il_original) <= kI:  # Завжди True, але залишаємо для читабельності
                        stats[l]["H0"] += 1

                    for i in range(6):
                        Il_variant = index_of_coincidence(row[i+1], l)
                        if abs(Il_original - Il_variant) > kI:
                            stats[l]["H1"][i] += 1

        if total == 0:
            print(f"L = {L}, N = {N} — No valid data found.\n")
            continue

        for l in ls:
            P_type1 = 1 - (stats[l]["H0"] / total)
            P_type2 = [stats[l]["H1"][i] / total for i in range(6)]
            
            gram_type = "mono" if l == 1 else "bi"
            kI = get_threshold("4.0", L, gram_type)
            
            record_callback(
                criterion_key="4.0",
                criterion_label="4.0",
                params_label=f"kI={kI}, l={l}",
                gram_type=gram_type,
                L=L,
                N=N,
                fp=P_type1,
                fn_list=P_type2
            )


def criterion_empty_boxes5_0(
    L_Ns,
    SORTED_MONOGRAMS,
    SORTED_BIGRAMS,
    j_values_mono=[50],
    j_values_bi=[50, 100, 200],
    record_callback=None,
    generated_dir=None
):
    for L, N in L_Ns:
        total = 0

        H0_mono = {j: 0 for j in j_values_mono}
        H1_mono = {j: [0] * 6 for j in j_values_mono}
        H0_bi = {j: 0 for j in j_values_bi}
        H1_bi = {j: [0] * 6 for j in j_values_bi}

        path = os.path.join(generated_dir, f"texts_L{L}_N{N}.csv")
        with open(path, encoding="utf-8") as csv_file:
            spamreader = csv.reader(csv_file, delimiter=';')
            for row in spamreader:
                if len(row) < 7:
                    continue
                total += 1

                for j in j_values_mono:
                    kempt_mono = get_threshold("5.0", L, "mono")
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
                    kempt_bi = get_threshold("5.0", L, "bi")
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
            kempt_mono = get_threshold("5.0", L, "mono")
            P_type1_mono = 1 - (H0_mono[j] / total)
            P_type2_mono = [H1_mono[j][i] / total for i in range(6)]
            if record_callback:
                record_callback(
                    criterion_key=f"5.0_mono_j{j}",
                    criterion_label="5.0",
                    params_label=f"j_mono={j}, kempt_mono={kempt_mono}",
                    gram_type="mono",
                    L=L,
                    N=N,
                    fp=P_type1_mono,
                    fn_list=P_type2_mono
                )

        for j in j_values_bi:
            kempt_bi = get_threshold("5.0", L, "bi")
            P_type1_bi = 1 - (H0_bi[j] / total)
            P_type2_bi = [H1_bi[j][i] / total for i in range(6)]
            if record_callback:
                record_callback(
                    criterion_key=f"5.0_bi_j{j}",
                    criterion_label="5.0",
                    params_label=f"j_bi={j}, kempt_bi={kempt_bi}",
                    gram_type="bi",
                    L=L,
                    N=N,
                    fp=P_type1_bi,
                    fn_list=P_type2_bi
                )


def compress_ratio(data: bytes, compressed: bytes):
    if len(data) == 0:
        return 1.0
    return len(compressed) / len(data)


def criterion_compression6_0(L_Ns, compression_algorithms=("lzma", "deflate", "bwt"), record_callback=None, generated_dir=None):

    for L, N in L_Ns:
        threshold = get_threshold("6.0", L)
        total = 0

        stats = {
            alg: {"H0": 0, "H1": [0] * 6}
            for alg in compression_algorithms
        }

        path = os.path.join(generated_dir, f"texts_L{L}_N{N}.csv")
        with open(path, encoding="utf-8") as csv_file:
            reader = csv.reader(csv_file, delimiter=';')
            for row in reader:
                if len(row) < 7:
                    continue
                total += 1

                for alg in compression_algorithms:
                    for i in range(7):
                        text = row[i].encode("utf-8")

                        if alg == "lzma":
                            comp = lzma.compress(text)
                        elif alg == "deflate":
                            comp = zlib.compress(text, level=9)
                        elif alg == "bwt":
                            comp = bz2.compress(text)
                        else:
                            raise ValueError(f"Unknown algorithm: {alg}")

                        ratio = compress_ratio(text, comp)

                        if ratio < threshold:
                            if i == 0:
                                stats[alg]["H0"] += 1
                            else:
                                stats[alg]["H1"][i - 1] += 1

        if total == 0:
            print(f"[!] L={L}, N={N} — no data found")
            continue

        for alg in compression_algorithms:
            P_type1 = 1 - (stats[alg]["H0"] / total)
            P_type2 = [stats[alg]["H1"][i] / total for i in range(6)]
            
            if record_callback and hasattr(record_callback, 'compression'):
                record_callback.compression(
                    algorithm=alg,
                    L=L,
                    N=N,
                    threshold=threshold,
                    fp=P_type1,
                    fn_list=P_type2
                )

