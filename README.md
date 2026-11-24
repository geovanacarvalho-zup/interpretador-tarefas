# 🧠 Interpretador Inteligente de Tarefas (StackSpot AI)

Aplicação de terminal (CLI) em Python que transforma frases em linguagem natural em tarefas estruturadas usando a **StackSpot AI**, valida os dados com **Pydantic** e salva localmente em **JSON** e **SQLite**.

---

## 🚀 Como Configurar e Rodar

### 1. Criar o ambiente virtual e instalar as dependências
No terminal, dentro da pasta do projeto, execute:

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt



### 2. Pegar suas credenciais na StackSpot AI

1. Acesse o portal da **StackSpot AI** e faça login na sua conta.
2. **Credenciais da Conta:** No menu do seu perfil (ou na aba **Integração de API** de qualquer agente), gere uma **Credencial de Serviço** e copie seu `Client ID` e `Client Key`.
3. **Agente (`Agent Slug`):** Utilize o slug de um agente já existente na sua conta (desde que não possua instruções conflitantes) ou crie um agente novo sem *Knowledge Sources* restritivos e copie o ID dele na aba **Integração de API**.