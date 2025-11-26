import itertools
import csv
import os
from collections import Counter

from criteria import (
    criterion_most_frequent2_0,
    criterion_most_frequent2_1,
    criterion_most_frequent2_2,
    criterion_most_frequent2_3,
    criterion_index_of_coincidence,
    criterion_empty_boxes5_0,
    criterion_compression6_0
)


#CONSTANTS
ALPHABET = "абвгдеєжзиіїйклмнопрстуфхцчшщьюя"
DISTORTIONS = [
    {"name": "vizhener_1", "title": "Спотворення за допомогою шифру Віженера (r = 1)"},
    {"name": "vizhener_5", "title": "Спотворення за допомогою шифру Віженера (r = 5)"},
    {"name": "vizhener_10", "title": "Спотворення за допомогою шифру Віженера (r = 10)"},
    {"name": "aphine", "title": "Спотворення за допомогою афінного шифру"},
    {"name": "uniform", "title": "Рівномірний випадковий розподіл"},
    {"name": "recursive", "title": "Рекурсивний модульний розподіл"}
]
DISTORTION_NAMES = [d["name"] for d in DISTORTIONS]
DISTORTION_TABLES = {name: {} for name in DISTORTION_NAMES}
COMPRESSION_TABLES = {}
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LAB2_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
DATA_DIR = os.path.join(LAB2_DIR, "data")
GENERATED_DIR = os.path.join(LAB2_DIR, "generated_texts")
RESULTS_DIR = os.path.join(LAB2_DIR, "results")
DISTORTIONS_DIR = os.path.join(RESULTS_DIR, "distortions")
GRAMS = [1, 2]
MONOGRAMS = dict.fromkeys(ALPHABET, 0)
BIGRAMS = dict.fromkeys([a + b for a, b in itertools.product(ALPHABET, repeat=2)], 0)
L_Ns = [
    (10, 10000),
    (100, 10000),
    (1000, 10000),
    (10000, 1000)
]


def _ensure_distortion_record(variant, key, L, N, criterion_label, params):
    """Ensure base row exists for given distortion/criterion combination."""
    table = DISTORTION_TABLES[variant]
    if key not in table:
        table[key] = {
            "L": L,
            "N": N,
            "criterion": criterion_label,
            "params": params,
            "mono": {"FP": "", "FN": ""},
            "bi": {"FP": "", "FN": ""}
        }
    else:
        if params:
            table[key]["params"] = params
    return table[key]


def record_distortion_stats(criterion_key, criterion_label, params_label, gram_type, L, N, fp, fn_list):
    """Store FP/FN pairs per distortion variant for downstream aggregation."""
    if len(fn_list) != len(DISTORTION_NAMES):
        raise ValueError(f"{criterion_label} returned {len(fn_list)} FN values, expected {len(DISTORTION_NAMES)}.")

    for idx, variant in enumerate(DISTORTION_NAMES):
        record = _ensure_distortion_record(variant, (L, N, criterion_key), L, N, criterion_label, params_label)
        record[gram_type]["FP"] = fp
        record[gram_type]["FN"] = fn_list[idx]


def record_compression_stats(algorithm, L, N, threshold, fp, fn_list):
    """Collect FP/FN per distortion for compression algorithms (criterion 6.0)."""
    table = COMPRESSION_TABLES.setdefault(algorithm, {})
    for idx, variant in enumerate(DISTORTION_NAMES):
        key = (variant, L, N)
        if key not in table:
            table[key] = {
                "distortion": variant,
                "L": L,
                "N": N,
                "threshold": threshold,
                "FP": "",
                "FN": ""
            }
        table[key]["FP"] = fp
        table[key]["FN"] = fn_list[idx]


class RecordCallback:
    def __init__(self):
        pass
    
    def __call__(self, criterion_key, criterion_label, params_label, gram_type, L, N, fp, fn_list):
        record_distortion_stats(criterion_key, criterion_label, params_label, gram_type, L, N, fp, fn_list)
    
    def compression(self, algorithm, L, N, threshold, fp, fn_list):
        record_compression_stats(algorithm, L, N, threshold, fp, fn_list)


def write_distortion_tables(output_dir=DISTORTIONS_DIR):
    os.makedirs(output_dir, exist_ok=True)
    header = ["L", "criterion", "params", "FP_mono", "FN_mono", "FP_bi", "FN_bi"]

    for variant, rows in DISTORTION_TABLES.items():
        row_values = sorted(rows.values(), key=lambda r: (r["L"], r["criterion"], r["params"]))
        if not row_values:
            continue
        path = os.path.join(output_dir, f"{variant}.csv")
        with open(path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow(header)
            for row in row_values:
                writer.writerow([
                    row["L"],
                    row["criterion"],
                    row["params"],
                    row["mono"]["FP"],
                    row["mono"]["FN"],
                    row["bi"]["FP"],
                    row["bi"]["FN"]
                ])
        print(f"Distortion table saved: {path}")


def write_compression_tables(output_dir=DISTORTIONS_DIR):
    os.makedirs(output_dir, exist_ok=True)
    header = ["distortion", "L", "threshold", "FP", "FN"]
    for algorithm, rows in COMPRESSION_TABLES.items():
        if not rows:
            continue
        row_values = sorted(rows.values(), key=lambda r: (r["distortion"], r["L"]))
        path = os.path.join(output_dir, f"compression_{algorithm}.csv")
        with open(path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow(header)
            for row in row_values:
                writer.writerow([
                    row["distortion"],
                    row["L"],
                    row["threshold"],
                    row["FP"],
                    row["FN"]
                ])
        print(f"Compression table saved: {path}")


# статистика монограм та біграм
stats_source = os.path.join(DATA_DIR, "franko_zbirka_cleared.txt")
with open(stats_source, encoding="utf-8") as file:
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


def main():
    callback = RecordCallback()
    
    print("Запуск критеріїв...")
    
    print("Обчислення критерію 2.0...")
    criterion_most_frequent2_0(
        L_Ns=L_Ns,
        MONOGRAMS_MOST_FREQUENT=MONOGRAMS_MOST_FREQUENT,
        BIGRAMS_MOST_FREQUENT=BIGRAMS_MOST_FREQUENT,
        record_callback=callback,
        generated_dir=GENERATED_DIR
    )
    
    print("Обчислення критерію 2.1...")
    criterion_most_frequent2_1(
        L_Ns=L_Ns,
        MONOGRAMS_MOST_FREQUENT=MONOGRAMS_MOST_FREQUENT,
        BIGRAMS_MOST_FREQUENT=BIGRAMS_MOST_FREQUENT,
        record_callback=callback,
        generated_dir=GENERATED_DIR
    )
    
    print("Обчислення критерію 2.2...")
    criterion_most_frequent2_2(
        L_Ns=L_Ns,
        MONOGRAMS_MOST_FREQUENT=MONOGRAMS_MOST_FREQUENT,
        BIGRAMS_MOST_FREQUENT=BIGRAMS_MOST_FREQUENT,
        record_callback=callback,
        generated_dir=GENERATED_DIR
    )
    
    print("Обчислення критерію 2.3...")
    criterion_most_frequent2_3(
        L_Ns=L_Ns,
        MONOGRAMS_MOST_FREQUENT=MONOGRAMS_MOST_FREQUENT,
        BIGRAMS_MOST_FREQUENT=BIGRAMS_MOST_FREQUENT,
        record_callback=callback,
        generated_dir=GENERATED_DIR
    )
    
    print("Обчислення критерію 4.0...")
    criterion_index_of_coincidence(
        L_Ns=L_Ns,
        ls=(1, 2),
        record_callback=callback,
        generated_dir=GENERATED_DIR
    )
    
    print("Обчислення критерію 5.0...")
    criterion_empty_boxes5_0(
        L_Ns=L_Ns,
        SORTED_MONOGRAMS=SORTED_MONOGRAMS,
        SORTED_BIGRAMS=SORTED_BIGRAMS,
        j_values_mono=[30, 50],
        j_values_bi=[50, 100, 200],
        record_callback=callback,
        generated_dir=GENERATED_DIR
    )
    
    print("Обчислення критерію 6.0...")
    criterion_compression6_0(
        L_Ns=L_Ns,
        compression_algorithms=("lzma", "deflate", "bwt"),
        record_callback=callback,
        generated_dir=GENERATED_DIR
    )
    
    print("\nГенерація таблиць спотворень...")
    write_distortion_tables()
    write_compression_tables()
    
    print("\nDone")


if __name__ == "__main__":
    main()
