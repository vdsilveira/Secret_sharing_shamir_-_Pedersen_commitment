
# 🔐 Shamir Secret Sharing + Pedersen Commitments (3-de-5)

Projeto didático completo que combina:

- **Shamir's Secret Sharing** (threshold 3 de 5) em Python puro  
- **Pedersen Commitments** para cada share  
- **Verificação individual** da integridade de cada share  
- **Verificação global** da honestidade do dealer

Perfeito para estudos de criptografia threshold, MPC, carteiras multisig ou provas de conceito.

---

## Estrutura do Projeto

```
.
├── mensagem.txt              ← Seu segredo em texto plano
├── shamir.py                 ← Shamir Secret Sharing
├── pedersen_commit.py        ← Pedersen Commitments
├── verificar_dealer.py       ← Verificação global da honestidade do dealer
├── shares/                   ← 5 shares geradas (x, y, r)
├── commitments/              ← Commitments + parâmetros públicos
└── H.json                    ← Parâmetros públicos do Pedersen (gerado automaticamente)
```

---

### 1) 🔐 Gerar as 5 Shares (Threshold 3-de-5)

Coloque seu segredo no arquivo:

```txt
mensagem.txt
```

Em seguida execute:

```bash
python3 shamir.py gerar
```

**Resultado:**

```
shares/
├── share_01.txt   → formato: x,y,r
├── share_02.txt
├── share_03.txt
├── share_04.txt
└── share_05.txt
```

Cada share contém três valores separados por vírgula:

```
x, y, r
```

- `x` → índice da share (1 a 5)  
- `y` → valor do polinômio f(x) nesse ponto (o "segredo parcial")  
- `r` → blinding factor aleatório (usado no Pedersen Commitment)

> Qualquer 3 dessas 5 shares recuperam o segredo original.

---

### 2) 🔓 Recuperar o Segredo

Use qualquer combinação de 3 shares (exemplo: 1, 3 e 5):

```bash
python3 shamir.py recover 1 3 5
```

Saída:

```
======= SEGREDO RECONSTRUÍDO =======
Seu segredo original aqui!
====================================
```

Funciona com qualquer trio válido!

---

### 3) 📌 Gerar Todos os Pedersen Commitments de Uma Vez

```bash
python3 pedersen_commit.py gerar_todos
```

**Arquivos criados:**

```
commitments/
├── commitment_01.txt
├── commitment_02.txt
├── commitment_03.txt
├── commitment_04.txt
├── commitment_05.txt
└── H.json                 ← Parâmetros públicos (g, h, p) fixos
```

Cada `commitment_XX.txt` é um JSON contendo:

```json
{
  "share": 3,
  "x": 3,
  "y": 94738392010293847,
  "r": 55667788991011234,
  "commitment": "0xAbCdE...fG2",
  "H_used": { "g": "...", "h": "...", "p": "..." }
}
```

O commitment é calculado como:

**C = g^y · h^r mod p** → perfeitamente oculto e vinculante

---

### 4) 🛡 Verificar a Integridade de Uma Share Específica

```bash
python3 pedersen_commit.py verificar 4
```

**Saídas possíveis:**

```
[OK] Share 04 íntegra – commitment válido ✓
```

ou, se a share ou commitment foi alterado:

```
[ERRO] Commitment inválido para share 04!
```

---

### 5) 🧮 Verificar a Honestidade do Dealer (Verificação Global)

Depois de gerar todos os commitments, rode:

```bash
python3 verificar_dealer.py
```

**Exemplo de saída com dealer honesto:**

```
[OK] Share 01 íntegra
[OK] Share 02 íntegra
[OK] Share 03 íntegra
[OK] Share 04 íntegra
[OK] Share 05 íntegra

✓ Todas as shares são individualmente válidas.
ℹ Usando threshold k=3 para reconstrução.

✓ Todas as 5 shares estão sobre o mesmo polinômio de grau < 3
✔ Dealer foi HONESTO – consistência global confirmada!
```

**Se o dealer foi malicioso ou alguma share foi corrompida:**

```
[ERRO] Share 03 NÃO está sobre o polinômio reconstruído!
→ Dealer malicioso OU share corrompida/tamperada
```

---

## Pronto!

Você agora tem um sistema completo de **threshold cryptography verificável** com:

- Segredo dividido em 5 shares (3 necessárias)
- Commitments criptográficos em cada share
- Verificação individual e global
- Detecção automática de dealer malicioso

Ideal para:

- Estudos acadêmicos
- Provas de conceito de MPC
- Implementações de carteiras multisig verificáveis
- Experimentos com Verifiable Secret Sharing (VSS)

Divirta-se e compartilhe conhecimento! 🚀
