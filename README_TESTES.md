# Testes automatizados

O projeto utiliza o módulo `unittest`, incluído na biblioteca padrão do Python. Não é necessário instalar dependências externas para executar os testes.

## Como executar

Abra o terminal na pasta raiz do projeto e execute:

```powershell
py -m unittest -v test_main.py
```

Também é possível utilizar:

```powershell
python -m unittest -v test_main.py
```

No Windows, utilize o comando que estiver disponível na instalação do Python.

Ao final da execução, a mensagem `OK` indica que todos os testes executados passaram. Caso apareça `FAILED`, consulte as mensagens do terminal para identificar os testes que precisam de correção.

## Cenários testados

Os testes automatizados verificam os seguintes comportamentos:

- Processamento do arquivo `solicitacoes.json` fornecido com o desafio.
- Geração do arquivo `aprovados.csv` com as colunas `id`, `nome` e `cpf`.
- Exportação somente de registros com status `APROVADO`.
- Rejeição de registros com CPF vazio, nulo ou composto apenas por espaços.
- Tratamento de arquivos JSON com sintaxe inválida.
- Tratamento de JSON válido com estrutura diferente da esperada.
- Tratamento de arquivo de entrada inexistente.
- Tratamento de registros incompletos, sem interromper o processamento dos registros válidos.
- Tratamento de falhas durante a geração do CSV.
- Execução do programa a partir de outra pasta, mantendo os arquivos de entrada e saída no diretório do projeto.

## Resultado esperado para os dados fornecidos

O arquivo original contém 15 solicitações. De acordo com os critérios do desafio, 7 registros devem ser exportados, com os IDs:

`1, 4, 6, 9, 12, 13 e 15`.

O CSV utiliza vírgula como separador e é gravado em UTF-8.

## Estrutura do projeto

```text
teste-sicredi/
├── main.py
├── test_main.py
├── solicitacoes.json
├── README.md
├── README_TESTES.md
├── aprovados.csv
└── processamento.log
```

Os arquivos `aprovados.csv` e `processamento.log` são gerados durante a execução. Eles também podem estar presentes no repositório como exemplos de saída.

## Observações

Os testes utilizam diretórios temporários para isolar os cenários e evitar alterações no arquivo original de solicitações.

O CPF é tratado como texto. Os testes verificam o preenchimento do campo, mas não validam os dígitos verificadores, pois essa validação não faz parte dos requisitos do desafio.

A descrição da possível integração com um processo BPM está no `README.md`. A aplicação atual processa arquivos JSON localmente e não integra diretamente uma plataforma BPM.