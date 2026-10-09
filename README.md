
# teste-sicredi
Projeto desenvolvido como parte do teste técnico para a vaga de Assistente de Desenvolvimento de Sistemas do Sicredi. O objetivo é aplicar conceitos de programação, organização de código e testes automatizados, contribuindo para a qualidade, confiabilidade e manutenção do software.
=======
# Processamento de solicitações em Python

Este projeto foi desenvolvido para o teste técnico de Assistente de Desenvolvimento de Sistemas. A aplicação lê solicitações de um arquivo JSON, aplica as regras de seleção definidas no desafio e gera um CSV com os registros aprovados. Também mantém um log para facilitar a conferência da execução.

## O que o programa faz

- Lê os dados de `solicitacoes.json`.
- Seleciona registros cujo status seja exatamente `APROVADO`.
- Ignora registros com CPF nulo ou vazio.
- Gera `aprovados.csv` com as colunas `id`, `nome` e `cpf`.
- Registra informações do processamento e ocorrências em `processamento.log`.
- Trata problemas como arquivo ausente, JSON inválido, estrutura inesperada e falhas na geração do CSV.

O CPF é tratado como texto para preservar o valor recebido. A aplicação não valida os dígitos verificadores do CPF, pois essa verificação não faz parte das regras consideradas neste desafio.

## Tecnologias

- Python 3.10 ou superior
- Bibliotecas nativas: `csv`, `json`, `logging` e `unittest`

Não é necessário instalar dependências externas.

## Estrutura do projeto

```text
teste-sicredi/
├── main.py
├── test_main.py
├── solicitacoes.json
├── README.md
├── aprovados.csv
└── processamento.log
```

`aprovados.csv` e `processamento.log` são gerados durante a execução. Caso ainda não existam, serão criados pelo programa conforme o comportamento implementado.

## Como executar

1. Tenha o Python 3.10 ou superior instalado.
2. Abra o terminal na pasta do projeto.
3. Execute:

```powershell
python main.py
```
Get-Content aprovados.csv

Get-Content processamento.log
No Windows, também é possível usar `py main.py`.

Ao terminar, confira os arquivos `aprovados.csv` e `processamento.log` na pasta do projeto.

## Como executar os testes automatizados

Os testes utilizam o `unittest`, que já faz parte do Python. Na raiz do projeto, execute:

```powershell
python -m unittest -v test_main.py
```

No Windows, também é possível usar:

```powershell
py -m unittest -v test_main.py
```

O terminal mostra quais testes foram executados e o resultado de cada um. A mensagem `OK` indica que os testes executados terminaram sem falhas.

Os cenários descritos para os testes incluem:

- processamento dos dados de entrada;
- geração do CSV;
- exportação somente de registros aprovados;
- descarte de registros com CPF vazio;
- tratamento de JSON inválido;
- tratamento de registros incompletos;
- preservação dos registros válidos quando outros registros precisam ser ignorados.

## Regras de seleção

Um registro é exportado quando:

1. O campo `status` é exatamente `APROVADO`.
2. O CPF não é nulo nem vazio.

Os registros que não atendem a esses critérios não devem aparecer no CSV final. As ocorrências relevantes são registradas no log.

## Resultado esperado para os dados do desafio

De acordo com as regras descritas para o arquivo de entrada fornecido, são esperados 7 registros no CSV, com os IDs `1, 4, 6, 9, 12, 13 e 15`.

Depois de executar o programa, confira se esses registros aparecem no `aprovados.csv` e se as colunas estão na ordem `id`, `nome`, `cpf`.

## Organização do código

O processamento foi dividido em funções para separar as responsabilidades: carregar os dados, aplicar as regras, gerar o CSV e coordenar a execução. Essa organização facilita a leitura, a manutenção e a verificação das regras por meio dos testes automatizados.

A solução roda localmente a partir de um arquivo JSON. A referência a BPM é uma possibilidade de uso dessa lógica em um fluxo maior; o projeto não integra diretamente uma plataforma BPM.

