import csv
import json
import logging
import sys
from pathlib import Path
from typing import Any

PASTA_PROJETO = Path(__file__).resolve().parent
ARQUIVO_ENTRADA = PASTA_PROJETO / "solicitacoes.json"
ARQUIVO_SAIDA = PASTA_PROJETO / "aprovados.csv"
ARQUIVO_LOG = PASTA_PROJETO / "processamento.log"
COLUNAS_CSV = ["id", "nome", "cpf"]


def configurar_log() -> None:
    logging.basicConfig(
        filename=ARQUIVO_LOG,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        encoding="utf-8",
        force=True,
    )


def carregar_json(caminho: Path = ARQUIVO_ENTRADA) -> list[Any]:
    with caminho.open("r", encoding="utf-8") as arquivo:
        dados = json.load(arquivo)
    if not isinstance(dados, list):
        raise ValueError("A estrutura do JSON deve ser uma lista de solicitações.")
    return dados


def filtrar_aprovados(dados: list[Any]) -> tuple[list[dict[str, Any]], int]:
    aprovados: list[dict[str, Any]] = []
    ignorados = 0

    for indice, registro in enumerate(dados, start=1):
        if not isinstance(registro, dict):
            logging.warning("Registro %s ignorado: formato inválido (não é um objeto).", indice)
            ignorados += 1
            continue

        identificador = registro.get("id", indice)
        campos_obrigatorios = ("id", "nome", "cpf", "status")
        faltantes = [campo for campo in campos_obrigatorios if campo not in registro]
        if faltantes:
            logging.warning(
                "Registro %s ignorado: campos ausentes (%s).",
                identificador, ", ".join(faltantes)
            )
            ignorados += 1
            continue

        cpf = registro.get("cpf")
        if registro.get("status") != "APROVADO":
            logging.info("Registro %s ignorado: status diferente de APROVADO.", identificador)
            ignorados += 1
            continue

        if cpf is None or not str(cpf).strip():
            logging.warning(
                "Registro %s ignorado: CPF inválido, vazio ou nulo.", identificador
            )
            ignorados += 1
            continue

        aprovados.append({
            "id": registro["id"],
            "nome": registro["nome"],
            "cpf": str(cpf).strip(),
        })

    return aprovados, ignorados


def gerar_csv(registros: list[dict[str, Any]], caminho: Path = ARQUIVO_SAIDA) -> None:
    with caminho.open("w", encoding="utf-8-sig", newline="") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=COLUNAS_CSV)
        escritor.writeheader()
        escritor.writerows(registros)


def registrar_erro(mensagem: str, erro: BaseException | None = None) -> None:
    logging.error(
        "Processamento encerrado com erro: %s",
        mensagem,
        exc_info=erro is not None,
    )


def main() -> int:
    configurar_log()
    print("Iniciando processamento das solicitações...")
    logging.info("Início do processamento.")

    try:
        dados = carregar_json()
    except FileNotFoundError as erro:
        mensagem = f"Arquivo de entrada não encontrado: '{ARQUIVO_ENTRADA.name}'."
        print(mensagem, file=sys.stderr)
        registrar_erro(mensagem, erro)
        return 1
    except json.JSONDecodeError as erro:
        mensagem = f"JSON inválido: {erro}"
        print(mensagem, file=sys.stderr)
        registrar_erro(mensagem, erro)
        return 1
    except (UnicodeDecodeError, ValueError) as erro:
        mensagem = f"Erro ao ler o arquivo JSON: {erro}"
        print(mensagem, file=sys.stderr)
        registrar_erro(mensagem, erro)
        return 1
    except OSError as erro:
        mensagem = f"Erro ao abrir o arquivo de entrada: {erro}"
        print(mensagem, file=sys.stderr)
        registrar_erro(mensagem, erro)
        return 1

    logging.info("Total de registros lidos: %s", len(dados))
    aprovados, ignorados = filtrar_aprovados(dados)

    try:
        gerar_csv(aprovados)
    except (OSError, csv.Error) as erro:
        mensagem = f"Erro durante a geração do CSV: {erro}"
        print(mensagem, file=sys.stderr)
        registrar_erro(mensagem, erro)
        return 1

    logging.info("Total de registros exportados: %s", len(aprovados))
    logging.info("Total de registros ignorados: %s", ignorados)
    logging.info("Processamento concluído com sucesso.")

    print("\nProcessamento concluído com sucesso!")
    print(f"Solicitações lidas: {len(dados)}")
    print(f"Solicitações aprovadas exportadas: {len(aprovados)}")
    print(f"Solicitações ignoradas: {ignorados}")
    print(f"Arquivo CSV gerado: {ARQUIVO_SAIDA}")
    print(f"Arquivo de log: {ARQUIVO_LOG}")

    if aprovados:
        print("\nRegistros exportados:")
        print("ID | Nome | CPF")
        print("-" * 55)
        for registro in aprovados:
            print(f"{registro['id']} | {registro['nome']} | {registro['cpf']}")
    else:
        print("\nNenhuma solicitação atendeu aos critérios de exportação.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
