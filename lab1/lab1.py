import csv
from typing import List, Tuple


def load_probabilities() -> Tuple[List[float], List[float]]:

    path = f"prob_01.csv"
    rows: List[List[str]] = []
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row or all(cell.strip() == "" for cell in row):
                continue
            rows.append([cell.strip() for cell in row])

    p_plain = [float(x.replace(",", ".")) for x in rows[0]]
    p_key   = [float(x.replace(",", ".")) for x in rows[1]]

    return p_plain, p_key


def load_cipher_table() -> List[List[int]]:

    path = f"table_01.csv"
    matrix: List[List[int]] = []
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row or all(cell.strip() == "" for cell in row):
                continue
            matrix.append([int(cell.strip()) for cell in row])

    return matrix



def compute_joint_P_M_C(p_plain: List[float], p_key: List[float], table: List[List[int]]) -> List[List[float]]:

    n = len(p_plain)
    joint = [[0.0 for _ in range(n)] for _ in range(n)]
    for m in range(n):
        for i in range(len(p_key)):
            c = table[i][m]
            joint[m][c] += p_plain[m] * p_key[i]
    return joint


def compute_P_C(joint: List[List[float]]) -> List[float]:

    n = len(joint)
    P_C = [0.0 for _ in range(n)]
    for m in range(n):
        for c in range(n):
            P_C[c] += joint[m][c]
    return P_C


def main():
    p_plain, p_key = load_probabilities()
    table = load_cipher_table()
    joint = compute_joint_P_M_C(p_plain, p_key, table)
    P_C = compute_P_C(joint)
    print("P(C):", [f"{x:.6f}" for x in P_C])
    print("P(M,C):")
    for m, row in enumerate(joint):
        print(m, [f"{x:.6f}" for x in row])





if __name__ == "__main__":
    main()