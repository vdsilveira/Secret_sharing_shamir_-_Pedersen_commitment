import os
import secrets
import json

PRIME = 2**521 - 1   # primo grande
G = 2                # gerador g

COMMITMENTS_DIR = "commitments"
SHARES_DIR = "shares"


# ----------------------------------------
# Gerar H toda vez (sem persistência em disco)
# ----------------------------------------

def generate_H():
    t = secrets.randbelow(PRIME - 2) + 1
    return pow(G, t, PRIME)


# H gerado apenas em memória (mesmo valor durante toda execução do script)
H = generate_H()


# ----------------------------------------
# Funções básicas
# ----------------------------------------

def pedersen_commit(value: int, r: int, g: int = G, h: int = H, p: int = PRIME) -> int:
    return (pow(g, value, p) * pow(h, r, p)) % p


def parse_share_file(path: str):
    with open(path, "r") as f:
        content = f.read().strip()

    if "x=" in content and "y=" in content:
        data = {}
        for line in content.splitlines():
            if "=" in line:
                k, v = line.split("=", 1)
                data[k.strip()] = int(v.strip())
        return data["x"], data["y"]

    txt = content.replace("(", "").replace(")", "").replace(",", " ")

    # Tenta vários separadores
    for sep in [",", ":", " "]:
        if sep in txt:
            parts = txt.split(sep, 1)
            if len(parts) == 2:
                return int(parts[0].strip()), int(parts[1].strip())

    raise ValueError(f"Formato inválido no share: {path}")


# ----------------------------------------
# 1) Criar commitment para um share
# ----------------------------------------

def gerar_commitment_share(numero_share: int):
    share_file = os.path.join(SHARES_DIR, f"share_{numero_share:02d}.txt")
    if not os.path.exists(share_file):
        raise FileNotFoundError(f"Share não encontrado: {share_file}")

    x, y = parse_share_file(share_file)
    r = secrets.randbelow(PRIME - 1)
    C = pedersen_commit(y, r)

    os.makedirs(COMMITMENTS_DIR, exist_ok=True)

    out = {
        "share": numero_share,
        "x": x,
        "y": y,                   # ainda salvamos para debug/transparência
        "commitment": C,
        "r": r,
        "H_used": H
    }

    commit_file = os.path.join(COMMITMENTS_DIR, f"commitment_{numero_share:02d}.txt")
    with open(commit_file, "w") as f:
        json.dump(out, f, indent=2)

    print(f"Commitment gerado: {commit_file}")
    return C, r


# ----------------------------------------
# 2) Verificar commitment (CORRIGIDO!)
# ----------------------------------------

def verificar_commitment(numero_share: int):
    commit_file = os.path.join(COMMITMENTS_DIR, f"commitment_{numero_share:02d}.txt")
    share_file = os.path.join(SHARES_DIR, f"share_{numero_share:02d}.txt")

    if not os.path.exists(commit_file):
        raise FileNotFoundError(f"Commitment não encontrado: {commit_file}")
    if not os.path.exists(share_file):
        raise FileNotFoundError(f"Share não encontrado: {share_file}")

    # 1) Lê o commitment (C, r, H_used)
    data = json.load(open(commit_file))
    C = data["commitment"]
    r = data["r"]
    H_used = data["H_used"]

    # 2) Lê o y ATUAL do arquivo share (o que pode ter sido alterado!)
    _, y_atual = parse_share_file(share_file)

    # 3) Verifica: g^y_atual * h^r == C ?
    C_check = (pow(G, y_atual, PRIME) * pow(H_used, r, PRIME)) % PRIME

    if C_check == C:
        print(f"[OK] Commitment válido para share {numero_share:02d} → share está íntegro")
        return True
    else:
        print(f"[ERRO] Commitment INVÁLIDO para share {numero_share:02d}")
        print(f"    → O share foi ALTERADO ou corrompido!")
        return False


# ----------------------------------------
# CLI
# ----------------------------------------

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("\nUso:")
        print("  python3 pedersen_commit.py gerar <número>")
        print("  python3 pedersen_commit.py verificar <número>\n")
        sys.exit(1)

    comando = sys.argv[1].lower()
    try:
        share_num = int(sys.argv[2])
    except ValueError:
        print("Erro: número da share deve ser inteiro")
        sys.exit(1)

    if comando == "gerar":
        gerar_commitment_share(share_num)
    elif comando in ("verificar", "verifica", "check"):
        verificar_commitment(share_num)
    else:
        print("Comando desconhecido. Use: gerar | verificar")