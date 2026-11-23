# NutriVision
- Repositório do projeto integrado do curso de Ciência da Computação
- 1° Semestre / 2026

## Desenvolvedores
- Murilo Montoro Marqui
- Álvaro Gruli

## Ideia principal
A ideia seria um sistema para nutricionistas acompanharem a evolução dos pacientes ao longo do tempo, em vez de apenas armazenar consultas.

## NutriMetrics: gerador de dados nutricionais

Esta seção acrescenta o simulador NutriMetrics ao README original, cujo título histórico NutriVision e créditos foram preservados. O projeto simula registros de refeições de pacientes inteiramente fictícios para futura análise estatística. Esta entrega contém o gerador Python, o CSV de exemplo e sua validação.

O PDF **P1 – DevOps e Infraestrutura Privada**, seção 5.1, orienta o simulador: execução por comando, mínimo de 10 registros, identificador, informação temporal, variáveis relevantes e armazenamento estruturado. A avaliação completa também exige infraestrutura e demonstração em VM. Essas partes continuam pendentes para uma etapa posterior solicitada pela equipe. Veja `docs/analise_requisitos.md`.

## Executar no Ubuntu

Requer **Python 3.10 ou superior**. Não há bibliotecas externas para instalar; `requirements.txt` registra essa decisão.

```bash
sudo apt update
sudo apt install -y python3
cd NutriMetrics
python3 --version
python3 simulador/gerador_dados.py --quantidade 1000 --seed 42
```

O comando acrescenta 1.000 registros a `dados/dados_nutricionais.csv`. O diretório é criado automaticamente. Sem `--quantidade`, são gerados 10 registros. No Windows, utilize `python` no lugar de `python3`, caso esse seja o comando do seu interpretador instalado.

```bash
# Mais dados no mesmo CSV, preservando os anteriores:
python3 simulador/gerador_dados.py --quantidade 10000 --seed 43

# Período e população explícitos; o caminho relativo depende do diretório atual:
python3 simulador/gerador_dados.py --quantidade 1000 \
  --saida dados/experimento.csv --seed 42 --pacientes 20 \
  --data-inicio 2026-01-01 --data-fim 2026-01-31

# Ajuda:
python3 simulador/gerador_dados.py --help
```

O destino padrão é relativo à raiz do projeto, calculado a partir do script, mesmo se o programa for chamado de outra pasta. Um `--saida` relativo é resolvido a partir da pasta de onde o comando é executado. Caminhos absolutos também são aceitos.

| Parâmetro | Padrão | Regra |
| --- | --- | --- |
| `--quantidade` | `10` | Inteiro maior ou igual a 10 |
| `--saida` | `dados/dados_nutricionais.csv` na raiz do projeto | CSV a criar ou complementar |
| `--seed` | Sorteada e mostrada no terminal | Inteiro para reproduzir os atributos sintéticos |
| `--pacientes` | `100` | População possível; inteiro positivo |
| `--data-inicio` | 30 dias antes do dia atual | Data `AAAA-MM-DD` |
| `--data-fim` | Ontem | Data `AAAA-MM-DD`, anterior ao dia atual em UTC-03:00 |

As datas inicial e final são inclusivas e configuráveis independentemente. Ao definir somente uma delas, a outra mantém seu padrão; informe ambas para evitar intervalos indesejados. Datas invertidas, inválidas ou que incluam hoje/futuro são recusadas. Refeições são distribuídas uniformemente entre os dias do período.

## Formato e dicionário dos dados

Cada linha representa uma refeição sintética. O CSV usa UTF-8 sem BOM, vírgula entre colunas, ponto decimal, cabeçalho único em snake_case e datas ISO 8601 com fuso explícito. Há 20 colunas, sem campos obrigatórios vazios.

| Coluna | Tipo / unidade | Significado |
| --- | --- | --- |
| `registro_id` | Inteiro positivo | Identificador crescente, único dentro deste CSV |
| `paciente_id` | Texto | Identificador fictício derivado da versão, seed e índice do paciente |
| `idade` | Inteiro, anos | Idade de referência da população adulta sintética, 18 a 80 |
| `peso_kg` | Decimal, kg | Peso de referência, derivado de altura e IMC sorteado |
| `altura_m` | Decimal, m | Altura de referência, de 1,45 a 2,00 |
| `imc` | Decimal, kg/m² | Peso exportado dividido pela altura exportada ao quadrado |
| `objetivo_nutricional` | Categoria | `reducao_peso`, `manutencao` ou `ganho_massa` |
| `nivel_atividade_fisica` | Categoria | `sedentario`, `leve`, `moderado` ou `intenso` |
| `tipo_refeicao` | Categoria | Café, lanche da manhã, almoço, lanche da tarde, jantar ou ceia |
| `alimento_principal` | Texto | Nome do preparo completo, por exemplo `arroz_feijao_frango_e_legumes` |
| `quantidade_g` | Decimal, g | Massa consumida do preparo completo |
| `calorias_kcal` | Decimal, kcal | Energia calculada a partir dos macronutrientes exportados |
| `proteinas_g` | Decimal, g | Proteínas na porção |
| `carboidratos_g` | Decimal, g | Carboidratos na porção |
| `gorduras_g` | Decimal, g | Gorduras na porção |
| `fibras_g` | Decimal, g | Fibras na porção, limitadas pelos carboidratos |
| `agua_ml` | Inteiro, mL | Água consumida junto à refeição, 0 a 600, em passos de 50 |
| `data_hora_refeicao` | ISO 8601 | Momento simulado, com deslocamento fixo UTC-03:00 |
| `data_hora_geracao` | ISO 8601 | Momento real da geração do lote em UTC |
| `versao_gerador` | Texto | Versão das regras da simulação, atualmente `1` |

## Regras de consistência e decisões técnicas

1. **Pacientes estáveis:** cada combinação de versão, seed e índice produz o mesmo perfil por SHA-256 e um gerador pseudoaleatório independente. O perfil não depende da quantidade de refeições nem do tamanho da população. Com a mesma seed, o paciente reaparece com os mesmos dados entre execuções. Seeds diferentes geram populações diferentes. Não é necessário armazenar cadastro auxiliar ou manter pacientes em memória.
2. **IMC:** primeiro são arredondados peso e altura; depois é calculado `peso_kg / altura_m²`, com duas casas decimais. A faixa sorteada é de 18 a 38; o arredondamento do peso pode causar variação residual de 0,01. Peso fica aproximadamente entre 38 e 152 kg.
3. **Composição:** cada preparo possui proporções didáticas fixas por 100 g. Todos os nutrientes são proporcionais à massa consumida. A porção depende do tipo de refeição, objetivo e atividade. Maior IMC aumenta a probabilidade do objetivo de redução de peso apenas para criar uma associação explorável na simulação.
4. **Energia:** adota-se a convenção simplificada `4 × proteínas + 4 × carboidratos + 9 × gorduras`. O cálculo utiliza `Decimal` e os macros já arredondados do CSV; a igualdade pode ser conferida exatamente com aritmética decimal. Não há termo adicional para fibras neste modelo.
5. **Horários:** café 06:00–08:59; lanche da manhã 09:00–10:59; almoço 11:30–14:29; lanche da tarde 15:00–17:29; jantar 18:00–20:59; ceia 21:00–22:59. Todos os horários de refeição usam um deslocamento fixo de UTC-03:00, sem simulação de horário de verão histórico.
6. **IDs e append:** antes de acrescentar, o programa lê o CSV por streaming, confere cabeçalho, preenchimento estrutural e IDs positivos estritamente crescentes; o próximo ID é o último mais um. Não carrega os registros existentes nem os novos em uma lista. O custo de tempo é O(registros existentes + novos), com memória O(1) em relação ao número de registros.
7. **Preservação:** um bloqueio `.lock` impede dois processos deste gerador de escreverem no mesmo destino simultaneamente. Exceções capturáveis durante a gravação revertem o tamanho ao estado anterior. CSV incompatível ou incompleto é recusado sem sobrescrever seu conteúdo. O bloqueio pressupõe sistema de arquivos local e que os escritores respeitem o protocolo.

Os coeficientes e as associações são hipóteses didáticas inventadas, não dados clínicos, recomendações alimentares ou valores obtidos de uma tabela nutricional oficial. Não existem nomes, documentos ou pacientes reais.

O modelo sorteia refeições observadas de forma independente. Não representa um diário completo, não garante uma refeição de cada tipo por paciente/dia e permite coincidências de paciente e horário. Água corresponde somente à refeição, não ao consumo diário. Peso, idade, altura, objetivo e atividade são atributos de referência fixos da coorte; evolução clínica, aniversários e alterações de peso não são modelados.

### Reprodutibilidade

Com a mesma versão do Python, versão do gerador, seed, população e período, os atributos sintéticos e a ordem de sorteio se repetem. `data_hora_geracao` registra a execução real; `registro_id` continua a sequência do arquivo de destino. Por isso, a mesma seed em execuções reais não implica CSVs idênticos byte a byte. O teste de reprodução congela também o relógio e utiliza dois arquivos inicialmente vazios.

Repetir uma seed acrescenta novas linhas com novos IDs, mas pode repetir o conteúdo sintético das refeições. Para ampliar a diversidade, escolha outra seed. Os IDs de registros são exclusivos **por arquivo**: para acumular um conjunto sem colisões, use sempre o mesmo CSV. Ao unir CSVs independentes, será necessário distinguir a origem ou renumerar os registros. Uma migração de esquema ou das regras de pacientes deve utilizar outro CSV ou uma migração explícita.

### Falhas e retomada

Uma interrupção forçada do processo, queda de energia ou falha de disco pode deixar lote parcial e bloqueio residual. Não há garantia transacional contra essas falhas. Preserve uma cópia do CSV, verifique seu final e remova somente o `.lock` associado se nenhum processo estiver ativo. Linhas incompletas são recusadas na próxima execução; qualquer reparo de um arquivo danificado deve ser feito explicitamente após backup. Não remova dados nem bloqueios de um processo em execução.

## Testes e exemplo

Na raiz do projeto:

```bash
python3 -m unittest discover -s testes -v
```

São 18 testes com arquivos temporários: lotes de 10, 1.000 e 10.000 registros, criação de diretórios, cabeçalho, preservação do conteúdo, IDs, perfis, IMC, nutrientes, limites, datas, semente, erros de parâmetros, CSV incompatível, truncamento, duplicatas existentes, arquivo vazio, quebra de linha final, concorrência, reversão após erro e importação analítica com SQLite da biblioteca padrão.

O CSV `dados/exemplo_dados.csv` foi produzido com:

```bash
python3 simulador/gerador_dados.py --quantidade 1000 \
  --saida dados/exemplo_dados.csv --seed 42 --pacientes 20 \
  --data-inicio 2026-01-01 --data-fim 2026-01-31
```

Esse comando foi executado uma vez sobre um destino inexistente. Se executado novamente, acrescentará mais 1.000 linhas ao exemplo. Para um novo experimento sem misturar lotes, escolha outro `--saida`. `docs/validacao.md` registra o ambiente e os resultados reais desta entrega. A leitura com `csv.DictReader` e a conversão numérica para SQLite foram testadas; a importação em R ainda não foi executada.

## Organização

```text
NutriMetrics/
├── simulador/
│   ├── __init__.py
│   ├── gerador_dados.py
│   └── requirements.txt
├── dados/
│   └── exemplo_dados.csv
├── testes/
│   └── test_gerador_dados.py
├── docs/
│   ├── analise_requisitos.md
│   └── validacao.md
├── .gitignore
└── README.md
```

O `.gitignore` exclui CSVs de execução e preserva o exemplo. Também exclui ambientes virtuais, arquivos locais de estado, variáveis privadas e chaves comuns. O diretório `infraestrutura/` será criado na etapa de implantação, com os arquivos reais de OpenTofu, cloud-init e Ansible.

## Integração futura com a VM

A futura automação deverá instalar `python3` >= 3.10, criar o diretório do projeto e o diretório de dados com permissão para o usuário executor, transferir `simulador/` e executar o comando. A aplicação não precisa de rede, servidor HTTP, Docker, serviço de banco de dados ou caminho exclusivo da máquina hospedeira.

Quando a VM e o usuário já estiverem configurados, a transferência e a execução poderão seguir este modelo, substituindo `USUARIO` e `IP_DA_VM` pelos valores reais:

```bash
ssh USUARIO@IP_DA_VM 'mkdir -p ~/NutriMetrics/dados'
scp -r simulador USUARIO@IP_DA_VM:~/NutriMetrics/
ssh USUARIO@IP_DA_VM 'python3 ~/NutriMetrics/simulador/gerador_dados.py --quantidade 1000 --seed 42'
ssh USUARIO@IP_DA_VM 'head -n 3 ~/NutriMetrics/dados/dados_nutricionais.csv'
```

Esses comandos são orientações para uma VM futura; não foram executados nesta entrega. O Ansible deverá conservar o CSV existente nas reimplantações. Não copiar os arquivos de estado presentes nos materiais de referência para o repositório da equipe. A demonstração final exigirá executar novamente na VM e guardar evidências reais do provisionamento, configuração, transferência e geração de dados.

## Adicionar ao repositório

O pacote contém os arquivos desta etapa, sem `.git` e sem materiais de referência. Copie seu conteúdo para a raiz do clone local do NutriMetrics, revise o README ampliado e execute os testes. Depois, versione os arquivos com Git pelo fluxo usado pela equipe. Nenhuma alteração foi enviada ao GitHub automaticamente.

## Geração automática a cada 5 minutos

Na pasta NutriMetrics, ligue com a quantidade desejada por rodada:

```powershell
python simulador/controle_gerador.py ligar --quantidade 100
```

A primeira rodada é imediata. Depois, são gerados 100 registros a cada 5 minutos.
Mantenha o computador ligado e o terminal aberto. Não inicia automaticamente com o Windows.
Se o computador dormir, as rodadas perdidas não são recuperadas.

Para desligar, use Ctrl+C no terminal do gerador ou execute em outro terminal:

```powershell
python simulador/controle_gerador.py desligar
python simulador/controle_gerador.py status
```

O comando desligar solicita a parada após a rodada em andamento. Use status para confirmar.
Para mudar a quantidade, desligue, aguarde a confirmação e ligue novamente com outro valor.
O mínimo continua sendo 10 registros por rodada.

O arquivo padrão continua sendo dados/dados_nutricionais.csv, sem apagar registros anteriores.
Você pode escolher outro arquivo com --saida dados/outro.csv; informe o mesmo --saida ao consultar ou desligar.
A pasta .controle ao lado do CSV guarda informações de execução. Não a remova enquanto o gerador estiver ligado.
O bloqueio protege processos locais; não execute simultaneamente em dois computadores pelo OneDrive.
Cada rodada sorteia uma nova semente e uma nova população fictícia. As refeições continuam simuladas nos últimos 30 dias completos, como no gerador original.

Para testar rapidamente sem esperar 5 minutos:

```powershell
python simulador/controle_gerador.py ligar --quantidade 10 --intervalo-segundos 2 --saida dados/teste_periodico.csv
```

Desligue esse teste com Ctrl+C. O intervalo padrão, sem essa opção, é 300 segundos.
Validação realizada: repetição com intervalo reduzido, quantidade, IDs únicos, status, bloqueio de uma segunda execução, parada, reinício com nova quantidade e preservação do CSV. Não foi aguardado um ciclo real de cinco minutos.
