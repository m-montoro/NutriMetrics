source("tratamento/filtrar_nutricao.R")
p <- tempfile(); dir.create(p)
r <- filtrar_nutricao("dados/dados_nutricionais.csv",p)
primeiro <- readLines(r$arquivo)
filtrar_nutricao("dados/dados_nutricionais.csv",p)
stopifnot(length(list.files(p))==1, identical(primeiro,readLines(r$arquivo)))
d <- read.csv2(r$arquivo)
stopifnot(ncol(d)==15, !anyDuplicated(d$paciente_id),
  all(abs(d$massa_magra+d$massa_gorda-d$peso_kg)<0.001))
bruto <- ler_csv("dados/dados_nutricionais.csv")
bruto$peso_kg[1] <- "-1"
entrada <- tempfile(fileext=".csv")
write.csv(bruto,entrada,row.names=FALSE)
erro <- tryCatch({filtrar_nutricao(entrada,p); FALSE},error=function(e) TRUE)
stopifnot(erro, identical(primeiro,readLines(r$arquivo)))
unlink(entrada)
cat("OK: 15 colunas, arquivo unico, repeticao, massas e entrada invalida.\n")

stopifnot(identical(classificar_gordura(c(5.9,6,13.5,14,20.9,21,24.9,25),rep("homem",8)),
 c("muito_baixo_magro","baixo","baixo","ideal","ideal","elevado","elevado","obesidade")))
stopifnot(identical(classificar_gordura(c(13.9,14,20.5,21,28.9,29,32.9,33),rep("mulher",8)),
 c("muito_baixo_magro","baixo","baixo","ideal","ideal","elevado","elevado","obesidade")))
brutos <- ler_csv("dados/dados_nutricionais.csv")
idx <- match(d$paciente_id,brutos$paciente_id)
b <- brutos[idx,]
esperado <- 10*as.numeric(b$peso_kg)+625*as.numeric(b$altura_m)-5*as.numeric(b$idade)+ifelse(b$sexo=="homem",5,-161)+unname(c(sedentario=0,leve=150,moderado=300,intenso=500)[b$nivel_atividade_fisica])
stopifnot(all(abs(d$total_calorias_basal-esperado)<=0.005001),
 all(abs(d$total_agua_l-as.numeric(b$peso_kg)*0.035)<=0.000501),
 all(d$n_refeicoes_livres>=0 & d$n_refeicoes_livres<=100))
cat("OK: formulas, agua e limites da classificacao para ambos os sexos.\n")
