import csv
import json
import logging
from pathlib import Path


INPUT_FILE = Path("solicitacoes.json")
OUTPUT_FILE = Path("aprovados.csv")
LOG_FILE = Path("processamento.log")

REQUIRED_FIELDS = {"id", "nome", "cpf", "status"}


def configurar_log() -> logging.Logger:
    """Configura o arquivo de log da execução."""
    logger = logging.getLogger("processamento")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    handler = logging.FileHandler(LOG_FILE, mode="w", encoding="utf-8")
    handler.setFormatter(
        logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    )
    logger.addHandler(handler)

    return logger


def carregar_json(logger: logging.Logger) -> list:
    """Carrega os registros do arquivo JSON."""
    try:
        with INPUT_FILE.open("r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
    except FileNotFoundError:
        logger.error("Arquivo de entrada não encontrado: %s", INPUT_FILE)
        raise
    except json.JSONDecodeError as erro:
        logger.error("JSON inválido: %s", erro)
        raise

    if not isinstance(dados, list):
        logger.error("JSON inválido: o conteúdo principal deve ser uma lista.")
        raise ValueError("O JSON deve conter uma lista de registros.")

    return dados


def filtrar_aprovados(dados: list, logger: logging.Logger) -> list:
    """Filtra registros aprovados que possuem CPF preenchido."""
    aprovados = []

    for posicao, registro in enumerate(dados, start=1):
        if not isinstance(registro, dict):
            logger.warning(
                "Registro %d ignorado: formato inválido; era esperado um objeto.",
                posicao,
            )
            continue

        campos_faltantes = REQUIRED_FIELDS - registro.keys()
        if campos_faltantes:
            logger.warning(
                "Registro %d ignorado: campos ausentes: %s",
                posicao,
                ", ".join(sorted(campos_faltantes)),
            )
            continue

        status = registro.get("status")
        cpf = registro.get("cpf")

        if status != "APROVADO":
            logger.info(
                "Registro %s ignorado: status '%s'.",
                registro.get("id", posicao),
                status,
            )
            continue

        if cpf is None or (isinstance(cpf, str) and not cpf.strip()):
            logger.info(
                "Registro %s ignorado: CPF vazio ou nulo.",
                registro.get("id", posicao),
            )
            continue

        aprovados.append(registro)

    return aprovados


def gerar_csv(registros: list, logger: logging.Logger) -> None:
    """Gera o arquivo CSV com os registros aprovados."""
    try:
        with OUTPUT_FILE.open(
            "w", newline="", encoding="utf-8"
        ) as arquivo:
            escritor = csv.DictWriter(
                arquivo,
                fieldnames=["id", "nome", "cpf"],
                delimiter=",",
            )
            escritor.writeheader()

            for registro in registros:
                escritor.writerow(
                    {
                        "id": registro["id"],
                        "nome": registro["nome"],
                        "cpf": registro["cpf"],
                    }
                )
    except (OSError, csv.Error) as erro:
        logger.error("Erro durante a geração do CSV: %s", erro)
        raise


def main() -> None:
    logger = configurar_log()
    logger.info("Início do processamento.")

    try:
        dados = carregar_json(logger)
        logger.info("Total de registros lidos: %d", len(dados))

        aprovados = filtrar_aprovados(dados, logger)
        gerar_csv(aprovados, logger)

        logger.info("Total de registros exportados: %d", len(aprovados))
        logger.info("Arquivo gerado: %s", OUTPUT_FILE)
        logger.info("Processamento concluído com sucesso.")

    except (FileNotFoundError, json.JSONDecodeError, ValueError, OSError, csv.Error) as erro:
        logger.error("Processamento encerrado com erro: %s", erro)
        raise


if __name__ == "__main__":
    main()
