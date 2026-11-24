import os
import json
import sqlite3
from datetime import datetime
from typing import List, Tuple
from models import Task

DIRETORIO_PERSISTENCIA = "persistencia"
DB_NAME = "tarefas.db"


def inicializar_persistencia():
    os.makedirs(DIRETORIO_PERSISTENCIA, exist_ok=True)
    conexao = sqlite3.connect(DB_NAME)
    cursor = conexao.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tarefas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            categoria TEXT NOT NULL,
            prioridade TEXT NOT NULL,
            prazo TEXT,
            duracao_estimada_horas REAL,
            status TEXT NOT NULL,
            arquivo_json TEXT UNIQUE NOT NULL,
            criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conexao.commit()
    conexao.close()


def salvar_tarefa(tarefa: Task) -> str:
    os.makedirs(DIRETORIO_PERSISTENCIA, exist_ok=True)
    carimbo = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    nome_arquivo = f"tarefa_{carimbo}.json"
    caminho_json = os.path.join(DIRETORIO_PERSISTENCIA, nome_arquivo).replace("\\", "/")

    # 1. Salva a tarefa estruturada no diretório de persistência em JSON
    with open(caminho_json, "w", encoding="utf-8") as arquivo:
        arquivo.write(tarefa.model_dump_json(indent=2))

    # 2. Registra no banco SQLite relacionando com o arquivo JSON salvo
    conexao = sqlite3.connect(DB_NAME)
    cursor = conexao.cursor()
    cursor.execute("""
        INSERT INTO tarefas (
            titulo, categoria, prioridade, prazo, duracao_estimada_horas, status, arquivo_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        tarefa.titulo,
        tarefa.categoria,
        tarefa.prioridade,
        tarefa.prazo.isoformat() if tarefa.prazo else None,
        tarefa.duracao_estimada_horas,
        tarefa.status,
        caminho_json
    ))
    conexao.commit()
    conexao.close()

    return caminho_json


def sincronizar_jsons_com_db():
    """
    Lê os arquivos JSON do diretório de persistência e garante que todos
    estejam relacionados e cadastrados no banco SQLite.
    """
    os.makedirs(DIRETORIO_PERSISTENCIA, exist_ok=True)
    conexao = sqlite3.connect(DB_NAME)
    cursor = conexao.cursor()

    for nome_arquivo in sorted(os.listdir(DIRETORIO_PERSISTENCIA)):
        if not nome_arquivo.endswith(".json"):
            continue

        caminho_json = os.path.join(DIRETORIO_PERSISTENCIA, nome_arquivo).replace("\\", "/")
        cursor.execute("SELECT id FROM tarefas WHERE arquivo_json = ?", (caminho_json,))
        if cursor.fetchone() is None:
            with open(caminho_json, "r", encoding="utf-8") as f:
                dados = json.load(f)
            tarefa = Task.model_validate(dados)
            cursor.execute("""
                INSERT INTO tarefas (
                    titulo, categoria, prioridade, prazo, duracao_estimada_horas, status, arquivo_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                tarefa.titulo,
                tarefa.categoria,
                tarefa.prioridade,
                tarefa.prazo.isoformat() if tarefa.prazo else None,
                tarefa.duracao_estimada_horas,
                tarefa.status,
                caminho_json
            ))

    conexao.commit()
    conexao.close()


def listar_tarefas() -> List[Tuple]:
    sincronizar_jsons_com_db()
    conexao = sqlite3.connect(DB_NAME)
    cursor = conexao.cursor()
    cursor.execute("""
        SELECT id, titulo, categoria, prioridade, prazo, duracao_estimada_horas, status, arquivo_json
        FROM tarefas
        ORDER BY id ASC
    """)
    registros = cursor.fetchall()
    conexao.close()
    return registros