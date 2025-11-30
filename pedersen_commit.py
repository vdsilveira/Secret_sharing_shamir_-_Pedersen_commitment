import os
import secrets
import json

PRIME = 2**521 - 1   # primo grande
G = 2                # gerador g

COMMITMENTS_DIR = "commitments"
SHARES_DIR = "shares"


# ------------------------------------------------------------
#  H PERSISTENTE (para todo o sistema)
# ------------------------------------------------------------

def generate_H():
    t = secrets.randbelow(PRIME - 2) + 1
    return pow(G, t, PRIME)

def load_or_create_H():
    """Garantir um único H para todos os commitments."""
    os.makedirs(COMMITMENTS_DIR, exist_ok=True)
    path = os.path.join(COMMITMENTS_DIR, "H.json")

    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                data = json.load(f)
                return int(data["H"])
        except Exception:
            pass

    # criar H novo
    H_new = generate_H()
    with open(path, "w") as f:
        json.dump({"H": H_new}, f)
    return H_new

# H global persistente
H = load_or_create_H()


# ------------------------------------------------------------
# Funções básicas
# ------------------------------------------------------------

def pedersen_commit(value: int, r: int, g: int = G, h: int = H, p: int = PRIME) -> int:
    return (pow(g, value, p) * pow(h, r, p)) % p


def parse_share_file(path: str):
    """
    Suporta shares no formato:
       x,y,r
    ou:
       x,y
    """
    with open(path, "r") as f:
        line = f.read().strip()

    parts = [p.strip() for p in line.split(",")]

    if len(parts) == 2:
        x = int(parts[0])
        y = int(parts[1])
        return x, y, None

    if len(parts) == 3:
        x = int(parts[0])
        y = int(parts[1])
        r = int(parts[2])
        return x, y, r

    raise ValueError(f"Formato inválido para share: {path}")


# ------------------------------------------------------------
# 1) Criar commitment para um share (mantido)
# ------------------------------------------------------------

def gerar_commitment_share(numero_share: int):
    share_file = os.path.join(SHARES_DIR, f"share_{numero_share:02d}.txt")
    if not os.path.exists(share_file):
        raise FileNotFoundError(f"Share não encontrado: {share_file}")

    x, y, r = parse_share_file(share_file)

    if r is None:
        raise ValueError(
            f"Share {numero_share} não possui r! Regere as shares com o novo shamir.py."
        )

    C = pedersen_commit(y, r)

    os.makedirs(COMMITMENTS_DIR, exist_ok=True)

    out = {
        "share": numero_share,
        "x": x,
        "y": y,
        "r": r,
        "commitment": C,
        "H_used": H
    }

    commit_file = os.path.join(COMMITMENTS_DIR, f"commitment_{numero_share:02d}.txt")
    with open(commit_file, "w") as f:
        json.dump(out, f, indent=2)

    print(f"[OK] Commitment gerado: {commit_file}")
    return C, r


# ------------------------------------------------------------
# NOVO: Gerar todos os commitments de uma vez
# ------------------------------------------------------------

def gerar_todos_commitments():
    print("\n🔧 Gerando TODOS os commitments usando o mesmo H persistente...\n")

    if not os.path.exists(SHARES_DIR):
        print("ERRO: pasta shares/ não encontrada.")
        return

    files = sorted(f for f in os.listdir(SHARES_DIR) if f.startswith("share_"))

    if not files:
        print("ERRO: nenhuma share encontrada em shares/")
        return

    for fname in files:
        num = int(fname.replace("share_", "").replace(".txt", ""))
        gerar_commitment_share(num)

    print("\n✔ Todos os commitments foram gerados corretamente!\n")


# ------------------------------------------------------------
# 2) Verificar commitment individual
# ------------------------------------------------------------

def verificar_commitment(numero_share: int):
    commit_file = os.path.join(COMMITMENTS_DIR, f"commitment_{numero_share:02d}.txt")
    share_file = os.path.join(SHARES_DIR, f"share_{numero_share:02d}.txt")

    if not os.path.exists(commit_file):
        raise FileNotFoundError(f"Commitment não encontrado: {commit_file}")
    if not os.path.exists(share_file):
        raise FileNotFoundError(f"Share não encontrada: {share_file}")

    data = json.load(open(commit_file))

    C = data["commitment"]
    r_c = data["r"]
    H_used = data["H_used"]

    x, y_atual, r_atual = parse_share_file(share_file)

    if r_atual is None:
        raise ValueError("Share não possui r!")

    if r_atual != r_c:
        print(f"[ERRO] r do share mudou! Alteração detectada.")
        return False

    C_check = (pow(G, y_atual, PRIME) * pow(H_used, r_c, PRIME)) % PRIME

    if C_check == C:
        print(f"[OK] Commitment válido para share {numero_share:02d}")
        return True
    else:
        print(f"[ERRO] Commitment inválido para share {numero_share:02d}")
        return False


# ------------------------------------------------------------
# CLI
# ------------------------------------------------------------

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("\nUso:")
        print("  python3 pedersen_commit.py gerar <n>")
        print("  python3 pedersen_commit.py verificar <n>")
        print("  python3 pedersen_commit.py gerar_todos\n")
        sys.exit(1)

    comando = sys.argv[1].lower()

    if comando == "gerar_todos":
        gerar_todos_commitments()

    elif comando == "gerar":
        if len(sys.argv) != 3:
            print("Uso: python3 pedersen_commit.py gerar <n>")
            sys.exit(1)
        gerar_commitment_share(int(sys.argv[2]))

    elif comando in ("verificar", "check"):
        if len(sys.argv) != 3:
            print("Uso: python3 pedersen_commit.py verificar <n>")
            sys.exit(1)
        verificar_commitment(int(sys.argv[2]))

    else:
        print("Comando desconhecido. Use: gerar | verificar | gerar_todos")
