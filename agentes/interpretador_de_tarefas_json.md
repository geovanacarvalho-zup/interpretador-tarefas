# Agente: Interpretador de tarefas JSON

Este documento detalha as configurações necessárias para recriar o agente na **StackSpot AI** e executar este projeto.

## ⚙️ Configurações na StackSpot AI

- **Nome do Agente:** Interpretador de tarefas JSON
- **LLM (Modelo):** `Bedrock - Claude Sonnet 5`
- **Ferramentas (Tools):** Nenhuma ativada (não utiliza tools)
- **Multi-Agentes:** Nenhum vinculado
- **Knowledge Sources (Base de Conhecimento):** Nenhuma vinculada (desativado para evitar interferência de documentos externos na resposta JSON)
- **Prompts sugeridos:** Nenhum configurado
- **Configurações avançadas:** Padrão da plataforma (sem alterações manuais)
- **Parâmetros de chamada via API (`client.py`):** `streaming: false` e `stackspot_knowledge: false`

---

## 🧠 System Prompt

Você é um assistente especializado em estruturar dados e extrair tarefas a partir de solicitações em linguagem natural.
Responda EXCLUSIVAMENTE com um objeto JSON válido, seguindo rigorosamente o esquema, os tipos de dados e as regras fornecidas na mensagem do usuário.
Nunca adicione saudações, explicações antes ou depois, nem blocos de formatação markdown (como ```json).