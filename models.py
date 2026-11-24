from datetime import date
from typing import Literal, Optional, List
from pydantic import BaseModel, Field, field_validator


class Task(BaseModel):
    titulo: str = Field(..., min_length=3, description="Título claro e objetivo da tarefa")
    categoria: str = Field(default="Geral", min_length=2, description="Categoria da tarefa (ex: Trabalho, Pessoal, Financeiro)")
    prioridade: Literal["Baixa", "Média", "Alta"] = Field(
        default="Média",
        description="Prioridade permitida: Baixa, Média ou Alta"
    )
    prazo: Optional[date] = Field(
        default=None,
        description="Data limite no formato YYYY-MM-DD ou null se ausente"
    )
    duracao_estimada_horas: Optional[float] = Field(
        default=None,
        gt=0,
        description="Duração estimada em horas (número positivo) ou null se ausente"
    )
    status: Literal["Pendente", "Em andamento", "Concluída"] = Field(
        default="Pendente",
        description="Status inicial da tarefa"
    )

    @field_validator("titulo", "categoria")
    @classmethod
    def nao_pode_ser_vazio(cls, valor: str) -> str:
        if not valor or not valor.strip():
            raise ValueError("O campo não pode conter apenas espaços em branco.")
        return valor.strip()


class InterpretacaoResultado(BaseModel):
    informacao_suficiente: bool = Field(
        default=True,
        description="False se o texto do usuário for vago demais para identificar uma tarefa real"
    )
    motivo_insuficiencia: Optional[str] = Field(
        default=None,
        description="Explicação curta caso informacao_suficiente seja False"
    )
    tarefas: List[Task] = Field(
        default_factory=list,
        description="Lista com uma ou mais tarefas extraídas da solicitação"
    )