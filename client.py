import os
import json
from datetime import date
import requests
from dotenv import load_dotenv
from models import InterpretacaoResultado

load_dotenv()

CLIENT_ID = os.getenv("STACKSPOT_CLIENT_ID")
CLIENT_KEY = os.getenv("STACKSPOT_CLIENT_KEY")
REALM = os.getenv("STACKSPOT_REALM", "zup")
AGENT_SLUG = os.getenv("STACKSPOT_AGENT_SLUG")

AUTH_URL = f"https://idm.stackspot.com/{REALM}/oidc/oauth/token"
API_URL = f"https://genai-inference-app.stackspot.com/v1/agent/{AGENT_SLUG}/chat"


def obter_token_acesso() -> str:
    if not CLIENT_ID or not CLIENT_KEY or not AGENT_SLUG:
        raise ValueError("Credenciais ausentes no arquivo .env (STACKSPOT_CLIENT_ID, STACKSPOT_CLIENT_KEY ou STACKSPOT_AGENT_SLUG).")

    payload = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_KEY
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "InterpretadorTarefasFutureMinds/1.0"
    }

    resposta = requests.post(AUTH_URL, data=payload, headers=headers, timeout=15)
    if not resposta.ok:
        raise Exception(f"Falha na autenticação OAuth2: {resposta.status_code} - {resposta.text}")

    return resposta.json()["access_token"]


def _extrair_json_limpo(texto_bruto: str) -> str:
    texto = texto_bruto.strip()
    if texto.startswith("```json"):
        texto = texto[7:]
    elif texto.startswith("```"):
        texto = texto[3:]
    if texto.endswith("```"):
        texto = texto[:-3]
    return texto.strip()


def interpretar_solicitacao(texto_usuario: str) -> InterpretacaoResultado:
    token = obter_token_acesso()
    data_hoje = date.today().isoformat()

    prompt = f"""
Você é um assistente especializado em extrair tarefas estruturadas de textos em linguagem natural.
Data de referência atual (hoje): {data_hoje}.

Analise a solicitação do usuário abaixo e responda EXCLUSIVAMENTE com um objeto JSON válido, sem nenhum texto explicativo antes ou depois, e sem blocos markdown.

Regras obrigatórias:
1. Se a solicitação for vaga, sem ação clara ou insuficiente para criar uma tarefa (ex: "oi", "preciso resolver umas coisas", "me ajuda"), defina "informacao_suficiente": false, explique o motivo em "motivo_insuficiencia" e deixe "tarefas": [].
2. Se houver uma ou mais ações claras, extraia TODAS elas dentro da lista "tarefas" e defina "informacao_suficiente": true.
3. O campo "prioridade" deve ser EXATAMENTE um destes valores: "Baixa", "Média" ou "Alta".
4. O campo "prazo" deve ser uma data calculada a partir de hoje ({data_hoje}) no formato "YYYY-MM-DD", ou null se não houver prazo mencionado.
5. O campo "duracao_estimada_horas" deve ser um número decimal (float) positivo, ou null se não mencionado.
6. O campo "status" deve ser sempre "Pendente".

Formato JSON obrigatório:
{{
  "informacao_suficiente": true,
  "motivo_insuficiencia": null,
  "tarefas": [
    {{
      "titulo": "string",
      "categoria": "string",
      "prioridade": "Baixa" | "Média" | "Alta",
      "prazo": "YYYY-MM-DD" ou null,
      "duracao_estimada_horas": float ou null,
      "status": "Pendente"
    }}
  ]
}}

Solicitação do usuário:
"{texto_usuario}"
"""

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": "InterpretadorTarefasFutureMinds/1.0"
    }
    payload = {
        "streaming": False,
        "user_prompt": prompt,
        "stackspot_knowledge": False,
        "return_ks_in_response": False,
        "deep_search_ks": False
    }

    resposta = requests.post(API_URL, json=payload, headers=headers, timeout=30)
    if not resposta.ok:
        raise Exception(f"Erro HTTP {resposta.status_code} ({resposta.reason}): {resposta.text}")

    dados_api = resposta.json()
    if isinstance(dados_api, dict):
        conteudo_ia = dados_api.get("message", dados_api.get("result", dados_api.get("answer", str(dados_api))))
    else:
        conteudo_ia = str(dados_api)

    json_limpo = _extrair_json_limpo(conteudo_ia)
    dados_estruturados = json.loads(json_limpo)

    return InterpretacaoResultado.model_validate(dados_estruturados)