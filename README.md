# 🚀 PyQuotex

---
<p align="center">
  <a href="https://github.com/cleitonleonel/pyquotex">
    <img src="pyquotex.png" alt="pyquotex" width="45%" height="auto">
  </a>
</p>
<p align="center">
  <i>Unofficial Quotex Library API Client written in Python!</i>
</p>
<p align="center">
  <img src="https://img.shields.io/badge/python-3.12%20%7C%203.13-green" alt="Python Versions"/>
</p>

---

## 📘 Sobre o projeto (PT-BR)

O **PyQuotex** nasceu como uma biblioteca open-source para facilitar a comunicação com a plataforma Quotex via WebSockets. Com o tempo e devido ao uso indevido, uma versão privada mais segura e robusta foi criada.

---

## 📘 About the Project (EN)

**PyQuotex** started as an open-source library to make it easier to communicate with the Quotex platform using WebSockets. Due to misuse, a more robust private version was later introduced.

---

## 🎯 Objetivo da Biblioteca / Library Goal

Prover ferramentas para desenvolvedores integrarem seus sistemas com a plataforma Quotex, permitindo operações automatizadas de forma segura e eficiente.

> ⚠️ Esta biblioteca **não é um robô de operações** e não toma decisões por conta própria.

---

# 📚 Documentação Completa
https://cleitonleonel.github.io/pyquotex/


## 🛠 Instalação

### 1. Clone o repositório:

```bash
git clone https://github.com/cleitonleonel/pyquotex.git
cd pyquotex
poetry install
poetry run python app.py
```

### 2. Ou instale diretamente no seu projeto com Poetry:

```bash
poetry add git+https://github.com/cleitonleonel/pyquotex.git
```

### 2.1. Instale com um comando no Termux (Android):

```shell
curl -sSL https://raw.githubusercontent.com/cleitonleonel/pyquotex/refs/heads/master/run_in_termux.sh | sh
```

### 3. Requisitos adicionais
Se você encontrar um erro relacionado ao `playwright install` ao usar esta biblioteca, siga os passos abaixo para resolver o problema.

### Instalar navegadores do Playwright
Certifique-se de que o Playwright e os navegadores compatíveis estejam instalados.

![playwright_info.png](playwright_info.png)

```bash
playwright install
```
---

## 🧪 Exemplo de uso

```python
from pyquotex.stable_api import Quotex

client = Quotex(
  email="your_email",
  password="your_password",
  lang="pt"  # ou "en"
)

await client.connect()
print(await client.get_balance())
await client.close()
```

## 🔀 Multi sessão no mesmo processo (2 instrumentos)

Agora o estado de conexão/WebSocket é isolado por instância de cliente. Isso permite executar duas sessões no mesmo processo sem compartilhar flags de conexão.

```python
import asyncio
import time
from pyquotex.stable_api import Quotex


async def watch_symbol(email, password, symbol, period=60):
  client = Quotex(email=email, password=password, lang="en")
  ok, reason = await client.connect()
  if not ok:
    print(symbol, "connect error:", reason)
    return

  asset_name, asset_data = await client.get_available_asset(symbol, force_open=True)
  if not asset_data or not asset_data[2]:
    print(symbol, "asset unavailable")
    await client.close()
    return

  candles = await client.get_candles(asset_name, time.time(), 3600, period)
  print(symbol, "candles:", len(candles))
  await client.close()


async def main():
  await asyncio.gather(
    watch_symbol("user_1@email.com", "pass_1", "AUDJPY_otc"),
    watch_symbol("user_2@email.com", "pass_2", "EURUSD_otc"),
  )


asyncio.run(main())
```

Boas práticas:
- Uma instância de `Quotex` por sessão.
- Não reutilizar o mesmo objeto para múltiplos logins concorrentes.
- Fechar cada sessão com `await client.close()`.

---

## 💡 Recursos Principais

| Função                     | Descrição                              |
| -------------------------- | -------------------------------------- |
| `connect()`                | Conecta via WebSocket com reconexão    |
| `get_balance()`            | Retorna o saldo da conta               |
| `buy_simple()`             | Realiza uma operação de compra simples |
| `buy_and_check_win()`      | Compra e verifica o resultado          |
| `get_candle()`             | Retorna candles históricos             |
| `get_realtime_sentiment()` | Sentimento em tempo real do ativo      |
| `balance_refill()`         | Recarrega a conta demo                 |

---

## 🔒 Versão Privada Disponível

Uma versão privada está disponível com recursos adicionais, estabilidade aprimorada e melhor suporte.

👉 [Acesse a versão privada](https://t.me/pyquotex/852) para desbloquear o máximo do PyQuotex!

### 💥 Comparativo de Versões

| Recurso                        | Open Source ✅ | Versão Privada ✨      |
|--------------------------------| ------------- | --------------------- |
| Suporte a Multilogin           | ❌             | ✅                     |
| Monitoramento de Sentimentos   | ✅             | ✅ + detecção avançada |
| Proxy/DNS Customizado          | ❌             | ✅                     |
| Robustez e Alta Confiabilidade | ✅             | ✨ Nível enterprise    |
| Velocidade de Execução         | ✅             | ⚡ Ultra rápido        |
| Suporte                        | ❌             | ✅                     |

---

## 🤝 Apoie este projeto

[![Buy Me a Coffee](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/cleiton.leonel)

### 💸 Criptomoedas

* **Dogecoin (DOGE)**: `DMwSPQMk61hq49ChmTMkgyvUGZbVbWZekJ`
* **Bitcoin (BTC)**: `bc1qtea29xkpyx9jxtp2kc74m83rwh93vjp7nhpgkm`
* **Ethereum (ETH)**: `0x20d1AD19277CaFddeE4B8f276ae9f3E761523223`
* **Solana (SOL)**: `4wbE2FVU9x4gVErVSsWwhcdXQnDBrBVQFvbMqaaykcqo`

---

## 📞 Contato

* Telegram: [@cleitonleonel](https://t.me/cleitonleonel)
* GitHub: [cleitonleonel](https://github.com/cleitonleonel)
* LinkedIn: [Cleiton Leonel](https://www.linkedin.com/in/cleiton-leonel-creton-331138167/)

---
