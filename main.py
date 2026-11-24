import json
from datetime import date
from pydantic import ValidationError
from client import interpretar_solicitacao
from storage import inicializar_persistencia, salvar_tarefa, listar_tarefas
from models import Task


def exibir_tarefa_formatada(tarefa: Task, numero: int = 1):
    prazo_texto = tarefa.prazo.strftime("%d/%m/%Y") if tarefa.prazo else "Não informado"
    duracao_texto = f"{tarefa.duracao_estimada_horas}h" if tarefa.duracao_estimada_horas is not None else "Não informada"

    print("\n" + "=" * 52)
    print(f"📋 TAREFA #{numero}")
    print("=" * 52)
    print(f"  Título:     {tarefa.titulo}")
    print(f"  Categoria:  {tarefa.categoria}")
    print(f"  Prioridade: {tarefa.prioridade}")
    print(f"  Prazo:      {prazo_texto}")
    print(f"  Duração:    {duracao_texto}")
    print(f"  Status:     {tarefa.status}")
    print("=" * 52)


def corrigir_tarefa(tarefa: Task) -> Task:
    print("\n✏️  Modo de Correção (pressione Enter para manter o valor atual):")

    novo_titulo = input(f"  Título [{tarefa.titulo}]: ").strip()
    nova_categoria = input(f"  Categoria [{tarefa.categoria}]: ").strip()
    nova_prioridade = input(f"  Prioridade (Baixa/Média/Alta) [{tarefa.prioridade}]: ").strip()
    novo_prazo = input(f"  Prazo (AAAA-MM-DD ou 'limpar') [{tarefa.prazo or 'None'}]: ").strip()
    nova_duracao = input(f"  Duração em horas (ex: 2.5 ou 'limpar') [{tarefa.duracao_estimada_horas or 'None'}]: ").strip()

    dados_atualizados = tarefa.model_dump()

    if novo_titulo:
        dados_atualizados["titulo"] = novo_titulo
    if nova_categoria:
        dados_atualizados["categoria"] = nova_categoria
    if nova_prioridade:
        dados_atualizados["prioridade"] = nova_prioridade
    if novo_prazo.lower() == "limpar":
        dados_atualizados["prazo"] = None
    elif novo_prazo:
        dados_atualizados["prazo"] = date.fromisoformat(novo_prazo)
    if nova_duracao.lower() == "limpar":
        dados_atualizados["duracao_estimada_horas"] = None
    elif nova_duracao:
        dados_atualizados["duracao_estimada_horas"] = float(nova_duracao.replace(",", "."))

    # Revalida toda a tarefa com o Pydantic após a edição manual
    return Task.model_validate(dados_atualizados)


def exibir_lista_cadastrada():
    registros = listar_tarefas()
    if not registros:
        print("\n📭 Nenhuma tarefa cadastrada até o momento.")
        return

    print("\n" + "=" * 75)
    print("📚 TAREFAS CADASTRADAS (DB + ARQUIVOS JSON)")
    print("=" * 75)
    for reg in registros:
        id_db, titulo, categoria, prioridade, prazo, duracao, status, arquivo_json = reg
        prazo_str = prazo if prazo else "Sem prazo"
        dur_str = f"{duracao}h" if duracao is not None else "-"
        print(f"#{id_db} | {titulo} [{categoria}]")
        print(f"     Prioridade: {prioridade} | Prazo: {prazo_str} | Duração: {dur_str} | Status: {status}")
        print(f"     Arquivo vinculado: {arquivo_json}")
        print("-" * 75)


def main():
    inicializar_persistencia()
    print("=" * 58)
    print("🧠 INTERPRETADOR INTELIGENTE DE TAREFAS - STACKSPOT AI")
    print("Descreva o que precisa fazer em linguagem natural.")
    print("Comandos: 'listar' para ver tarefas | 'sair' para encerrar.")
    print("=" * 58)

    while True:
        try:
            entrada = input("\nVocê: ").strip()

            if not entrada:
                continue

            if entrada.lower() == "sair":
                print("Encerrando o interpretador. Até mais!")
                break

            if entrada.lower() == "listar":
                exibir_lista_cadastrada()
                continue

            print("Analisando solicitação com StackSpot AI...")
            resultado = interpretar_solicitacao(entrada)

            if not resultado.informacao_suficiente or not resultado.tarefas:
                motivo = resultado.motivo_insuficiencia or "Não foi possível identificar uma tarefa clara."
                print(f"\n⚠️  Informação insuficiente: {motivo}")
                print("Tente detalhar melhor qual ação precisa realizar.")
                continue

            print(f"\n✅ {len(resultado.tarefas)} tarefa(s) identificada(s)!")

            for idx, tarefa in enumerate(resultado.tarefas, start=1):
                exibir_tarefa_formatada(tarefa, idx)

                while True:
                    opcao = input("Salvar tarefa? [s = sim / c = corrigir / n = descartar]: ").strip().lower()
                    if opcao == "c":
                        try:
                            tarefa = corrigir_tarefa(tarefa)
                            exibir_tarefa_formatada(tarefa, idx)
                        except (ValidationError, ValueError) as erro_edicao:
                            print(f"❌ Valor inválido na correção: {erro_edicao}")
                    elif opcao == "s":
                        caminho = salvar_tarefa(tarefa)
                        print(f"💾 Tarefa salva com sucesso em '{caminho}' e registrada no SQLite!")
                        break
                    elif opcao == "n":
                        print("🗑️  Tarefa descartada.")
                        break
                    else:
                        print("Opção inválida. Digite 's', 'c' ou 'n'.")

        except KeyboardInterrupt:
            print("\nOperação interrompida pelo usuário. Saindo...")
            break
        except json.JSONDecodeError:
            print("\n❌ Erro de contrato: A resposta da LLM não veio em um formato JSON válido.")
        except ValidationError as erro_validacao:
            print(f"\n❌ Erro de validação Pydantic (contrato violado):\n{erro_validacao}")
        except Exception as erro:
            print(f"\n❌ Ocorreu um erro: {erro}")


if __name__ == "__main__":
    main()