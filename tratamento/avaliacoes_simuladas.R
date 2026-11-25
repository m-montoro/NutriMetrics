# Cria uma avaliacao ficticia para cada paciente do projeto.
criar_avaliacoes <- function(d) {
  campos <- c("paciente_id", "idade", "peso_kg", "altura_m", "imc")
  p <- unique(d[campos])
  if (anyDuplicated(p$paciente_id)) stop("Paciente com medidas conflitantes.")
  p$percentual_gordura_corporal <- numeric(nrow(p))
  p$data_ultima_consulta <- as.Date(rep(NA_character_, nrow(p)))
  for (i in seq_len(nrow(p))) {
    # O identificador mantem o valor ficticio igual nas proximas execucoes.
    codigo <- utf8ToInt(p$paciente_id[i])
    numero <- sum(codigo * seq_along(codigo)^2)
    p$percentual_gordura_corporal[i] <- 12 + (numero %% 2801) / 100
    datas <- d$data_hora_geracao[d$paciente_id == p$paciente_id[i]]
    referencia <- as.Date(min(datas) - 3 * 3600, tz="UTC")
    p$data_ultima_consulta[i] <- referencia - (7 + numero %% 84)
  }
  p$massa_gorda_kg <- round(p$peso_kg * p$percentual_gordura_corporal / 100, 2)
  p$massa_livre_gordura_kg <- round(p$peso_kg - p$massa_gorda_kg, 2)
  p$origem_avaliacao <- rep("simulacao_academica_nao_medida", nrow(p))
  p
}

# Esta copia usa o formato habitual do Excel em portugues.
salvar_excel_ptbr <- function(d, caminho) {
  for (k in names(d)) {
    if (inherits(d[[k]], "POSIXt")) {
      d[[k]] <- if (length(d[[k]])) paste0(format(d[[k]] - 3*3600,
                       "%Y-%m-%dT%H:%M:%S", tz="UTC"), "-03:00") else character()
    }
  }
  write.table(d, caminho, sep=";", dec=",", row.names=FALSE, quote=TRUE,
              na="", fileEncoding="UTF-8")
}
