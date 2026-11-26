# 🧠 Interpretador Inteligente de Tarefas (StackSpot AI)

Aplicação de terminal (CLI) em Python que transforma frases em linguagem natural em tarefas estruturadas usando a **StackSpot AI**, valida os dados com **Pydantic** e salva localmente em **JSON** e **SQLite**.

---

## 🚀 1. Criar o ambiente virtual e instalar as dependências

No terminal, dentro da pasta do projeto, execute:

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

## 🔑 2. Pegar suas credenciais na StackSpot AI

1. Acesse o portal da **StackSpot AI** e faça login na sua conta.
2. **Credenciais da Conta:** No menu do seu perfil (ou na aba **Integração de API** de qualquer agente), gere uma **Credencial de Serviço** e copie seu `Client ID` e `Client Key`.
3. **Agente (`Agent Slug`):** Utilize o slug de um agente já existente na sua conta (desde que não possua instruções conflitantes) ou crie um agente novo sem *Knowledge Sources* restritivos e copie o ID dele na aba **Integração de API**.

---

## ⚙️ 3. Configurar o seu arquivo `.env`

Na raiz do projeto, crie um arquivo chamado `.env` (baseado no `.env.example`) e preencha com os seus dados:

```env
STACKSPOT_REALM=zup
STACKSPOT_CLIENT_ID=cole_seu_client_id_aqui
STACKSPOT_CLIENT_KEY=cole_sua_client_key_aqui
STACKSPOT_AGENT_SLUG=cole_o_slug_do_seu_agente_aqui
```

---

## ▶️ 4. Executar a aplicação

Com o ambiente virtual ativo, rode:

```bash
python main.py
```

**Comandos disponíveis no terminal:**
- **Texto livre:** Descreva uma ou mais tarefas em linguagem natural (ex: *"Terminar relatório até sexta, urgente, 2 horas"*).
- `listar`: Exibe todas as tarefas salvas no SQLite e seus arquivos `.json`.
- `sair`: Encerra o programa.
