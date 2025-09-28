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

def compute_P_M_given_C(joint: List[List[float]], P_C: List[float]) -> List[List[float]]:

    n = len(joint)
    cond = [[0.0 for _ in range(n)] for _ in range(n)]
    for m in range(n):
        for c in range(n):
            pc = P_C[c]
            cond[m][c] = (joint[m][c] / pc) if pc > 0.0 else 0.0
    return cond


def compute_deterministic_decision(cond: List[List[float]]):

    n = len(cond)
    best_m = [0 for _ in range(n)]
    best_val = [0.0 for _ in range(n)]
    for c in range(n):
        m_star = 0
        p_star = cond[0][c]
        for m in range(1, n):
            if cond[m][c] > p_star:
                p_star = cond[m][c]
                m_star = m
        best_m[c] = m_star
        best_val[c] = p_star
    return best_m, best_val


def main():
    p_plain, p_key = load_probabilities()
    table = load_cipher_table()
    joint = compute_joint_P_M_C(p_plain, p_key, table)
    P_C = compute_P_C(joint)
    cond = compute_P_M_given_C(joint, P_C)


    best_m, best_val = compute_deterministic_decision(cond)
    print("Deterministic δ_D(c) = argmax_m P(M|C=c):")
    for c in range(len(P_C)):
        print(f"c={c} -> m*={best_m[c]} (P={best_val[c]:.6f})")

    avg_correct = sum(P_C[c] * best_val[c] for c in range(len(P_C)))
    bayes_risk_01 = 1.0 - avg_correct
    print(f"Avg correct prob (deterministic): {avg_correct:.6f}")
    print(f"Bayes risk (0-1 loss): {bayes_risk_01:.6f}")





if __name__ == "__main__":
    main()