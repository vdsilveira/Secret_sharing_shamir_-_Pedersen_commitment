#!/usr/bin/env python3
import os
import sys
import json
from pedersen_commit import PRIME, G, H, pedersen_commit, COMMITMENTS_DIR

def carregar_commitments_individuais():
    commits = []
    for fname in sorted(os.listdir(COMMITMENTS_DIR)):
        if fname.startswith("commitment_") and fname.endswith(".txt"):
            path = os.path.join(COMMITMENTS_DIR, fname)
            data = json.load(open(path))
            commits.append({
                "fname": fname,
                "id": data["share"],
                "x": int(data["x"]),
                "y": int(data["y"]),
                "r": int(data["r"]),
                "C": int(data["commitment"]),
                "H": int(data["H_used"])
            })
    if not commits:
        raise RuntimeError("Nenhum commitment_xx.txt encontrado na pasta commitments/")
    return commits

def verificar_individuais(commits):
    print("=== Verificação individual (recomputa C = g^y h^r) ===")
    ok_all = True
    for c in commits:
        C_check = pedersen_commit(c["y"], c["r"], g=G, h=c["H"], p=PRIME)
        ok = (C_check == c["C"])
        print(f"Share {c['id']:02d}: commitment ok? {ok}")
        if not ok:
            print(f"  arquivo: {c['fname']}")
            print(f"  esperado C: {c['C']}")
            print(f"  recomputado C: {C_check}")
            ok_all = False
    return ok_all

def interpolar_polinomio(shares_xy, k):
    # Lagrange: retorna coeficientes a0..a_{k-1}
    xs = [p[0] for p in shares_xy]
    vs = [p[1] for p in shares_xy]
    coefs = [0]*k
    for i in range(k):
        xi, yi = xs[i], vs[i]
        Li = [1] + [0]*(k-1)
        for j in range(k):
            if i == j: continue
            xj = xs[j]
            inv = pow(xi - xj, PRIME-2, PRIME)
            scale = (-xj * inv) % PRIME
            for d in range(k-1, -1, -1):
                Li[d] = (Li[d] * scale + (Li[d-1] if d>0 else 0)) % PRIME
        for d in range(k):
            coefs[d] = (coefs[d] + yi * Li[d]) % PRIME
    return coefs

def eval_poly_from_coefs(coefs, x):
    res = 0
    power = 1
    for c in coefs:
        res = (res + c*power) % PRIME
        power = (power * x) % PRIME
    return res

def debug_verificacao(commits, k):
    print(f"\n=== Debug: usando k = {k} para interpolação ===\n")

    # escolher primeiras k shares para interpolar
    if len(commits) < k:
        print("ERRO: menos commits do que k")
        return

    # preparar dados
    shares_y = [(c["x"], c["y"]) for c in commits[:k]]
    shares_r = [(c["x"], c["r"]) for c in commits[:k]]

    coefs_y = interpolar_polinomio(shares_y, k)
    coefs_r = interpolar_polinomio(shares_r, k)

    print("Coeficientes y (a_j):")
    for j, a in enumerate(coefs_y):
        print(f"  a_{j} = {a}")
    print("Coeficientes r (b_j):")
    for j, b in enumerate(coefs_r):
        print(f"  b_{j} = {b}")

    # verifica que avaliar f(i) e g(i) reproduz y/r de cada commit
    print("\nVerificando que f(x_i) e g(x_i) reproduzem as shares:")
    for c in commits:
        xi = c["x"]
        yi_eval = eval_poly_from_coefs(coefs_y, xi)
        ri_eval = eval_poly_from_coefs(coefs_r, xi)
        match_y = (yi_eval == c["y"])
        match_r = (ri_eval == c["r"])
        print(f"Share {c['id']:02d}: y ok? {match_y}, r ok? {match_r}")
        if not match_y:
            print(f"  esperado y: {c['y']}, avaliado: {yi_eval}")
        if not match_r:
            print(f"  esperado r: {c['r']}, avaliado: {ri_eval}")

    # gerar commitments globais Cj = g^{a_j} h^{b_j}
    Cglob = []
    for a,b in zip(coefs_y, coefs_r):
        Cglob.append((pow(G, a, PRIME) * pow(H, b, PRIME)) % PRIME)

    print("\nComparando LHS (g^y h^r) e RHS (produto Cglob^{x^j}) para cada share:")
    for c in commits:
        xi = c["x"]; yi = c["y"]; ri = c["r"]
        LHS = (pow(G, yi, PRIME) * pow(H, ri, PRIME)) % PRIME
        RHS = 1
        for j,Cj in enumerate(Cglob):
            exp = pow(xi, j, PRIME)
            RHS = (RHS * pow(Cj, exp, PRIME)) % PRIME
        ok = (LHS == RHS)
        print(f"Share {c['id']:02d}: LHS==RHS? {ok}")
        if not ok:
            print(f"  LHS: {LHS}")
            print(f"  RHS: {RHS}")
            # adicional: mostrar per-j products
            partial = 1
            print("  partial products by j:")
            for j,Cj in enumerate(Cglob):
                term = pow(Cj, pow(xi, j, PRIME), PRIME)
                partial = (partial * term) % PRIME
                print(f"    j={j}: term={term}, partial={partial}")
            # e mostrar H_used per commit vs H global
            print(f"  H_used in commit: {c['H']}")
            print(f"  H global module: {H}")
    print("\nDEBUG done.\n")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python3 verificar_dealer_debug.py <k>")
        print("Ex: python3 verificar_dealer_debug.py 3")
        sys.exit(1)

    k = int(sys.argv[1])
    commits = carregar_commitments_individuais()

    # 1) verificação individual
    ok_ind = verificar_individuais(commits)
    print("\nResultado verificação individual:", ok_ind)

    # 2) debug com k
    debug_verificacao(commits, k)
