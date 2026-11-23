# Análise e delimitação da entrega

## Materiais efetivamente analisados

Análise realizada em 11/11/2026.

1. **P1 – DevOps e Infraestrutura Privada.pdf**, fornecido em Downloads: sete páginas; extração de texto completa e conferência visual das páginas 3, 4 e 6, com organização, requisitos do simulador e preservação de dados. O documento é a referência acadêmica principal.
2. **devops-2026.zip**, localizado em Downloads: 20 entradas. Contém diretórios `ansible/` e `iac/`; `ansible/` não contém playbooks. Em `iac/`, foram examinados `main.tf` e `cloud_init.cfg`. O exemplo usa libvirt, duas VMs e cloud-init. O ZIP inclui estados locais; eles não foram copiados para a entrega nem utilizados pelo gerador.
3. **Repositório oficial** [m-montoro/NutriMetrics](https://github.com/m-montoro/NutriMetrics), clonado e examinado no commit `cf685971b4c545c9de71e39923cbcc29fcda62fe`: contém apenas `README.md`, com título histórico NutriVision, créditos da equipe e ideia de acompanhamento nutricional. Foram preservados esses conteúdos e acrescentadas as instruções do simulador. Não existia código a substituir.
4. **Referência** [marcelo-ciacco/devops-2026](https://github.com/marcelo-ciacco/devops-2026), clonado e examinado no commit `366f2e1e5c464d4163d3e1246e47d4d0d444c304`: estrutura `app/`, `iac/`, `ansible/`; aplicação Flask de sensores, coletor com escrita append em JSONL e automação de instalação/transferência. O domínio nutricional requer regras próprias. O simulador entregue usa CSV e execução direta no terminal, conforme o pedido.

O ZIP não é uma cópia idêntica do repositório de referência: seu escopo é infraestrutura. O repositório contém Docker e componentes posteriores ao checkpoint. Esses componentes não são necessários para este gerador e não foram incorporados. Foram lidos somente arquivos pertinentes; estados locais e ambientes virtuais de referência não integram a entrega.

## Correspondência com o PDF

| Referência acadêmica | Requisito | Situação nesta etapa |
| --- | --- | --- |
| 4.1 / 5.1.1 | Código em `simulador/` | Implementado |
| 5.1.2 | Execução por comando sem GUI | Implementado com argparse |
| 5.1.3 / 5.1.4 | Domínio do projeto, ID, ao menos três variáveis e informação temporal | Implementado: 20 colunas nutricionais, cadastrais e temporais |
| 5.1.5 | Pelo menos dez registros por execução | Implementado; valores menores são rejeitados |
| 5.1.6 | CSV ou JSON | Implementado em CSV UTF-8 |
| 4.1 | Exemplo em `dados/` | Gerado: `exemplo_dados.csv` |
| 5.6.5 | Novas execuções sem perda dos dados anteriores | Implementado e testado localmente |
| 5.5.4 | Ausência de caminhos exclusivos da máquina hospedeira | Implementado com pathlib e destino configurável |
| 4 / 5.2–5.5 | OpenTofu, cloud-init, Ansible e SSH | Próxima etapa; fora da implementação solicitada |
| 5.6.1–5.6.4 | Execução e evidências reais na VM | Pendente; não demonstrado nesta entrega |
| 5.7 | GitHub, documentação e histórico de desenvolvimento | Arquivos/documentação prontos; commits e publicação cabem à equipe |

**Este pacote atende à parte de desenvolvimento do simulador, mas não constitui a entrega completa do checkpoint.** O pedido atual exclui implementar infraestrutura. Por isso, não foram criados arquivos `.tf`, playbooks, Docker, pipeline ou uma VM. O diretório `infraestrutura/` deverá reunir os arquivos reais na fase seguinte.

## Plano implementado

1. Separar código, exemplo, testes e documentação, aproveitando o repositório existente.
2. Derivar perfis de pacientes de uma seed e índice, mantendo características fixas entre refeições e execuções com a mesma seed.
3. Associar preparos sintéticos a tipos de refeição e calcular nutrientes por massa consumida.
4. Calcular IMC e energia com os valores efetivamente exportados e arredondamento decimal explícito.
5. Gerar datas dentro de um período passado configurável e horários plausíveis por tipo de refeição.
6. Acrescentar linhas por iterador, verificando o arquivo existente e reservando sua escrita com bloqueio local.
7. Validar dados, CLI, repetição, preservação e importação analítica sem bibliotecas externas.

## Limites para futuras análises

As variáveis têm relações deliberadamente construídas. Padrões encontrados poderão refletir essas regras, em vez de evidência sobre uma população real. A coorte é adulta e estática; as refeições são amostras independentes. A versão das regras acompanha cada linha para permitir rastrear sua origem. Alterações futuras podem acrescentar um identificador de lote, evolução de peso ou cadastro longitudinal, mas deverão definir uma migração do CSV e seus critérios antes da implementação.
