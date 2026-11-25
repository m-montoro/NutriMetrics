# Le, confere e organiza os dados do NutriMetrics.
COLUNAS <- c(
  "registro_id", "paciente_id", "idade", "peso_kg", "altura_m", "imc",
  "objetivo_nutricional", "nivel_atividade_fisica", "sexo", "n_refeicoes_livres", "atividade_fisica", "tipo_refeicao",
  "alimento_principal", "quantidade_g", "calorias_kcal", "proteinas_g",
  "carboidratos_g", "gorduras_g", "fibras_g", "agua_ml",
  "data_hora_refeicao", "data_hora_geracao", "versao_gerador"
)
NUMERICAS <- c("n_refeicoes_livres", "idade", "peso_kg", "altura_m", "imc", "quantidade_g",
               "calorias_kcal", "proteinas_g", "carboidratos_g",
               "gorduras_g", "fibras_g", "agua_ml")
JANELAS <- list(cafe_da_manha=c(360, 539), lanche_manha=c(540, 659),
                almoco=c(690, 869), lanche_tarde=c(900, 1049),
                jantar=c(1080, 1259), ceia=c(1260, 1379))

ler_csv <- function(caminho) {
  if (!file.exists(caminho)) stop("CSV de entrada nao encontrado: ", caminho)
  larguras <- count.fields(caminho, sep=",", quote='"', comment.char="",
                          blank.lines.skip=FALSE)
  if (!length(larguras) || anyNA(larguras) || any(larguras != length(COLUNAS))) {
    stop("Estrutura CSV invalida: esperado cabecalho e linhas com 23 campos.")
  }
  d <- read.csv(caminho, colClasses="character", stringsAsFactors=FALSE,
                check.names=FALSE, fileEncoding="UTF-8-BOM", na.strings="",
                row.names=NULL, fill=FALSE, blank.lines.skip=FALSE)
  if (anyDuplicated(names(d)) || !setequal(names(d), COLUNAS)) {
    stop("Cabecalho incompativel com o CSV NutriMetrics versao 1.")
  }
  d[COLUNAS]
}

parse_iso <- function(x) {
  # Le a data e a hora, respeitando o fuso informado.
  formato <- "^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(\\.[0-9]{1,6})?(Z|[+-][0-9]{2}:[0-9]{2})$"
  saida <- rep(NA_real_, length(x))
  indices <- which(!is.na(x) & grepl(formato, x))
  for (i in indices) {
    local <- sub("(Z|[+-][0-9]{2}:[0-9]{2})$", "", x[i])
    instante <- suppressWarnings(as.POSIXct(strptime(local, "%Y-%m-%dT%H:%M:%OS", tz="UTC")))
    if (is.na(instante) || format(instante, "%Y-%m-%dT%H:%M:%S", tz="UTC") != substr(local, 1, 19)) next
    offset <- substring(x[i], nchar(local)+1)
    delta <- 0
    if (offset != "Z") {
      h <- as.integer(substr(offset, 2, 3))
      m <- as.integer(substr(offset, 5, 6))
      if (h > 14 || m > 59 || (h == 14 && m != 0)) next
      delta <- (h*3600+m*60) * ifelse(substr(offset, 1, 1)=="-", -1, 1)
    }
    saida[i] <- as.numeric(instante)-delta
  }
  as.POSIXct(saida, origin="1970-01-01", tz="UTC")
}

preparar_dados <- function(brutos, agora=Sys.time()) {
  if (!identical(names(brutos), COLUNAS)) stop("Esquema de entrada inesperado.")
  n <- nrow(brutos)
  d <- brutos
  for (k in names(d)) {
    d[[k]] <- trimws(d[[k]])
    d[[k]][!is.na(d[[k]]) & d[[k]]==""] <- NA_character_
  }
  normalizados <- d
  motivos <- rep("", n)
  marcar <- function(condicao, motivo) {
    idx <- which(!is.na(condicao) & condicao)
    motivos[idx] <<- ifelse(motivos[idx]=="", motivo, paste(motivos[idx], motivo, sep=";"))
  }
  marcar(!complete.cases(d), "campo_obrigatorio_ausente")
  for (k in NUMERICAS) {
    valor <- d[[k]]
    numero <- suppressWarnings(as.numeric(valor))
    valido <- !is.na(valor) & grepl("^[+-]?([0-9]+(\\.[0-9]*)?|\\.[0-9]+)$", valor) & is.finite(numero)
    numero[!valido] <- NA_real_
    marcar(!valido, paste0("numero_invalido:", k))
    d[[k]] <- numero
  }
  marcar(!grepl("^[1-9][0-9]*$", d$registro_id), "registro_id_invalido")
  marcar(!grepl("^pac_[0-9a-f]{64}$", d$paciente_id), "paciente_id_invalido")
  faixas <- list(n_refeicoes_livres=c(0,100), idade=c(18,80), peso_kg=c(37,153), altura_m=c(1.45,2),
                 imc=c(17.99,38.01), quantidade_g=c(70,662), calorias_kcal=c(0.01,3000),
                 proteinas_g=c(0.01,200), carboidratos_g=c(0.01,300),
                 gorduras_g=c(0.01,150), fibras_g=c(0,100), agua_ml=c(0,600))
  for (k in names(faixas)) {
    marcar(d[[k]] < faixas[[k]][1] | d[[k]] > faixas[[k]][2], paste0("fora_da_faixa:", k))
  }
  marcar(d$n_refeicoes_livres != floor(d$n_refeicoes_livres), "refeicoes_livres_nao_inteiras")
  marcar((d$nivel_atividade_fisica=="sedentario") != (d$atividade_fisica=="nao_faz_nada"), "atividade_incompativel")
  marcar(d$idade != floor(d$idade), "idade_nao_inteira")
  marcar(d$agua_ml %% 50 != 0, "agua_fora_do_passo_50ml")
  categorias <- list(sexo=c("homem","mulher"), atividade_fisica=c("academia","nao_faz_nada","corrida","bicicleta","caminhada","natacao","danca"), objetivo_nutricional=c("reducao_peso","manutencao","ganho_massa"),
                     nivel_atividade_fisica=c("sedentario","leve","moderado","intenso"),
                     tipo_refeicao=names(JANELAS), versao_gerador="1")
  for (k in names(categorias)) marcar(!d[[k]] %in% categorias[[k]], paste0("categoria_invalida:", k))
  imc <- d$peso_kg/d$altura_m^2
  kcal <- 4*d$proteinas_g+4*d$carboidratos_g+9*d$gorduras_g
  marcar(abs(d$imc-imc) > 0.005001, "imc_inconsistente")
  marcar(abs(d$calorias_kcal-kcal) > 0.02000001, "calorias_inconsistentes")
  marcar(d$fibras_g > d$carboidratos_g, "fibras_maiores_que_carboidratos")
  marcar(d$proteinas_g+d$carboidratos_g+d$gorduras_g > d$quantidade_g+0.02,
         "macronutrientes_maiores_que_porcao")
  refeicao <- parse_iso(d$data_hora_refeicao)
  geracao <- parse_iso(d$data_hora_geracao)
  marcar(is.na(refeicao) | is.na(geracao), "data_hora_invalida")
  marcar(refeicao > geracao | geracao > agora+1, "ordem_temporal_invalida")
  # Usa o mesmo fuso horario do gerador: UTC menos 3 horas.
  local <- as.POSIXlt(refeicao-3*3600, tz="UTC")
  minutos <- local$hour*60+local$min
  for (tipo in names(JANELAS)) {
    j <- JANELAS[[tipo]]
    marcar(d$tipo_refeicao==tipo & (minutos<j[1] | minutos>j[2]), "horario_incompativel")
  }
  # Se o mesmo ID tiver dados diferentes, separa todas essas linhas.
  # Se as linhas forem iguais, mantem a primeira e separa as copias.
  for (idx in split(seq_len(n), d$registro_id)) {
    if (length(idx)>1) {
      if (nrow(unique(normalizados[idx, , drop=FALSE])) > 1) {
        marcar(seq_len(n) %in% idx, "registro_id_conflitante")
      } else marcar(seq_len(n) %in% idx[-1], "duplicata_identica")
    }
  }
  perfil <- c("sexo","n_refeicoes_livres","atividade_fisica","idade","peso_kg","altura_m","imc","objetivo_nutricional","nivel_atividade_fisica")
  candidatos <- which(motivos=="")
  grupos <- split(candidatos, d$paciente_id[candidatos])
  for (idx in grupos) {
    if (nrow(unique(d[idx, perfil, drop=FALSE])) > 1) {
      marcar(d$paciente_id==d$paciente_id[idx[1]], "perfil_paciente_conflitante")
    }
  }
  bons <- which(motivos=="")
  tratados <- d[bons, , drop=FALSE]
  tratados$data_hora_refeicao <- refeicao[bons]
  tratados$data_hora_geracao <- geracao[bons]
  tratados$linha_origem <- bons+1L
  tratados$data_refeicao <- as.Date(refeicao[bons]-3*3600, tz="UTC")
  tratados$hora_refeicao <- local$hour[bons]
  tratados$dia_semana_iso <- as.integer(format(refeicao[bons]-3*3600, "%u", tz="UTC"))
  tratados$imc_recalculado <- round(imc[bons], 2)
  tratados$calorias_recalculadas_kcal <- round(kcal[bons], 2)
  tratados <- tratados[order(tratados$data_hora_refeicao, tratados$paciente_id), , drop=FALSE]
  ruins <- which(motivos!="")
  rejeitados <- brutos[ruins, , drop=FALSE]
  rejeitados$linha_origem <- ruins+1L
  rejeitados$motivos <- motivos[ruins]
  espacos <- sum(vapply(COLUNAS, function(k) {
    sum(!is.na(brutos[[k]]) & brutos[[k]]!=normalizados[[k]], na.rm=TRUE)
  }, numeric(1)))
  qualidade <- data.frame(
    metrica=c("registros_entrada","registros_tratados","registros_rejeitados",
              "pacientes_tratados","campos_com_espacos_normalizados"),
    valor=c(n,nrow(tratados),nrow(rejeitados),length(unique(tratados$paciente_id)),espacos))
  faltantes <- data.frame(coluna=COLUNAS, ausentes=vapply(normalizados, function(x) sum(is.na(x)), integer(1)))
  codigos <- unlist(strsplit(motivos[ruins], ";", fixed=TRUE), use.names=FALSE)
  tab <- table(codigos)
  problemas <- data.frame(motivo=as.character(names(tab)), ocorrencias=as.integer(tab))
  list(tratados=tratados, rejeitados=rejeitados, qualidade=qualidade,
       ausentes=faltantes, problemas=problemas)
}

