# O controlador chama este arquivo depois de gerar os dados.
source("tratamento/filtrar_nutricao.R", encoding="UTF-8")
args <- commandArgs(trailingOnly=TRUE)
if (length(args)!=2) stop("Informe a entrada e a pasta de saida.")
filtrar_nutricao(args[1],args[2])
