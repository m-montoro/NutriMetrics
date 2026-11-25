# NutriMetrics

Projeto integrado do curso de Ciência da Computação, desenvolvido no 1º semestre de 2026 por 
**Murilo Montoro Marqui** RA: 26001976 
**Álvaro Gruli** RA: 26001991

O NutriMetrics implementa a etapa de simulação de refeições para análise de dados. O Python gera os registros e o R consolida as informações em uma tabela por paciente. Todos os pacientes, refeições e indicadores corporais são fictícios e destinados a uso acadêmico.

## Requisitos

- **Python 3.10 ou superior** para gerar dados. O simulador usa a biblioteca padrão do Python.
- **R com `Rscript` disponível** para executar o tratamento pela linha de comando ou acompanhar cada rodada com `--filtrar`. Também é possível executar o tratamento manualmente no RStudio.
- **Tkinter** para usar a interface gráfica. O atalho `.bat` é destinado ao Windows.

## Arquivos de dados

| Arquivo | Conteúdo |
| --- | --- |
| `dados/dados_nutricionais.csv` | CSV bruto gerado pelo Python. Cada linha representa uma refeição. Novas rodadas acrescentam registros ao arquivo. |
| `dados/dados_organizados.csv` | CSV consolidado pelo R. Contém uma linha por paciente e as 15 colunas do modelo `Pasta1.xlsx`. A saída é atualizada a cada execução bem-sucedida. |

O CSV bruto usa UTF-8 sem BOM, vírgula entre colunas, ponto decimal e datas ISO 8601 com fuso explícito. O CSV organizado usa ponto e vírgula entre colunas e vírgula decimal para facilitar a abertura no Excel em português. Feche o arquivo de saída no Excel antes de atualizá-lo.

## Gerar um lote

Na raiz do projeto, execute o comando abaixo no Ubuntu. No Windows, use `python` no lugar de `python3` se esse for o comando do seu interpretador.

```bash
python3 simulador/gerador_dados.py --quantidade 1000 --seed 42
```

O comando acrescenta 1.000 refeições a `dados/dados_nutricionais.csv`. O diretório de saída é criado automaticamente quando necessário.

Para gerar um experimento separado, indique outro destino, a população e o período:

```bash
python3 simulador/gerador_dados.py --quantidade 1000 \
  --saida dados/experimento.csv --seed 42 --pacientes 20 \
  --data-inicio 2026-01-01 --data-fim 2026-01-31
```

| Parâmetro | Padrão | Uso |
| --- | --- | --- |
| `--quantidade` | `10` | Número de refeições a gerar, com mínimo de 10. |
| `--saida` | `dados/dados_nutricionais.csv` na raiz do projeto | Caminho do CSV. Um destino informado por caminho relativo é resolvido a partir do diretório atual. |
| `--seed` | Sorteada e exibida no terminal | Inteiro que permite reproduzir os atributos sintéticos. |
| `--pacientes` | `100` | Tamanho da população fictícia disponível para sorteio. |
| `--data-inicio` | 30 dias antes da data atual | Início inclusivo do período, em `AAAA-MM-DD`. |
| `--data-fim` | Ontem | Fim inclusivo do período, anterior ao dia atual em UTC−03:00. |

As duas datas podem ser informadas juntas para definir o período completo. O gerador recusa datas inválidas, intervalos invertidos e períodos que incluam o dia atual ou datas futuras.

## Gerar dados automaticamente

A primeira rodada ocorre assim que o gerador é ligado. O intervalo padrão entre rodadas é de cinco minutos. Mantenha o terminal aberto durante a execução.

```bash
python3 simulador/controle_gerador.py ligar --quantidade 100
```

Para consultar ou solicitar a parada, abra outro terminal na raiz do projeto:

```bash
python3 simulador/controle_gerador.py status
python3 simulador/controle_gerador.py desligar
```

Também é possível usar `Ctrl+C` no terminal do gerador. O comando `desligar` solicita a parada após a rodada em andamento. Confirme com `status` antes de reiniciar com outra quantidade.

Para testar rapidamente em um CSV separado:

```bash
python3 simulador/controle_gerador.py ligar \
  --quantidade 10 --intervalo-segundos 2 --saida dados/teste_periodico.csv
```

Ao usar `--saida`, passe o mesmo caminho aos comandos `status` e `desligar`. Cada rodada usa uma nova semente. A pasta `.controle` associada ao CSV guarda o estado da execução e deve ser mantida enquanto o gerador estiver ativo. Execute apenas uma instância por CSV, especialmente em pastas sincronizadas entre computadores.

## Organizar os dados com R

Para gerar refeições e atualizar o CSV organizado após cada rodada:

```bash
python3 simulador/controle_gerador.py ligar --quantidade 100 --filtrar
```

Se `Rscript` estiver instalado fora dos caminhos detectados pelo programa, informe seu caminho com `--rscript`.

Para executar somente o tratamento, use um dos comandos abaixo na raiz do projeto.

**Terminal**

```bash
Rscript tratamento/executar_filtros.R
```

**Console do RStudio**

```r
source("tratamento/executar_filtros.R", encoding = "UTF-8")
```

O tratamento consolida as refeições em uma linha por paciente. Se houver registros inválidos, os motivos são exibidos no terminal e o resultado anterior é preservado.

### Regras do CSV organizado

- A avaliação corporal é simulada. Massa magra e massa gorda somam o peso. A condição física é classificada por faixas diferentes para homens e mulheres.
- O total de água em litros, `total_agua_l`, é calculado por `peso_kg × 35 / 1.000`. O campo `agua_ml` do CSV bruto representa a água consumida junto a uma refeição.
- O campo `total_calorias_basal` contém a taxa metabólica basal (TMB) mais um adicional de 0, 150, 300 ou 500 kcal.
- A TMB é calculada por `10 × peso_kg + 6,25 × altura_cm − 5 × idade`, com ajuste de `+5` para homens ou `−161` para mulheres.
- O número de refeições livres é um inteiro fictício de 0 a 100 por paciente, sem período definido. A data da consulta fica fora das 15 colunas do modelo.

## Interface gráfica no Windows

Abra `Abrir gerador.bat`, escolha a quantidade e clique em **Ligar**. A interface executa o tratamento em R a cada rodada de cinco minutos. Use **Desligar** e aguarde o término da rodada atual antes de mudar a quantidade. O botão **Abrir pasta dos CSVs** abre a pasta dos arquivos gerados.

## Dicionário do CSV bruto

O arquivo possui 23 colunas. Cada linha corresponde a uma refeição sintética.

| Coluna | Significado |
| --- | --- |
| `registro_id` | Identificador inteiro, positivo e crescente dentro do arquivo. |
| `paciente_id` | Identificador fictício derivado da versão do gerador, da semente e do índice do paciente. |
| `idade` | Idade de referência em anos. |
| `peso_kg` | Peso de referência em quilogramas. |
| `altura_m` | Altura de referência em metros. |
| `imc` | Índice calculado com o peso e a altura exportados. |
| `objetivo_nutricional` | Redução de peso, manutenção ou ganho de massa. |
| `nivel_atividade_fisica` | Nível de atividade física do perfil simulado. |
| `sexo` | Sexo do paciente fictício. |
| `n_refeicoes_livres` | Número fictício de refeições livres atribuído ao paciente. |
| `atividade_fisica` | Atividade física registrada no perfil simulado. |
| `tipo_refeicao` | Café, lanche da manhã, almoço, lanche da tarde, jantar ou ceia. |
| `alimento_principal` | Nome do preparo consumido. |
| `quantidade_g` | Massa da porção em gramas. |
| `calorias_kcal` | Energia da porção em quilocalorias. |
| `proteinas_g` | Proteínas da porção em gramas. |
| `carboidratos_g` | Carboidratos da porção em gramas. |
| `gorduras_g` | Gorduras da porção em gramas. |
| `fibras_g` | Fibras da porção em gramas. |
| `agua_ml` | Água consumida junto à refeição, em mililitros. |
| `data_hora_refeicao` | Horário simulado da refeição em UTC−03:00. |
| `data_hora_geracao` | Horário real de geração do lote em UTC. |
| `versao_gerador` | Versão das regras de simulação. |

### Consistência e preservação dos dados

O gerador calcula o IMC com o peso e a altura exportados. A energia segue a fórmula didática `4 × proteínas + 4 × carboidratos + 9 × gorduras`, usando os macronutrientes arredondados. Os perfis dos pacientes são estáveis para a mesma combinação de versão, semente e índice.

Com a mesma configuração e semente, os atributos sintéticos podem ser reproduzidos. O horário real da geração e a sequência de IDs dependem da execução e do arquivo de destino. Rodar novamente o mesmo comando pode acrescentar refeições sintéticas repetidas com novos IDs.

Antes de acrescentar registros, o simulador confere o cabeçalho, a estrutura das linhas e a sequência de IDs. Um bloqueio local impede gravações simultâneas pelo gerador. CSVs incompatíveis ou truncados são recusados. Se houver interrupção forçada, faça uma cópia do CSV e verifique as últimas linhas antes de retomar. Remova um bloqueio residual somente após confirmar que o processo terminou.

## Testes

Na raiz do projeto:

```bash
python3 -m unittest discover -s testes -v
Rscript testes/test_csv_unico.R
```

A suíte Python inclui 18 testes de geração, consistência, reprodutibilidade, acréscimo de registros, concorrência, reversão após erro e importação em SQLite. Os 18 passaram em Windows com Python 3.12. Também foi verificado o ciclo `ligar`, gerar 10 registros, consultar `status` e `desligar` com um CSV temporário. A suíte R e a execução com `--filtrar` no Ubuntu ainda precisam de validação para esta versão.

## Organização do projeto

```text
NutriMetrics/
├── Abrir gerador.bat
├── dados/          # CSVs de entrada e saída gerados durante a execução
├── docs/           # Análise de requisitos
├── simulador/      # Gerador, controlador e interface Python
├── testes/         # Testes Python e R
├── tratamento/     # Scripts de tratamento em R
├── .gitignore
└── README.md
```

A documentação dos requisitos do simulador para a avaliação de infraestrutura está em `docs/analise_requisitos.md`. Os CSVs de execução, os arquivos de estado e o cache Python ficam fora do controle de versão.
