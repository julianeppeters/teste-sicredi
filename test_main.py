import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
MAIN_FILE = PROJECT_ROOT / "main.py"
INPUT_FILE = PROJECT_ROOT / "solicitacoes.json"


class TestProcessamentoSolicitacoes(unittest.TestCase):
    def setUp(self):
        if not MAIN_FILE.exists():
            self.fail("main.py não foi encontrado na raiz do projeto.")
        if not INPUT_FILE.exists():
            self.fail("solicitacoes.json não foi encontrado na raiz do projeto.")


    def executar_aplicacao(self, pasta, diretorio_execucao=None):
        arquivo_main = pasta / "main.py"
        arquivo_main.write_text(
            MAIN_FILE.read_text(encoding="utf-8"),
            encoding="utf-8",
        )

        return subprocess.run(
            [sys.executable, str(arquivo_main)],
            cwd=diretorio_execucao or pasta,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )




    def ler_csv(self, caminho):
        with caminho.open("r", encoding="utf-8-sig", newline="") as arquivo:
            return list(csv.DictReader(arquivo))

    def test_processa_arquivo_real_e_gera_csv(self):
        """Verifica o fluxo principal com o arquivo de entrada do projeto."""
        with tempfile.TemporaryDirectory() as temp:
            pasta = Path(temp)
            (pasta / "solicitacoes.json").write_text(
                INPUT_FILE.read_text(encoding="utf-8"), encoding="utf-8"
            )

            resultado = self.executar_aplicacao(pasta)

            self.assertEqual(resultado.returncode, 0, resultado.stderr)
            csv_file = pasta / "aprovados.csv"
            self.assertTrue(csv_file.exists(), "aprovados.csv não foi gerado.")

            registros = self.ler_csv(csv_file)
            ids = [int(registro["id"]) for registro in registros]
            self.assertEqual(ids, [1, 4, 6, 9, 12, 13, 15])
            self.assertEqual(len(registros), 7)
            self.assertEqual(list(registros[0].keys()), ["id", "nome", "cpf"])
            self.assertTrue(all(registro["cpf"].strip() for registro in registros))

            log = (pasta / "processamento.log").read_text(encoding="utf-8")
            self.assertIn("Total de registros lidos: 15", log)
            self.assertIn("Total de registros exportados: 7", log)
            self.assertIn("Processamento concluído com sucesso.", log)

    def test_nao_exporta_cpf_vazio(self):
        """Garante que registros aprovados sem CPF não sejam exportados."""
        dados = [
            {"id": 100, "nome": "Pessoa Sem CPF", "cpf": "", "status": "APROVADO"},
            {"id": 101, "nome": "Pessoa Aprovada", "cpf": "12345678900", "status": "APROVADO"},
        ]
        with tempfile.TemporaryDirectory() as temp:
            pasta = Path(temp)
            (pasta / "solicitacoes.json").write_text(
                json.dumps(dados, ensure_ascii=False), encoding="utf-8"
            )
            resultado = self.executar_aplicacao(pasta)

            self.assertEqual(resultado.returncode, 0, resultado.stderr)
            registros = self.ler_csv(pasta / "aprovados.csv")
            self.assertEqual([registro["id"] for registro in registros], ["101"])

            log = (pasta / "processamento.log").read_text(encoding="utf-8")
            self.assertIn("CPF inválido, vazio ou nulo", log)

    def test_nao_exporta_status_diferente_de_aprovado(self):
        """Garante que somente registros APROVADO sejam exportados."""
        dados = [
            {"id": 200, "nome": "Pendente", "cpf": "11111111111", "status": "PENDENTE"},
            {"id": 201, "nome": "Reprovado", "cpf": "22222222222", "status": "REPROVADO"},
            {"id": 202, "nome": "Aprovado", "cpf": "33333333333", "status": "APROVADO"},
        ]
        with tempfile.TemporaryDirectory() as temp:
            pasta = Path(temp)
            (pasta / "solicitacoes.json").write_text(
                json.dumps(dados, ensure_ascii=False), encoding="utf-8"
            )
            resultado = self.executar_aplicacao(pasta)

            self.assertEqual(resultado.returncode, 0, resultado.stderr)
            registros = self.ler_csv(pasta / "aprovados.csv")
            self.assertEqual([registro["id"] for registro in registros], ["202"])

    def test_json_invalido_encerra_com_erro_e_registra_log(self):
        """Confirma código de erro e registro da falha quando o JSON é inválido."""
        with tempfile.TemporaryDirectory() as temp:
            pasta = Path(temp)
            (pasta / "solicitacoes.json").write_text('{"id": 1,', encoding="utf-8")

            resultado = self.executar_aplicacao(pasta)

            self.assertNotEqual(resultado.returncode, 0)
            log = (pasta / "processamento.log").read_text(encoding="utf-8")
            self.assertIn("JSON inválido", log)
            self.assertIn("Processamento encerrado com erro", log)
            self.assertFalse((pasta / "aprovados.csv").exists())

    def test_arquivo_de_entrada_inexistente_encerra_com_erro_e_registra_log(self):
        """Confirma o tratamento do arquivo JSON ausente."""
        with tempfile.TemporaryDirectory() as temp:
            pasta = Path(temp)
            resultado = self.executar_aplicacao(pasta)

            self.assertNotEqual(resultado.returncode, 0)
            log = (pasta / "processamento.log").read_text(encoding="utf-8")
            self.assertIn("Arquivo de entrada não encontrado", log)
            self.assertIn("Processamento encerrado com erro", log)
            self.assertFalse((pasta / "aprovados.csv").exists())

    def test_falha_na_geracao_csv_encerra_com_erro_e_registra_log(self):
        """Simula uma falha de escrita criando uma pasta com o nome do CSV."""
        dados = [
            {"id": 400, "nome": "Pessoa Aprovada", "cpf": "12345678900", "status": "APROVADO"}
        ]
        with tempfile.TemporaryDirectory() as temp:
            pasta = Path(temp)
            (pasta / "solicitacoes.json").write_text(
                json.dumps(dados, ensure_ascii=False), encoding="utf-8"
            )
            (pasta / "aprovados.csv").mkdir()

            resultado = self.executar_aplicacao(pasta)

            self.assertNotEqual(resultado.returncode, 0)
            log = (pasta / "processamento.log").read_text(encoding="utf-8")
            self.assertIn("Erro durante a geração do CSV", log)
            self.assertIn("Processamento encerrado com erro", log)

    def test_trata_registro_incompleto_sem_interromper_processamento(self):
        """Registros incompletos são registrados e ignorados, sem perder os válidos."""
        dados = [
            {"id": 300, "nome": "Registro Válido", "cpf": "44444444444", "status": "APROVADO"},
            {"id": 301, "nome": "Sem CPF", "status": "APROVADO"},
            {"id": 302, "cpf": "55555555555", "status": "APROVADO"},
        ]
        with tempfile.TemporaryDirectory() as temp:
            pasta = Path(temp)
            (pasta / "solicitacoes.json").write_text(
                json.dumps(dados, ensure_ascii=False), encoding="utf-8"
            )
            resultado = self.executar_aplicacao(pasta)

            self.assertEqual(resultado.returncode, 0, resultado.stderr)
            registros = self.ler_csv(pasta / "aprovados.csv")
            self.assertEqual([registro["id"] for registro in registros], ["300"])

            log = (pasta / "processamento.log").read_text(encoding="utf-8")
            self.assertIn("campos ausentes", log)

    def test_ignora_cpf_nulo(self):
        """Ignora CPF null e continua processando os demais registros."""
        dados = [
            {"id": 501, "nome": "Sem CPF", "cpf": None, "status": "APROVADO"},
            {"id": 502, "nome": "Com CPF", "cpf": "12345678900", "status": "APROVADO"},
        ]

        with tempfile.TemporaryDirectory() as temp:
            pasta = Path(temp)
            (pasta / "solicitacoes.json").write_text(
                json.dumps(dados), encoding="utf-8"
            )

            resultado = self.executar_aplicacao(pasta)

            self.assertEqual(resultado.returncode, 0, resultado.stderr)
            registros = self.ler_csv(pasta / "aprovados.csv")
            self.assertEqual([r["id"] for r in registros], ["502"])

            log = (pasta / "processamento.log").read_text(encoding="utf-8")
            self.assertIn("CPF", log)
            self.assertIn("nulo", log.lower())

    def test_ignora_cpf_com_apenas_espacos(self):
        """Ignora CPF contendo somente espaços."""
        dados = [
            {"id": 503, "nome": "CPF em branco", "cpf": "   ", "status": "APROVADO"},
            {"id": 504, "nome": "Com CPF", "cpf": "12345678900", "status": "APROVADO"},
        ]

        with tempfile.TemporaryDirectory() as temp:
            pasta = Path(temp)
            (pasta / "solicitacoes.json").write_text(
                json.dumps(dados), encoding="utf-8"
            )

            resultado = self.executar_aplicacao(pasta)

            self.assertEqual(resultado.returncode, 0, resultado.stderr)
            registros = self.ler_csv(pasta / "aprovados.csv")
            self.assertEqual([r["id"] for r in registros], ["504"])

            log = (pasta / "processamento.log").read_text(encoding="utf-8")
            self.assertIn("CPF", log)
            self.assertIn("Registro 503 ignorado", log)
            self.assertIn("CPF inválido, vazio ou nulo", log)
    def test_json_valido_com_estrutura_incorreta(self):
        """Rejeita um JSON válido que não contém uma lista de registros."""
        with tempfile.TemporaryDirectory() as temp:
            pasta = Path(temp)
            (pasta / "solicitacoes.json").write_text(
                '{"id": 1, "nome": "Maria"}', encoding="utf-8"
            )

            resultado = self.executar_aplicacao(pasta)

            self.assertNotEqual(resultado.returncode, 0)

            log = (pasta / "processamento.log").read_text(encoding="utf-8")
            self.assertIn("Processamento encerrado com erro", log)
            self.assertFalse((pasta / "aprovados.csv").exists())

    def test_execucao_a_partir_de_outra_pasta(self):
        """Mantém entrada e saídas na pasta do projeto."""
        dados = [
            {"id": 505, "nome": "Teste de caminho",
             "cpf": "12345678900", "status": "APROVADO"}
        ]

        with tempfile.TemporaryDirectory() as temp:
            raiz = Path(temp)
            projeto = raiz / "projeto"
            projeto.mkdir()
            outra_pasta = raiz / "outra_pasta"
            outra_pasta.mkdir()

            (projeto / "solicitacoes.json").write_text(
                json.dumps(dados), encoding="utf-8"
            )

            resultado = self.executar_aplicacao(projeto, outra_pasta)

            self.assertEqual(resultado.returncode, 0, resultado.stderr)
            self.assertTrue((projeto / "aprovados.csv").exists())
            self.assertTrue((projeto / "processamento.log").exists())
            self.assertFalse((outra_pasta / "aprovados.csv").exists())
            self.assertFalse((outra_pasta / "processamento.log").exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
