import csv
import json
import logging
import sys
from pathlib import Path
from typing import Any


ARQUIVO_ENTRADA = Path("solicitacoes.json")
ARQUIVO_SAIDA = Path("aprovados.csv")
ARQUIVO_LOG = Path("processamento.log")
COLUNAS_CSV = ["id", "nome", "cpf"]


def configurar_log() -> None:
    """Configura o registro das informações de execução."""
    logging.basicConfig(
        filename=ARQUIVO_LOG,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        encoding="utf-8",
        force=True,
    )


def carregar_json(caminho: Path = ARQUIVO_ENTRADA) -> list[Any]:
    """Lê o JSON e confirma que o conteúdo principal é uma lista."""
    with caminho.open("r", encoding="utf-8") as arquivo:
        dados = json.load(arquivo)

    if not isinstance(dados, list):
        raise ValueError("A estrutura do JSON deve ser uma lista de solicitações.")

    return dados


def filtrar_aprovados(dados: list[Any]) -> tuple[list[dict[str, Any]], int]:
    """Seleciona registros aprovados com CPF preenchido; ignora registros inválidos."""
    aprovados = []
    ignorados = 0

    for indice, registro in enumerate(dados, start=1):
        if not isinstance(registro, dict):
            logging.warning("Registro %s ignorado: formato inválido (não é um objeto).", indice)
            ignorados += 1
            continue

        campos_obrigatorios = ("id", "nome", "cpf", "status")
        faltantes = [campo for campo in campos_obrigatorios if campo not in registro]
        if faltantes:
            logging.warning(
                "Registro %s ignorado: campos ausentes (%s).",
                indice,
                ", ".join(faltantes),
            )
            ignorados += 1
            continue

        cpf = registro.get("cpf")
        if registro.get("status") != "APROVADO":
            logging.info("Registro %s ignorado: status diferente de APROVADO.", indice)
            ignorados += 1
            continue

        if cpf is None or not str(cpf).strip():
            logging.warning("Registro %s ignorado: CPF vazio ou nulo.", indice)
            ignorados += 1
            continue

        aprovados.append(
            {
                "id": registro["id"],
                "nome": registro["nome"],
                "cpf": str(cpf).strip(),
            }
        )

    return aprovados, ignorados


def gerar_csv(registros: list[dict[str, Any]], caminho: Path = ARQUIVO_SAIDA) -> None:
    """Grava os registros aprovados em CSV UTF-8."""
    with caminho.open("w", encoding="utf-8-sig", newline="") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=COLUNAS_CSV)
        escritor.writeheader()
        escritor.writerows(registros)


def main() -> int:
    configurar_log()
    print("Iniciando processamento das solicitações...")
    logging.info("Início do processamento.")

    try:
        dados = carregar_json()
    except FileNotFoundError:
        mensagem = f"Erro: arquivo de entrada '{ARQUIVO_ENTRADA}' não encontrado."
        print(mensagem, file=sys.stderr)
        logging.exception(mensagem)
        return 1
    except (json.JSONDecodeError, UnicodeDecodeError, ValueError) as erro:
        mensagem = f"Erro ao ler o arquivo JSON: {erro}"
        print(mensagem, file=sys.stderr)
        logging.exception(mensagem)
        return 1
    except OSError as erro:
        mensagem = f"Erro ao abrir o arquivo de entrada: {erro}"
        print(mensagem, file=sys.stderr)
        logging.exception(mensagem)
        return 1

    logging.info("Total de registros lidos: %s", len(dados))
    aprovados, ignorados = filtrar_aprovados(dados)

    try:
        gerar_csv(aprovados)
    except (OSError, csv.Error) as erro:
        mensagem = f"Erro ao gerar '{ARQUIVO_SAIDA}': {erro}"
        print(mensagem, file=sys.stderr)
        logging.exception(mensagem)
        return 1

    logging.info("Total de registros exportados: %s", len(aprovados))
    logging.info("Total de registros ignorados: %s", ignorados)
    logging.info("Processamento concluído com sucesso.")

    print("\nProcessamento concluído com sucesso!")
    print(f"Solicitações lidas: {len(dados)}")
    print(f"Solicitações aprovadas exportadas: {len(aprovados)}")
    print(f"Solicitações ignoradas: {ignorados}")
    print(f"Arquivo CSV gerado: {ARQUIVO_SAIDA.resolve()}")
    print(f"Arquivo de log: {ARQUIVO_LOG.resolve()}")

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
