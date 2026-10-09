# Testes automatizados

O projeto utiliza o `unittest`, biblioteca nativa do Python. Não é necessário instalar dependências externas.

## Executar os testes

Na raiz do projeto:

```powershell
python -m unittest -v test_main.py
```

No Windows, também pode ser usado:

```powershell
py -m unittest -v test_main.py
```

## O que é validado

Os testes verificam:

- processamento do arquivo JSON real;
- geração do `aprovados.csv`;
- exportação apenas de registros com `status = APROVADO`;
- rejeição de registros com CPF vazio;
- tratamento de JSON inválido;
- tratamento de registros incompletos;
- preservação dos registros válidos durante o processamento.

O arquivo de entrada fornecido pelo teste contém 15 solicitações. Pelas regras do desafio, 7 registros devem ser exportados: IDs `1, 4, 6, 9, 12, 13 e 15`.

## Estrutura

```text
teste-sicredi/
├── main.py
├── solicitacoes.json
├── test_main.py
├── README.md
├── aprovados.csv
└── processamento.log
```
