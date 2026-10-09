
# Teste Técnico Sicredi: Processamento de Solicitações em Python

Projeto desenvolvido para o teste técnico da vaga de Assistente de Desenvolvimento de Sistemas do Sicredi. A aplicação lê solicitações de cadastro em JSON, seleciona os registros aprovados que possuem CPF preenchido e gera um arquivo CSV para utilização por outras áreas. O processamento e as ocorrências são registrados em um arquivo de log, e testes automatizados verificam os principais cenários de funcionamento e erro.

Funcionalidades

Leitura dos registros de `solicitacoes.json`.
Seleção de solicitações com status `APROVADO` e CPF não nulo nem vazio.
Geração do arquivo `aprovados.csv`, com as colunas `id`, `nome` e `cpf`.
Registro do início e do fim do processamento, dos totais e das ocorrências em `processamento.log`.
Tratamento de situações como arquivo não encontrado, JSON inválido, registros incompletos e erros na geração do CSV.
Testes automatizados para verificar o comportamento da aplicação.
O CPF é tratado como texto, preservando o valor recebido. A validação dos dígitos verificadores não é realizada, pois não faz parte dos requisitos do desafio.
Tecnologias e pré-requisitos
Python 3.10 ou superior.
Bibliotecas nativas do Python, incluindo `csv`, `json`, `logging` e `unittest`.
Não é necessário instalar bibliotecas externas.

Estrutura do projeto

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
Os arquivos `aprovados.csv` e `processamento.log` são gerados durante a execução. Eles também podem estar presentes no repositório como exemplos do resultado produzido.

Como executar

Instale o Python 3.10 ou superior.
Abra o terminal na pasta do projeto.
Execute:
```powershell
python main.py
```
No Windows, se o comando `python` não estiver disponível, tente:
```powershell
py main.py
```
Após a execução, confira os arquivos gerados no diretório do projeto. Para visualizar seu conteúdo no PowerShell, use:
```powershell
Get-Content aprovados.csv
Get-Content processamento.log
```

Como executar os testes automatizados

Os testes usam o módulo `unittest`, incluído na instalação padrão do Python. Na pasta do projeto, execute:
```powershell
python -m unittest -v test_main.py
```
No Windows, também é possível executar:
```powershell
py -m unittest -v test_main.py
```
O terminal apresenta o resultado de cada teste. A mensagem `OK` indica que os testes executados terminaram sem falhas.
Os testes verificam cenários de processamento dos dados, geração do CSV, seleção de registros aprovados, CPF vazio, JSON inválido e registros incompletos. Consulte `README_TESTES.md` para informações adicionais sobre os testes.

Regras de seleção

Um registro é exportado somente quando atende aos dois critérios:
O campo `status` é igual a `APROVADO`.
O campo `cpf` está presente e não é nulo nem vazio.
Registros que não atendem aos critérios ou que apresentam problemas de estrutura são ignorados conforme as regras implementadas, e as ocorrências relevantes são registradas no log. Um registro inválido não deve interromper o processamento dos demais registros válidos.

Resultado esperado para o arquivo fornecido

Para os dados de exemplo incluídos no desafio, são esperados 7 registros no arquivo `aprovados.csv`, com os IDs `1, 4, 6, 9, 12, 13 e 15`.
O CSV utiliza vírgula como separador e é gravado em UTF-8, com as colunas na ordem `id`, `nome`, `cpf`.

Organização da solução

O código foi organizado em funções para separar responsabilidades, como leitura dos dados, aplicação dos critérios, geração do CSV e coordenação do processamento. Essa divisão facilita a leitura, a manutenção e a realização de testes.

Possível integração com um processo BPM

Em um processo de BPM (Business Process Management), os dados poderiam ser recebidos por um formulário conectado ao fluxo de trabalho. Após o envio, o sistema registraria a solicitação e a encaminharia para a etapa de aprovação. Quando uma pessoa responsável aprovasse o cadastro, o processo chamaria uma rotina equivalente à deste projeto para validar os campos necessários e incluir o registro no CSV. Solicitações pendentes ou reprovadas não seriam exportadas. O fluxo também poderia registrar o responsável e a data da decisão, manter histórico das etapas e notificar a área responsável em caso de falha.
Esta implementação é executada localmente a partir de um arquivo JSON; ela não integra diretamente uma plataforma BPM.

A documentação oficial do Python pode ser consultada para esclarecer o uso de módulos como `csv`, `json`, `logging` e `unittest`. O ChatGPT foi utilizado como apoio na revisão e organização da documentação. A implementação, as decisões adotadas e os resultados devem ser compreendidos e conferidos pela pessoa candidata, que poderá explicar o funcionamento do código durante a entrevista.
