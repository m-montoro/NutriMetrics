# Confere a entrada e organiza uma linha por paciente.
source("tratamento/tratar_dados.R", encoding="UTF-8")
source("tratamento/avaliacoes_simuladas.R", encoding="UTF-8")

# Usa os limites fornecidos para esta simulacao.
classificar_gordura <- function(percentual, sexo) {
  limites <- ifelse(sexo=="homem", 6, 14)
  baixo <- ifelse(sexo=="homem", 14, 21)
  ideal <- ifelse(sexo=="homem", 21, 29)
  elevado <- ifelse(sexo=="homem", 25, 33)
  ifelse(percentual < limites, "muito_baixo_magro",
    ifelse(percentual < baixo, "baixo",
      ifelse(percentual < ideal, "ideal",
        ifelse(percentual < elevado, "elevado", "obesidade"))))
}

filtrar_nutricao <- function(entrada, saida="dados") {
  destino <- file.path(saida, "dados_organizados.csv")
  if (normalizePath(entrada, mustWork=TRUE) == normalizePath(destino, mustWork=FALSE))
    stop("A entrada e a saida precisam ser diferentes.")
  resultado <- preparar_dados(ler_csv(entrada))
  d <- resultado$tratados
  if (nrow(resultado$rejeitados)) {
    print(resultado$problemas)
    stop("Existem registros invalidos. Corrija a entrada; a saida anterior foi mantida.")
  }
  a <- criar_avaliacoes(d)
  idx <- match(a$paciente_id, d$paciente_id)
  agua <- round(a$peso_kg * 35 / 1000, 3)
  # A formula usa a altura em centimetros.
  tmb <- 10*a$peso_kg + 6.25*(a$altura_m*100) - 5*a$idade + ifelse(d$sexo[idx]=="homem",5,-161)
  adicional <- c(sedentario=0, leve=150, moderado=300, intenso=500)
  calorias <- round(tmb + unname(adicional[d$nivel_atividade_fisica[idx]]),2)
  # Organiza as colunas do modelo.
  organizado <- data.frame(
    paciente_id=a$paciente_id, idade=a$idade, peso_kg=a$peso_kg,
    altura_m=a$altura_m, imc=a$imc,
    objetivo_nutricional=d$objetivo_nutricional[idx],
    nivel_atividade_fisica=d$nivel_atividade_fisica[idx],
    n_refeicoes_livres=d$n_refeicoes_livres[idx],
    total_calorias_basal=calorias,
    percentual_gordura=a$percentual_gordura_corporal,
    massa_magra=a$massa_livre_gordura_kg, massa_gorda=a$massa_gorda_kg,
    total_agua_l=agua, atividade_fisica=d$atividade_fisica[idx],
    condicao_fisica=classificar_gordura(a$percentual_gordura_corporal,d$sexo[idx]))
  organizado <- organizado[order(organizado$paciente_id), , drop=FALSE]
  dir.create(saida, recursive=TRUE, showWarnings=FALSE)
  temporario <- tempfile("organizado_",tmpdir=saida)
  on.exit(unlink(temporario), add=TRUE)
  salvar_excel_ptbr(organizado,temporario)
  if (!file.copy(temporario,destino,overwrite=TRUE)) stop("Feche o CSV no Excel e tente novamente.")
  message(nrow(organizado), " pacientes simulados. CSV: ", normalizePath(destino))
  invisible(list(dados=organizado, arquivo=destino))
}
