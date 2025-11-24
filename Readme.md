# Projeto: Shamir Secret Sharing + Pedersen Commitments

Este projeto implementa de forma didática e funcional:

- **Compartilhamento de Segredos de Shamir** (threshold 3-de-5) em Python puro  
- **Commitments de Pedersen** para cada share  
- **Verificação criptográfica** da integridade de cada share individual

## Estrutura do Projeto

```
.
├── mensagem.txt          ← Segredo original (texto plano)
├── shamir.py             ← Implementação do Shamir Secret Sharing
├── pedersen_commit.py    ← Implementação dos Pedersen Commitments
├── shares/               ← Shares gerados
└── commitments/          ← Commitments de cada share
```

---

### 1) Gerar o segredo e os 5 shares (Shamir 3-de-5)

Coloque o segredo desejado no arquivo `mensagem.txt`.

```bash
python3 shamir.py gerar
```

Isso cria 5 shares (qualquer 3 deles recuperam o segredo):

```
shares/
├── share_01.txt
├── share_02.txt
├── share_03.txt
├── share_04.txt
└── share_05.txt
```

Cada arquivo contém: `x,y` (ponto da curva polinomial).

---

### 2) Recuperar o segredo usando 3 shares

Exemplo com os shares 1, 2 e 4:

```bash
python3 shamir.py recover 1 2 4
```

Saída esperada:

```
======= SEGREDO RECONSTRUÍDO =======
<conteúdo original de mensagem.txt>
====================================
```

Você pode usar qualquer combinação de 3 shares diferentes.

---

### 3) Gerar um Pedersen Commitment para uma share

Exemplo: gerar commitment para a share 2

```bash
python3 pedersen_commit.py gerar 2
```

Isso cria o arquivo:

```
commitments/commitment_02.txt
```

Conteúdo do commitment:

```
x: 2
y: 7384938392...         ← valor do share (segredo parcial)
C: (h1, h2)              ← commitment = g^y * h^r mod p
r: 1094832049...         ← valor aleatório (blinder)
H: (h1, h2)              ← parâmetros públicos do commitment
```

---

### 4) Verificar a integridade de uma share via commitment

```bash
python3 pedersen_commit.py verificar 2
```

Se tudo estiver correto:

```
[OK] Commitment válido para share 02
```

Se o share ou o commitment tiver sido alterado:

```
[ERRO] Commitment inválido!
```

---

### Estrutura final esperada após gerar tudo

```
.
├── mensagem.txt
├── shamir.py
├── pedersen_commit.py
├── shares/
│   ├── share_01.txt
│   ├── share_02.txt
│   ├── share_03.txt
│   ├── share_04.txt
│   └── share_05.txt
└── commitments/
    ├── commitment_01.txt
    ├── commitment_02.txt
    ├── commitment_03.txt
    ├── commitment_04.txt
    └── commitment_05.txt
```

Pronto! Agora você tem um sistema completo de **threshold cryptography** com **verificação criptográfica individual** de cada share usando Pedersen Commitments.

Ideal para estudos, provas de conceito ou integração em projetos de MPC, carteiras multisig, etc.