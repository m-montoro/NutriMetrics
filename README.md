# NutriMetrics

Projeto academico com dados ficticios. As avaliacoes corporais sao simuladas, nao medidas.

## Arquivos de dados

- dados/dados_nutricionais.csv: entrada gerada pelo Python, com as refeicoes acumuladas.
- dados/dados_organizados.csv: resultado do R, com uma linha por paciente e as 15 colunas do modelo Pasta1.xlsx.

O R atualiza o mesmo arquivo a cada execucao. Nao cria lotes ou outros relatorios.
O resultado usa ponto e virgula entre colunas e virgula decimal para o Excel em portugues.
O peso e a altura sao conferidos. A gordura corporal e ficticia. Massa magra e massa gorda somam o peso.
Refeicoes livres sao inteiros ficticios de 0 a 100 por paciente, sem periodo definido. Sexo e atividade sao gerados no CSV bruto.
total_agua_l usa a regra solicitada: peso em kg vezes 35 dividido por 1000, em litros.
A coluna total_calorias_basal contem TMB mais o adicional solicitado (0, 150, 300 ou 500 kcal); portanto nao e apenas a taxa basal.
TMB: 10*peso + 6.25*altura em cm - 5*idade, com +5 para homem e -161 para mulher.
Essas sao regras da simulacao, nao uma prescricao individual.
condicao_fisica usa a tabela fornecida pelo usuario como regra da simulacao, nao como diagnostico.
Homens: abaixo de 6 muito baixo; de 6 ate menos de 14 baixo; de 14 ate menos de 21 ideal; de 21 ate menos de 25 elevado; a partir de 25 obesidade.
Mulheres: abaixo de 14 muito baixo; de 14 ate menos de 21 baixo; de 21 ate menos de 29 ideal; de 29 ate menos de 33 elevado; a partir de 33 obesidade.
A data da consulta nao faz parte das 15 colunas solicitadas.
Se houver registros invalidos, o R informa os motivos no terminal e mantem o resultado anterior.

## Gerar e organizar automaticamente

Na pasta do projeto:

```powershell
python simulador/controle_gerador.py ligar --quantidade 100 --filtrar
```

A primeira rodada e imediata, depois ocorre a cada 5 minutos. Mantenha o terminal aberto.
Para parar, abra outro terminal na mesma pasta:

```powershell
python simulador/controle_gerador.py desligar
```

Para executar somente o R, no console do RStudio com a pasta do projeto aberta:

```r
source("tratamento/executar_filtros.R", encoding="UTF-8")
```

Ou no PowerShell, dentro da pasta NutriMetrics:

```powershell
& "C:\Program Files\R\R-4.6.2\bin\Rscript.exe" tratamento/executar_filtros.R
```

Feche o CSV no Excel antes de atualizar. Os arquivos de controle do gerador sao necessarios para ligar e desligar.

## Interface

Abra Abrir gerador.bat com dois cliques. Escolha a quantidade e clique em Ligar. O R organiza automaticamente a cada rodada de 5 minutos. Desligar e fechar a janela aguardam a rodada atual terminar. Para mudar a quantidade, desligue primeiro. O botao Abrir pasta dos CSVs mostra os dois arquivos.

