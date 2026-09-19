# Organizador de Anexos por Regras

> Este projeto foi gerado automaticamente por IA e revisado por um agente automatizado, nao por uma pessoa. Leia o codigo antes de usar.

## Descrição

Automação local de linha de comando para organizar arquivos de uma pasta de entrada conforme regras declarativas em YAML. As regras podem filtrar por extensão, prefixo do nome e idade mínima baseada na data de modificação.

Por padrão, a ferramenta apenas simula as movimentações. Com `--execute`, ela move os arquivos para os destinos configurados e grava um relatório JSON com as ações planejadas ou realizadas e os arquivos que não corresponderam a nenhuma regra.

## Objetivo

Reduzir a triagem manual de arquivos locais por meio de regras determinísticas, mantendo um registro auditável das ações planejadas ou executadas.

## Como funciona

1. A CLI recebe uma pasta de entrada, um arquivo YAML de regras e o caminho para o relatório JSON.
2. O arquivo YAML é validado antes do processamento.
3. A aplicação examina somente os arquivos regulares no nível imediato da pasta de entrada, em ordem de nome.
4. Diretórios são ignorados, assim como o próprio arquivo de relatório quando ele estiver na pasta de entrada.
5. Para cada arquivo, a primeira regra compatível é selecionada.
6. Os critérios definidos em uma mesma regra são combinados com lógica **AND**:
   - `extension`: compara a extensão sem diferenciar maiúsculas e minúsculas;
   - `prefix`: compara o início do nome de forma sensível a maiúsculas e minúsculas;
   - `min_age_days`: exige uma idade mínima, em dias, calculada a partir da data de modificação.
7. Se o destino já existir ou tiver sido reservado durante o mesmo processamento, é usado um sufixo numérico, como `arquivo (1).pdf`.
8. Sem `--execute`, as ações são registradas como planejadas e nenhum arquivo é movido. Com `--execute`, os diretórios de destino são criados quando necessário e os arquivos são movidos.
9. O relatório JSON é gravado ao final do processamento.

## Arquitetura

- `requirements.txt`: arquivo de dependências do projeto.
- `src/organizador_anexos/__init__.py`: define a versão do pacote.
- `src/organizador_anexos/__main__.py`: implementa a interface de linha de comando e o ponto de entrada `python -m organizador_anexos`.
- `src/organizador_anexos/rules.py`: carrega, valida e representa as regras YAML.
- `src/organizador_anexos/organizer.py`: seleciona regras, planeja destinos, resolve colisões e move arquivos quando solicitado.
- `src/organizador_anexos/report.py`: serializa o resultado em JSON UTF-8.
- `tests/conftest.py`: configuração compartilhada dos testes.
- `tests/test_cli.py`: testes da interface de linha de comando.
- `tests/test_organizer.py`: testes da organização de arquivos.
- `tests/test_rules.py`: testes do carregamento e da validação das regras.

## Tecnologias

- Python 3.11+
- PyYAML, para leitura segura do YAML com `yaml.safe_load`
- Biblioteca padrão do Python: `argparse`, `dataclasses`, `datetime`, `json`, `pathlib` e `shutil`
- pytest, fornecido pelo ambiente de execução

## Instalação

Instale as dependências declaradas pelo projeto com:

```bash
python -m pip install -r requirements.txt
```

O pacote está em `src/` e o projeto não possui arquivo de instalação. Por isso, é necessário incluir `src/` no `PYTHONPATH` ao executar o módulo.

## Configuração

A aplicação não lê variáveis de ambiente.

As regras são fornecidas em um arquivo YAML. O documento deve conter **somente** a chave `rules`, cujo valor é uma lista. Cada regra aceita as chaves abaixo:

| Chave | Obrigatória | Descrição |
| --- | --- | --- |
| `name` | Não | Nome da regra registrado no relatório. Quando ausente, recebe `regra-<posição>`. |
| `destination` | Sim | Destino relativo à pasta de entrada. Não pode ser absoluto nem conter `..`. |
| `extension` | Não | Extensão a comparar, como `.pdf`. A comparação não diferencia maiúsculas e minúsculas. |
| `prefix` | Não | Prefixo literal do nome do arquivo. A comparação diferencia maiúsculas e minúsculas. |
| `min_age_days` | Não | Idade mínima de modificação em dias, como número não negativo. |

Chaves desconhecidas, valores de texto vazios e estruturas YAML inválidas são rejeitados. Uma regra sem critérios opcionais corresponde a qualquer arquivo processado.

## Uso

A CLI exige `--input`, `--rules` e `--report`. Sem `--execute`, a execução é uma simulação.

Linux/macOS:

```bash
PYTHONPATH=src python -m organizador_anexos --input <pasta-de-entrada> --rules <arquivo-de-regras.yaml> --report <relatorio.json>
```

Windows (PowerShell):

```powershell
$env:PYTHONPATH="src"; python -m organizador_anexos --input <pasta-de-entrada> --rules <arquivo-de-regras.yaml> --report <relatorio.json>
```

Para efetivar as movimentações, acrescente `--execute`:

Linux/macOS:

```bash
PYTHONPATH=src python -m organizador_anexos --input <pasta-de-entrada> --rules <arquivo-de-regras.yaml> --report <relatorio.json> --execute
```

Windows (PowerShell):

```powershell
$env:PYTHONPATH="src"; python -m organizador_anexos --input <pasta-de-entrada> --rules <arquivo-de-regras.yaml> --report <relatorio.json> --execute
```

Em caso de sucesso, a CLI informa a quantidade de arquivos movidos ou planejados, a quantidade sem regra e o caminho do relatório. Erros de regras inválidas, falha de leitura ou pasta de entrada inexistente são exibidos em português e retornam código diferente de zero.

## Exemplos

Exemplo de arquivo de regras YAML:

```yaml
rules:
  - name: documentos-pdf
    destination: documentos
    extension: .pdf

  - name: anexos-antigos
    destination: arquivos-antigos
    prefix: anexo_
    min_age_days: 30

  - name: demais-arquivos
    destination: outros
```

Neste exemplo:

- arquivos com extensão `.pdf` são direcionados para `documentos`;
- arquivos cujo nome começa com `anexo_` e tenham pelo menos 30 dias de modificação são direcionados para `arquivos-antigos`;
- os demais arquivos correspondem à última regra, que não possui critérios opcionais.

Exemplo de estrutura do relatório gerado:

```json
{
  "mode": "simulation",
  "input": "<caminho-absoluto-da-pasta-de-entrada>",
  "planned_at": "<data-e-hora-em-formato-ISO-8601>",
  "moved_or_planned": [
    {
      "source": "<arquivo-de-origem>",
      "destination": "<destino-planejado>",
      "rule": "documentos-pdf",
      "status": "planned"
    }
  ],
  "unmatched": []
}
```

No modo de execução, `mode` é `execute` e o status das ações movidas é `moved`.

## Testes

Execute a suíte com:

```bash
python -m pytest
```

Os testes usam arquivos temporários e não acessam a rede.

## Limitações

- Apenas arquivos regulares no nível imediato da pasta de entrada são processados; subpastas não são percorridas.
- Os únicos critérios disponíveis são extensão, prefixo e idade mínima de modificação.
- Não há suporte a expressões regulares, tamanho de arquivo, conteúdo ou metadados.
- A primeira regra compatível, conforme a ordem no YAML, sempre vence.
- A ferramenta move arquivos apenas quando `--execute` é informado; ela não implementa cópia de arquivos.
- Não há mecanismo de desfazer movimentações.
- O relatório disponível é JSON; não há tabela Rich nem relatório HTML.
- Os destinos são locais e relativos à pasta de entrada.

## O que foi aprendido

O experimento demonstra práticas para automação local de arquivos com comportamento verificável:

- validação explícita de configuração declarativa antes de alterar arquivos;
- simulação como comportamento padrão;
- prioridade determinística baseada na ordem das regras;
- prevenção de colisões por reserva de destinos durante o planejamento;
- registro estruturado das ações e dos arquivos sem correspondência.

## Possível aplicação na FOX

Pode servir como base para a organização local e auditável de anexos recebidos por equipes da FOX. Um processo externo poderia preparar uma pasta de entrada, executar primeiro a simulação para revisão do relatório e, após validação operacional, realizar a movimentação efetiva.

O relatório JSON também pode ser usado por ferramentas internas que acompanhem ações de organização de arquivos.

## Status

O relatório de testes recebido informa: **passou: True; 8 teste(s) passaram; 8 teste(s) coletado(s)**.
