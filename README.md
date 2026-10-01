# NutriMetrics - P1 DevOps

Esse repositório faz parte do projeto NutriMetrics e foi criado para a P1 de DevOps.

A ideia dessa entrega é criar uma máquina virtual Linux por código, preparar o ambiente automaticamente e rodar nela um simulador que gera dados fictícios relacionados ao acompanhamento nutricional.

## Tecnologias usadas

- OpenTofu
- cloud-init
- Ansible
- SSH / SCP
- Python
- KVM/libvirt
- Git/GitHub

## Estrutura

```text
nutrimetrics/
├── infraestrutura/
│   ├── main.tf
│   ├── variables.tf
│   ├── cloud_init.cfg
│   └── ansible/
│       ├── inventory.ini
│       └── playbook.yml
├── simulador/
│   ├── simulador.py
│   └── requirements.txt
├── dados/
│   └── exemplo_dados.csv
├── .gitignore
└── README.md
```

## Como funciona

```text
OpenTofu
   ↓
cria a VM Ubuntu
   ↓
cloud-init cria o usuário e configura SSH
   ↓
Ansible instala Python e cria as pastas
   ↓
SCP envia o simulador
   ↓
simulador roda dentro da VM
   ↓
CSV é gerado dentro da VM
```

## 1. Criar uma chave SSH

Caso ainda não tenha uma chave para o projeto:

```bash
ssh-keygen -t ed25519 -f ~/.ssh/nutrimetrics_ed25519
```

## 2. Criar a máquina virtual

Entre na pasta:

```bash
cd infraestrutura
```

Inicialize o OpenTofu:

```bash
tofu init
```

Confira o que será criado:

```bash
tofu plan
```

Crie a VM:

```bash
tofu apply
```

Digite `yes` quando for solicitado.

Depois veja o IP:

```bash
tofu output vm_ip
```

## 3. Configurar o IP no Ansible

Abra:

```text
infraestrutura/ansible/inventory.ini
```

Troque `IP_DA_VM` pelo IP mostrado pelo OpenTofu.

## 4. Preparar a VM

Na pasta `infraestrutura/ansible`:

```bash
ansible-playbook -i inventory.ini playbook.yml
```

O Ansible instala Python e cria as pastas do NutriMetrics.

## 5. Enviar o simulador

Na raiz do projeto:

```bash
scp -i ~/.ssh/nutrimetrics_ed25519 simulador/simulador.py nutri@IP_DA_VM:/home/nutri/nutrimetrics/
```

## 6. Entrar na VM

```bash
ssh -i ~/.ssh/nutrimetrics_ed25519 nutri@IP_DA_VM
```

## 7. Rodar o simulador

Dentro da VM:

```bash
cd /home/nutri/nutrimetrics
python3 simulador.py
```

O arquivo será criado em:

```text
/home/nutri/nutrimetrics/dados_nutrimetrics.csv
```

Para ver os dados:

```bash
cat dados_nutrimetrics.csv
```

Se rodar o simulador de novo, ele adiciona novos registros no mesmo arquivo.

## Simulador

O simulador gera dados fictícios como:

- id do registro
- id do paciente
- peso
- altura
- IMC
- circunferência abdominal
- objetivo
- data e hora

Nenhum dado utilizado é de paciente real.

## Destruir a VM

Quando quiser remover a infraestrutura:

```bash
cd infraestrutura
tofu destroy
```

## Observação

O projeto foi feito para a atividade de DevOps do NutriMetrics. A infraestrutura criada aqui vai servir como base para as próximas etapas de Big Data e análise de dados.
