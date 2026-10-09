import csv
import json
import os
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

    def executar_aplicacao(self, pasta_projeto, diretorio_execucao=None):
        arquivo_main = pasta_projeto / "main.py"
        arquivo_main.write_text(MAIN_FILE.read_text(encoding="utf-8"), encoding="utf-8")
        ambiente = {**os.environ, "PYTHONIOENCODING": "utf-8"}
        return subprocess.run(
            [sys.executable, str(arquivo_main)],
            cwd=diretorio_execucao or pasta_projeto,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=ambiente,
        )

    def ler_csv(self, caminho):
        with caminho.open("r", encoding="utf-8-sig", newline="") as arquivo:
            return list(csv.DictReader(arquivo))

    def preparar_projeto(self, pasta, dados=None):
        conteudo = (INPUT_FILE.read_text(encoding="utf-8") if dados is None
                    else json.dumps(dados, ensure_ascii=False))
        (pasta / "solicitacoes.json").write_text(conteudo, encoding="utf-8")

    def test_processa_arquivo_real_e_gera_csv(self):
        with tempfile.TemporaryDirectory() as temp:
            pasta = Path(temp)
            self.preparar_projeto(pasta)
            resultado = self.executar_aplicacao(pasta)
            self.assertEqual(resultado.returncode, 0, resultado.stderr)
            csv_file = pasta / "aprovados.csv"
            self.assertTrue(csv_file.exists(), "aprovados.csv não foi gerado.")
            registros = self.ler_csv(csv_file)
            ids = [int(r["id"]) for r in registros]
            self.assertEqual(ids, [1, 4, 6, 9, 12, 13, 15])
            self.assertEqual(len(registros), 7)
            self.assertEqual(list(registros[0].keys()), ["id", "nome", "cpf"])
            self.assertTrue(all(r["cpf"].strip() for r in registros))
            log = (pasta / "processamento.log").read_text(encoding="utf-8")
            self.assertIn("Total de registros lidos: 15", log)
            self.assertIn("Total de registros exportados: 7", log)
            self.assertIn("Processamento concluído com sucesso.", log)

    def test_nao_exporta_cpf_vazio(self):
        dados = [
            {"id": 100, "nome": "Pessoa Sem CPF", "cpf": "", "status": "APROVADO"},
            {"id": 101, "nome": "Pessoa Aprovada", "cpf": "12345678900", "status": "APROVADO"},
        ]
        with tempfile.TemporaryDirectory() as temp:
            pasta = Path(temp)
            self.preparar_projeto(pasta, dados)
            resultado = self.executar_aplicacao(pasta)
            self.assertEqual(resultado.returncode, 0, resultado.stderr)
            self.assertEqual([r["id"] for r in self.ler_csv(pasta / "aprovados.csv")], ["101"])
            log = (pasta / "processamento.log").read_text(encoding="utf-8")
            self.assertIn("CPF inválido, vazio ou nulo", log)
            self.assertIn("Registro 100 ignorado", log)

    def test_nao_exporta_status_diferente_de_aprovado(self):
        dados = [
            {"id": 200, "nome": "Pendente", "cpf": "11111111111", "status": "PENDENTE"},
            {"id": 201, "nome": "Reprovado", "cpf": "22222222222", "status": "REPROVADO"},
            {"id": 202, "nome": "Aprovado", "cpf": "33333333333", "status": "APROVADO"},
        ]
        with tempfile.TemporaryDirectory() as temp:
            pasta = Path(temp)
            self.preparar_projeto(pasta, dados)
            resultado = self.executar_aplicacao(pasta)
            self.assertEqual(resultado.returncode, 0, resultado.stderr)
            self.assertEqual([r["id"] for r in self.ler_csv(pasta / "aprovados.csv")], ["202"])

    def test_ignora_status_nulo_vazio_ou_de_tipo_invalido_sem_interromper(self):
        dados = [
            {"id": 701, "nome": "Status nulo", "cpf": "11111111111", "status": None},
            {"id": 702, "nome": "Status numérico", "cpf": "22222222222", "status": 123},
            {"id": 703, "nome": "Status vazio", "cpf": "33333333333", "status": ""},
            {"id": 704, "nome": "Status espaços", "cpf": "44444444444", "status": "   "},
            {"id": 705, "nome": "Aprovado após inválidos", "cpf": "55555555555", "status": "APROVADO"},
        ]
        with tempfile.TemporaryDirectory() as temp:
            pasta = Path(temp)
            self.preparar_projeto(pasta, dados)
            resultado = self.executar_aplicacao(pasta)
            self.assertEqual(resultado.returncode, 0, resultado.stderr)
            registros = self.ler_csv(pasta / "aprovados.csv")
            self.assertEqual([r["id"] for r in registros], ["705"])
            log = (pasta / "processamento.log").read_text(encoding="utf-8")
            self.assertIn("status diferente de APROVADO ou inválido", log)
            for identificador in (701, 702, 703, 704):
                self.assertIn(f"Registro {identificador} ignorado", log)
            self.assertIn("Total de registros exportados: 1", log)

    def test_json_invalido_encerra_com_erro_e_registra_log(self):
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
        with tempfile.TemporaryDirectory() as temp:
            pasta = Path(temp)
            resultado = self.executar_aplicacao(pasta)
            self.assertNotEqual(resultado.returncode, 0)
            log = (pasta / "processamento.log").read_text(encoding="utf-8")
            self.assertIn("Arquivo de entrada não encontrado", log)
            self.assertIn("Processamento encerrado com erro", log)
            self.assertFalse((pasta / "aprovados.csv").exists())

    def test_falha_na_geracao_csv_encerra_com_erro_e_registra_log(self):
        dados = [{"id": 400, "nome": "Pessoa Aprovada", "cpf": "12345678900", "status": "APROVADO"}]
        with tempfile.TemporaryDirectory() as temp:
            pasta = Path(temp)
            self.preparar_projeto(pasta, dados)
            (pasta / "aprovados.csv").mkdir()
            resultado = self.executar_aplicacao(pasta)
            self.assertNotEqual(resultado.returncode, 0)
            log = (pasta / "processamento.log").read_text(encoding="utf-8")
            self.assertIn("Erro durante a geração do CSV", log)
            self.assertIn("Processamento encerrado com erro", log)

    def test_trata_registro_incompleto_sem_interromper_processamento(self):
        dados = [
            {"id": 300, "nome": "Registro Válido", "cpf": "44444444444", "status": "APROVADO"},
            {"id": 301, "nome": "Sem CPF", "status": "APROVADO"},
            {"id": 302, "cpf": "55555555555", "status": "APROVADO"},
        ]
        with tempfile.TemporaryDirectory() as temp:
            pasta = Path(temp)
            self.preparar_projeto(pasta, dados)
            resultado = self.executar_aplicacao(pasta)
            self.assertEqual(resultado.returncode, 0, resultado.stderr)
            self.assertEqual([r["id"] for r in self.ler_csv(pasta / "aprovados.csv")], ["300"])
            log = (pasta / "processamento.log").read_text(encoding="utf-8")
            self.assertIn("campos ausentes", log)
            self.assertIn("Registro 301 ignorado", log)
            self.assertIn("Registro 302 ignorado", log)

    def test_ignora_cpf_nulo(self):
        dados = [
            {"id": 501, "nome": "Sem CPF", "cpf": None, "status": "APROVADO"},
            {"id": 502, "nome": "Com CPF", "cpf": "12345678900", "status": "APROVADO"},
        ]
        with tempfile.TemporaryDirectory() as temp:
            pasta = Path(temp)
            self.preparar_projeto(pasta, dados)
            resultado = self.executar_aplicacao(pasta)
            self.assertEqual(resultado.returncode, 0, resultado.stderr)
            self.assertEqual([r["id"] for r in self.ler_csv(pasta / "aprovados.csv")], ["502"])
            log = (pasta / "processamento.log").read_text(encoding="utf-8")
            self.assertIn("CPF", log)
            self.assertIn("nulo", log.lower())
            self.assertIn("Registro 501 ignorado", log)

    def test_ignora_cpf_com_apenas_espacos(self):
        dados = [
            {"id": 503, "nome": "CPF em branco", "cpf": "   ", "status": "APROVADO"},
            {"id": 504, "nome": "Com CPF", "cpf": "12345678900", "status": "APROVADO"},
        ]
        with tempfile.TemporaryDirectory() as temp:
            pasta = Path(temp)
            self.preparar_projeto(pasta, dados)
            resultado = self.executar_aplicacao(pasta)
            self.assertEqual(resultado.returncode, 0, resultado.stderr)
            self.assertEqual([r["id"] for r in self.ler_csv(pasta / "aprovados.csv")], ["504"])
            log = (pasta / "processamento.log").read_text(encoding="utf-8")
            self.assertIn("CPF", log)
            self.assertIn("Registro 503 ignorado", log)
            self.assertIn("CPF inválido, vazio ou nulo", log)

    def test_json_valido_com_estrutura_incorreta(self):
        with tempfile.TemporaryDirectory() as temp:
            pasta = Path(temp)
            (pasta / "solicitacoes.json").write_text('{"id": 1, "nome": "Maria"}', encoding="utf-8")
            resultado = self.executar_aplicacao(pasta)
            self.assertNotEqual(resultado.returncode, 0)
            log = (pasta / "processamento.log").read_text(encoding="utf-8")
            self.assertIn("Processamento encerrado com erro", log)
            self.assertFalse((pasta / "aprovados.csv").exists())


    def test_ignora_id_nulo_invalido_ou_nao_positivo(self):
        dados = [
            {"id": None, "nome": "ID nulo", "cpf": "11111111111", "status": "APROVADO"},
            {"id": "abc", "nome": "ID texto", "cpf": "22222222222", "status": "APROVADO"},
            {"id": 0, "nome": "ID zero", "cpf": "33333333333", "status": "APROVADO"},
            {"id": 506, "nome": "ID válido", "cpf": "44444444444", "status": "APROVADO"},
        ]
        with tempfile.TemporaryDirectory() as temp:
            pasta = Path(temp)
            self.preparar_projeto(pasta, dados)
            resultado = self.executar_aplicacao(pasta)
            self.assertEqual(resultado.returncode, 0, resultado.stderr)
            self.assertEqual([r["id"] for r in self.ler_csv(pasta / "aprovados.csv")], ["506"])
            log = (pasta / "processamento.log").read_text(encoding="utf-8")
            self.assertIn("campo id inválido", log)

    def test_ignora_nome_nulo_vazio_ou_de_tipo_invalido(self):
        dados = [
            {"id": 601, "nome": None, "cpf": "11111111111", "status": "APROVADO"},
            {"id": 602, "nome": "   ", "cpf": "22222222222", "status": "APROVADO"},
            {"id": 603, "nome": 123, "cpf": "33333333333", "status": "APROVADO"},
            {"id": 604, "nome": " Nome válido ", "cpf": "44444444444", "status": "APROVADO"},
        ]
        with tempfile.TemporaryDirectory() as temp:
            pasta = Path(temp)
            self.preparar_projeto(pasta, dados)
            resultado = self.executar_aplicacao(pasta)
            self.assertEqual(resultado.returncode, 0, resultado.stderr)
            registros = self.ler_csv(pasta / "aprovados.csv")
            self.assertEqual([r["id"] for r in registros], ["604"])
            self.assertEqual(registros[0]["nome"], "Nome válido")
            log = (pasta / "processamento.log").read_text(encoding="utf-8")
            self.assertIn("campo nome inválido", log)

    def test_execucao_a_partir_de_outra_pasta(self):
        with tempfile.TemporaryDirectory() as temp:
            raiz = Path(temp)
            projeto = raiz / "projeto"
            projeto.mkdir()
            outra_pasta = raiz / "outra_pasta"
            outra_pasta.mkdir()
            self.preparar_projeto(projeto, [
                {"id": 505, "nome": "Teste de caminho", "cpf": "12345678900", "status": "APROVADO"}
            ])
            resultado = self.executar_aplicacao(projeto, outra_pasta)
            self.assertEqual(resultado.returncode, 0, resultado.stderr)
            self.assertTrue((projeto / "aprovados.csv").exists())
            self.assertTrue((projeto / "processamento.log").exists())
            self.assertFalse((outra_pasta / "aprovados.csv").exists())
            self.assertFalse((outra_pasta / "processamento.log").exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
