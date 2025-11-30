#!/usr/bin/env python3
import os
import json
from pedersen_commit import PRIME, G, H, pedersen_commit, COMMITMENTS_DIR

K = 3   # k fixo conforme solicitado

# ------------------------------------------------------------
# Helpers: ler commits
# ------------------------------------------------------------
def carregar_commitments_individuais():
    commits = []
    for fname in sorted(os.listdir(COMMITMENTS_DIR)):
        if fname.startswith("commitment_") and fname.endswith(".txt"):
            path = os.path.join(COMMITMENTS_DIR, fname)
            data = json.load(open(path))
            commits.append({
                "id": int(data["share"]),
                "x": int(data["x"]),
                "y": int(data["y"]),
                "r": int(data["r"]),
                "C": int(data["commitment"]),
                "H": int(data["H_used"])
            })
    if not commits:
        raise RuntimeError("Nenhum commitment_xx.txt encontrado na pasta commitments/")
    return commits

# ------------------------------------------------------------
# Lagrange: avaliar polinômio no ponto t a partir de k pontos (xi, yi)
# ------------------------------------------------------------
def lagrange_eval(t, xs, ys, p):
    k = len(xs)
    total = 0
    for i in range(k):
        xi = xs[i]
        yi = ys[i]
        num = 1
        den = 1
        for j in range(k):
            if i == j:
                continue
            xj = xs[j]
            num = (num * (t - xj)) % p
            den = (den * (xi - xj)) % p
        inv_den = pow(den, p - 2, p)
        li = (num * inv_den) % p
        total = (total + yi * li) % p
    return total

# ------------------------------------------------------------
# Verifica integridade individual: recomputa C = g^y h^r
# ------------------------------------------------------------
def verificar_commitment_individual(entry):
    return pedersen_commit(entry["y"], entry["r"], g=G, h=entry["H"], p=PRIME) == entry["C"]

# ------------------------------------------------------------
# Verificação global usando Lagrange (k fixo = 3)
# ------------------------------------------------------------
def verificar_dealer():
    commits = carregar_commitments_individuais()
    n = len(commits)
    print(f"Encontrados {n} commitments individuais.\n")

    # 1) integridade individual
    for c in commits:
        if not verificar_commitment_individual(c):
            print(f"[ERRO] Share {c['id']:02d} foi alterada! Commitment inválido.")
            return
        print(f"[OK] Share {c['id']:02d} íntegra")

    print("\n[OK] Todas as shares são individualmente válidas.")
    print(f"[INFO] Usando k = {K} para reconstrução do polinômio.\n")

    if n < K:
        print(f"ERRO: Existem apenas {n} commits, mas k = {K} é necessário.")
        return

    # base: primeiras K shares
    base = commits[:K]
    xs_base = [c["x"] for c in base]
    ys_base = [c["y"] for c in base]
    rs_base = [c["r"] for c in base]

    # 2) Verificar todas as shares pela reconstrução da base
    for c in commits:
        xi = c["x"]
        yi = c["y"]
        ri = c["r"]

        y_eval = lagrange_eval(xi, xs_base, ys_base, PRIME)
        r_eval = lagrange_eval(xi, xs_base, rs_base, PRIME)

        if yi != y_eval or ri != r_eval:
            print(f"[ERRO] Share {c['id']:02d} NÃO segue o polinômio reconstruído.")
            print(f"  esperado: y={yi}, r={ri}")
            print(f"  obtido:   y={y_eval}, r={r_eval}")
            print("\n→ Dealer malicioso!.")
            return

        print(f"[OK] Share {c['id']:02d} consistente com o polinômio reconstruído")

    print("\n[✔] Todas as shares são consistentes com o polinômio (k=3).")
    print("[✔] Dealer HONESTO (consistência verificada)\n")

# ------------------------------------------------------------
if __name__ == "__main__":
    verificar_dealer()
