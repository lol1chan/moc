import csv
from typing import List, Tuple

# ----------------------------
# Парсинг CSV для варіанта XX
# ----------------------------

def load_probabilities() -> Tuple[List[float], List[float]]:
    """
    Зчитує prob_XX.csv і повертає:
      - p_plain: ймовірності відкритих текстів (довжина 20, float)
      - p_key:   ймовірності ключів (довжина 20, float)
    """
    path = f"prob_01.csv"
    rows: List[List[str]] = []
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        for row in reader:
            # ігноруємо порожні рядки
            if not row or all(cell.strip() == "" for cell in row):
                continue
            rows.append([cell.strip() for cell in row])

    p_plain = [float(x.replace(",", ".")) for x in rows[0]]
    p_key   = [float(x.replace(",", ".")) for x in rows[1]]

    return p_plain, p_key


def load_cipher_table() -> List[List[int]]:
    """
    Зчитує table_XX.csv і повертає 20×20 таблицю з int.
    Стовпці — відкритий текст (j), рядки — ключ (i), елемент — індекс h шифротексту.
    """
    path = f"table_01.csv"
    matrix: List[List[int]] = []
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row or all(cell.strip() == "" for cell in row):
                continue
            matrix.append([int(cell.strip()) for cell in row])

    return matrix


def main():
    p_plain, p_key = load_probabilities()
    table = load_cipher_table()

    print(f"prob_01.csv: 2×20 (перевірено)")
    print(f"  Σ P(plain) = {sum(p_plain):.6f}, Σ P(key) = {sum(p_key):.6f}")
    print(f"table_01.csv: 20×20 (перевірено)")

    # Приклад доступу: h для i-го ключа та j-го відкритого тексту
    i, j = 0, 0  # 0-початкова індексація у Python
    h = table[i][j]
    print(f"Приклад: h = table[i={i+1}][j={j+1}] = {h}")

if __name__ == "__main__":
    main()