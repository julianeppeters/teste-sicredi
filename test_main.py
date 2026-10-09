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

    def executar_aplicacao(self, pasta):
        resultado = subprocess.run(
            [sys.executable, str(MAIN_FILE)],
            cwd=pasta,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        return resultado

    def test_processa_arquivo_real_e_gera_csv(self):
        """Verifica o fluxo principal usando o solicitacoes.json do projeto."""
        with tempfile.TemporaryDirectory() as temp:
            temp_path = Path(temp)
            (temp_path / "solicitacoes.json").write_text(
                INPUT_FILE.read_text(encoding="utf-8"),
                encoding="utf-8",
            )

            resultado = self.executar_aplicacao(temp_path)

            self.assertEqual(
                resultado.returncode,
                0,
                msg=f"Programa terminou com erro:\n{resultado.stderr}",
            )

            csv_file = temp_path / "aprovados.csv"
            self.assertTrue(csv_file.exists(), "aprovados.csv não foi gerado.")

            with csv_file.open(
                "r", encoding="utf-8-sig", newline=""
            ) as arquivo:
                registros = list(csv.DictReader(arquivo))

            # No arquivo fornecido, somente os IDs 1, 4, 6, 9, 12, 13 e 15
            # atendem simultaneamente às regras:
            # status = APROVADO e CPF preenchido.
            ids = [int(registro["id"]) for registro in registros]

            self.assertEqual(ids, [1, 4, 6, 9, 12, 13, 15])
            self.assertEqual(len(registros), 7)

            for registro in registros:
                self.assertEqual(registro["status"], None) if "status" in registro else None
                self.assertTrue(registro["cpf"].strip())
                self.assertIn("id", registro)
                self.assertIn("nome", registro)
                self.assertIn("cpf", registro)

    def test_nao_exporta_cpf_vazio(self):
        """Garante que registro APROVADO sem CPF não seja exportado."""
        dados = [
            {
                "id": 100,
                "nome": "Pessoa Sem CPF",
                "cpf": "",
                "status": "APROVADO",
            },
            {
                "id": 101,
                "nome": "Pessoa Aprovada",
                "cpf": "12345678900",
                "status": "APROVADO",
            },
        ]

        with tempfile.TemporaryDirectory() as temp:
            temp_path = Path(temp)
            (temp_path / "solicitacoes.json").write_text(
                json.dumps(dados, ensure_ascii=False),
                encoding="utf-8",
            )

            resultado = self.executar_aplicacao(temp_path)

            self.assertEqual(
                resultado.returncode,
                0,
                msg=f"Programa terminou com erro:\n{resultado.stderr}",
            )

            csv_file = temp_path / "aprovados.csv"
            self.assertTrue(csv_file.exists())

            with csv_file.open(
                "r", encoding="utf-8-sig", newline=""
            ) as arquivo:
                registros = list(csv.DictReader(arquivo))

            self.assertEqual(len(registros), 1)
            self.assertEqual(registros[0]["id"], "101")

    def test_nao_exporta_status_diferente_de_aprovado(self):
        """Garante que somente status APROVADO seja exportado."""
        dados = [
            {
                "id": 200,
                "nome": "Pendente",
                "cpf": "11111111111",
                "status": "PENDENTE",
            },
            {
                "id": 201,
                "nome": "Reprovado",
                "cpf": "22222222222",
                "status": "REPROVADO",
            },
            {
                "id": 202,
                "nome": "Aprovado",
                "cpf": "33333333333",
                "status": "APROVADO",
            },
        ]

        with tempfile.TemporaryDirectory() as temp:
            temp_path = Path(temp)
            (temp_path / "solicitacoes.json").write_text(
                json.dumps(dados, ensure_ascii=False),
                encoding="utf-8",
            )

            resultado = self.executar_aplicacao(temp_path)

            self.assertEqual(
                resultado.returncode,
                0,
                msg=f"Programa terminou com erro:\n{resultado.stderr}",
            )

            with (temp_path / "aprovados.csv").open(
                "r", encoding="utf-8-sig", newline=""
            ) as arquivo:
                registros = list(csv.DictReader(arquivo))

            self.assertEqual([registro["id"] for registro in registros], ["202"])

    def test_trata_json_invalido(self):
        """Verifica se JSON inválido é tratado sem gerar CSV incorreto."""
        with tempfile.TemporaryDirectory() as temp:
            temp_path = Path(temp)
            (temp_path / "solicitacoes.json").write_text(
                '{"id": 1,',
                encoding="utf-8",
            )

            resultado = self.executar_aplicacao(temp_path)

            # O teste aceita encerramento normal ou controlado,
            # desde que a aplicação não gere um CSV com dados inválidos.
            csv_file = temp_path / "aprovados.csv"

            if csv_file.exists():
                with csv_file.open(
                    "r", encoding="utf-8-sig", newline=""
                ) as arquivo:
                    registros = list(csv.DictReader(arquivo))
                self.assertEqual(registros, [])

    def test_trata_registro_incompleto(self):
        """Verifica se registros sem campos obrigatórios não quebram o processamento."""
        dados = [
            {
                "id": 300,
                "nome": "Registro Válido",
                "cpf": "44444444444",
                "status": "APROVADO",
            },
            {
                "id": 301,
                "nome": "Sem CPF",
                "status": "APROVADO",
            },
            {
                "id": 302,
                "cpf": "55555555555",
                "status": "APROVADO",
            },
        ]

        with tempfile.TemporaryDirectory() as temp:
            temp_path = Path(temp)
            (temp_path / "solicitacoes.json").write_text(
                json.dumps(dados, ensure_ascii=False),
                encoding="utf-8",
            )

            resultado = self.executar_aplicacao(temp_path)

            self.assertEqual(
                resultado.returncode,
                0,
                msg=f"Programa terminou com erro:\n{resultado.stderr}",
            )

            csv_file = temp_path / "aprovados.csv"
            self.assertTrue(csv_file.exists())

            with csv_file.open(
                "r", encoding="utf-8-sig", newline=""
            ) as arquivo:
                registros = list(csv.DictReader(arquivo))

            self.assertEqual([registro["id"] for registro in registros], ["300"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
