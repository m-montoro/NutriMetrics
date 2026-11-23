# Validação executada

Data: 11/11/2026. Ambiente: Windows, Python 3.12.14, biblioteca padrão.

Comando na raiz do pacote:

```bash
python3 -m unittest discover -s testes -v
```

Resultado real da execução final da suíte: **18 testes passaram, 0 falhas, 0 erros**, em 1,230 s. Tempo observado neste ambiente, sem promessa de desempenho em outras máquinas.

A primeira tentativa encontrou restrições de acesso ao diretório temporário do sandbox. A execução foi repetida com a variável de ambiente `TMPDIR` apontando para uma pasta temporária gravável do workspace; a suíte e as regras de validação foram mantidas. Em ambientes comuns, o diretório temporário padrão deve ser suficiente. Se necessário, no Ubuntu:

```bash
mkdir -p /tmp/nutrimetrics-testes
TMPDIR=/tmp/nutrimetrics-testes python3 -m unittest discover -s testes -v
```

## Evidências cobertas

| Verificação | Resultado |
| --- | --- |
| Geração de 10 registros | Passou; diretório, arquivo e cabeçalho criados |
| Geração de 1.000 registros | Passou; campos, categorias, horários e limites conferidos |
| Geração de 10.000 registros | Passou; leitura sequencial e IDs de 1 a 10.000 |
| Segunda execução no mesmo arquivo | Passou; 10 + 1.000 = 1.010 linhas e prefixo anterior preservado byte a byte |
| Unicidade | Passou; IDs consecutivos sem colisão no mesmo CSV |
| Pacientes estáveis | Passou; perfis preservados entre registros, execuções e tamanhos de população |
| IMC | Passou; recomputado dos valores exportados com aritmética decimal |
| Calorias | Passou; igualdade com `4P + 4C + 9G` |
| Ausência de valores inválidos | Passou; preenchimento, finitude, positividade e faixas das variáveis numéricas |
| Datas e horários | Passou; ISO 8601 com fuso, intervalo inclusivo e horário próprio da refeição |
| Reprodução | Passou; seed, relógio e parâmetros fixos produziram arquivos idênticos em destinos vazios |
| CLI | Passou; argumentos, erros e execução a partir de outra pasta |
| CSV incompatível/truncado/duplicado | Passou; recusado com conteúdo preservado |
| Escrita concorrente | Passou; processo separado recusou destino bloqueado |
| Erro durante geração do lote | Passou; falha injetada, conteúdo anterior restaurado e bloqueio removido |
| CSV sem quebra final / vazio | Passou; continuação correta e cabeçalho correto |
| Uso em análise | Passou; CSV lido, tipos numéricos convertidos e 1.000 linhas importadas em SQLite |

O CSV de exemplo foi gerado pelo CLI, com 1.000 registros, seed 42, população possível de 20 pacientes e período de 01/01/2026 a 31/01/2026. O horário de geração no arquivo corresponde à execução real. Não foram usados dados reais.

## Limites da evidência

- Não houve execução em Ubuntu, VM, R ou infraestrutura DevOps. Os comandos para Ubuntu estão documentados e o código usa APIs portáveis da biblioteca padrão.
- O teste de falha cobre uma exceção capturável de geração/escrita, não queda de energia, disco sem possibilidade de recuperação ou encerramento forçado do sistema.
- A escrita e a leitura prévia do gerador são incrementais por construção; o teste de 10.000 linhas verifica funcionamento, não constitui benchmark de Big Data nem medição de memória.
- A unicidade de registros é garantida dentro de um CSV mantido pelo gerador; arquivos independentes iniciam suas próprias sequências.
- A conferência de entrada existente valida estrutura e ordem de IDs, sem auditar novamente toda a semântica nutricional de dados eventualmente editados externamente.
