import os
import random
from typing import List, Tuple

# Primo grande para o campo finito (2^127 - 1, Mersenne)
PRIME = 2**521 - 1  # primo de Mersenne enorme


# ===========================
#   FUNÇÕES DO SHAMIR
# ===========================

def eval_poly(coeffs: List[int], x: int, p: int) -> int:
    """Avalia polinômio (c0 + c1*x + c2*x^2 + ...)."""
    result = 0
    power = 1
    for c in coeffs:
        result = (result + c * power) % p
        power = (power * x) % p
    return result


def make_shares(secret: int, n: int, k: int, p: int = PRIME) -> List[Tuple[int, int]]:
    """Gera n shares com threshold k."""
    assert 1 <= k <= n
    assert secret < p

    coeffs = [secret] + [random.randrange(0, p) for _ in range(k - 1)]
    shares = []

    for i in range(1, n + 1):
        x = i
        y = eval_poly(coeffs, x, p)
        shares.append((x, y))

    return shares


def lagrange_interpolation(x: int, xs: List[int], ys: List[int], p: int) -> int:
    """Interpolação de Lagrange."""
    total = 0
    k = len(xs)

    for i in range(k):
        xi, yi = xs[i], ys[i]
        num = 1
        den = 1

        for j in range(k):
            if i == j:
                continue
            xj = xs[j]
            num = (num * (x - xj)) % p
            den = (den * (xi - xj)) % p

        inv_den = pow(den, p - 2, p)  # inverso modular (p é primo)
        term = yi * num * inv_den
        total = (total + term) % p

    return total


def recover(shares: List[Tuple[int, int]], p: int = PRIME) -> int:
    xs, ys = zip(*shares)
    return lagrange_interpolation(0, list(xs), list(ys), p)


# =========================================================
#                      GERAR SHARES
# =========================================================

def generate_shares():
    # 1 - Ler o segredo do arquivo
    if not os.path.exists("mensagem.txt"):
        print("ERRO: mensagem.txt não encontrado!")
        return

    with open("mensagem.txt", "rb") as f:
        raw = f.read()

    secret_int = int.from_bytes(raw, "big")

    # 2 - Gerar shares 3 de 5
    shares = make_shares(secret_int, n=5, k=3)

    # 3 - Salvar na pasta shares/
    os.makedirs("shares", exist_ok=True)

    for idx, (x, y) in enumerate(shares, start=1):
        filename = f"shares/share_{idx:02d}.txt"
        with open(filename, "w") as f:
            f.write(f"{x},{y}\n")

    print("✔ Shares gerados e salvos na pasta 'shares/'")

# =========================================================
#                      RECUPERAR SEGREDO
# =========================================================

def recover_secret(indices: List[int]):
    shares_to_use = []

    for idx in indices:
        filename = f"shares/share_{idx:02d}.txt"
        if not os.path.exists(filename):
            print(f"ERRO: share {idx} não encontrado!")
            return

        with open(filename, "r") as f:
            line = f.read().strip()
            x, y = map(int, line.split(","))
            shares_to_use.append((x, y))

    secret_int = recover(shares_to_use)
    secret_bytes = secret_int.to_bytes((secret_int.bit_length() + 7) // 8, "big")

    print("\n======= SEGREDO RECONSTRUÍDO =======")
    try:
        print(secret_bytes.decode())
    except:
        print(secret_bytes)
    print("====================================\n")


# =========================================================
#                      MODO DE USO
# =========================================================

if __name__ == "__main__":
    import sys

    if len(sys.argv) == 2 and sys.argv[1] == "gerar":
        generate_shares()

    elif len(sys.argv) == 5 and sys.argv[1] == "recover":
        # Exemplo: python3 shamir.py recover 1 4 5
        indices = list(map(int, sys.argv[2:5]))
        recover_secret(indices)

    else:
        print("\nUso:")
        print("  python3 shamir.py gerar")
        print("  python3 shamir.py recover <i> <j> <k>")
        print("\nExemplo:")
        print("  python3 shamir.py recover <i> <j> <k>\n")
