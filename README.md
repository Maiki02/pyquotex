# 🚀 PyQuotex

---
<p align="center">
  <a href="https://github.com/cleitonleonel/pyquotex">
    <img src="pyquotex.png" alt="pyquotex" width="350" height="auto" title="PyQuotex"/>
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

## 📝 Recent Changes / Cambios Recientes / Mudanças Recentes (April 2026)

### 🇺🇸 English
- `connect()` now includes an auth fallback: if WebSocket rejects the session token, pyquotex clears in-memory session data, runs `authenticate()` with credentials, and retries WebSocket connection.
- `get_candles()` now triggers a minimal subscription (`subscribe_realtime_candle`) to force historical payload delivery when required by the broker.
- In snapshot mode (`progressive=False`), subscription teardown is guaranteed in `finally` via `unsubscribe_realtime_candle`, avoiding bandwidth leaks.
- Connection and data routing remain isolated per client/asset for safer concurrent usage.

### 🇪🇸 Español
- `connect()` incluye fallback de autenticación: si WebSocket rechaza el token de sesión, pyquotex limpia la sesión en memoria, ejecuta `authenticate()` y reintenta la conexión.
- `get_candles()` dispara una suscripción mínima (`subscribe_realtime_candle`) para forzar entrega de histórico cuando el broker lo exige.
- En modo snapshot (`progressive=False`), el cierre de suscripción queda garantizado en `finally` con `unsubscribe_realtime_candle`, evitando fuga de red.
- El estado y ruteo de datos se mantienen aislados por cliente/activo para uso concurrente seguro.

### 🇧🇷 Português
- `connect()` possui fallback de autenticação: se o WebSocket rejeitar o token de sessão, o pyquotex limpa a sessão em memória, executa `authenticate()` e tenta conectar novamente.
- `get_candles()` dispara assinatura mínima (`subscribe_realtime_candle`) para forçar entrega do histórico quando o broker exige.
- No modo snapshot (`progressive=False`), o encerramento da assinatura é garantido em `finally` com `unsubscribe_realtime_candle`, evitando vazamento de rede.
- Estado e roteamento de dados permanecem isolados por cliente/ativo para concorrência segura.

---

## 💡 Recursos Principais

| Função                     | Descrição                              |
| -------------------------- | -------------------------------------- |
| `connect()`                | Conecta via WebSocket com reconexão    |
| `get_balance()`            | Retorna o saldo da conta               |
| `buy()`                    | Realiza uma operação de compra         |
| `check_win()`              | Verifica o resultado de uma operação   |
| `get_candles()`            | Retorna candles históricos             |
| `get_realtime_sentiment()` | Sentimento em tempo real do ativo      |
| `edit_practice_balance()`  | Recarrega a conta demo                 |

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

* Telegram: [cleitonlc](https://t.me/cleitonlc)
* GitHub: [cleitonleonel](https://github.com/cleitonleonel)
* LinkedIn: [Cleiton Leonel](https://www.linkedin.com/in/cleiton-leonel-creton-331138167/)

---
