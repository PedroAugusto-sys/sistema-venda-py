# Sistema de Vendas (Local)

Sistema de vendas local em Python com interface PySide6. Permite cadastrar produtos, clientes e registrar vendas.

## Requisitos

- Python 3.10+
- Windows, macOS ou Linux

## Instalação

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

## Executar

```bash
python main.py
```

## Dados

Os dados são gravados em `data/products.json` e `data/clients.json`.  
Se não existirem, o sistema cria automaticamente quando necessário.
