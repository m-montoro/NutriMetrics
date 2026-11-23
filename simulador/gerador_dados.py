#!/usr/bin/env python3
"""Gera refeições fictícias e salva em CSV."""

from __future__ import annotations

import argparse
import csv
import hashlib
import os
import random
import sys
from contextlib import contextmanager
from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

VERSAO = "1"
FUSO_REFEICOES = timezone(timedelta(hours=-3))
SAIDA_PADRAO = Path(__file__).resolve().parent.parent / "dados/dados_nutricionais.csv"
CAMPOS_PACIENTE = (
    "paciente_id", "idade", "peso_kg", "altura_m", "imc",
    "objetivo_nutricional", "nivel_atividade_fisica",
)
COLUNAS = (
    "registro_id", *CAMPOS_PACIENTE, "tipo_refeicao", "alimento_principal",
    "quantidade_g", "calorias_kcal", "proteinas_g", "carboidratos_g",
    "gorduras_g", "fibras_g", "agua_ml", "data_hora_refeicao",
    "data_hora_geracao", "versao_gerador",
)
# Proteínas, carboidratos, gorduras e fibras por 100 g de cada preparo.
# Os valores são fictícios, usados apenas neste projeto.
PREPAROS = {
    "cafe_da_manha": (
        ("aveia_com_iogurte_e_banana", 5.5, 19.0, 3.5, 2.2),
        ("pao_integral_com_ovos", 12.0, 24.0, 8.0, 3.0),
    ),
    "lanche_manha": (
        ("frutas_com_iogurte", 3.5, 16.0, 1.8, 1.5),
        ("banana_com_aveia", 3.0, 28.0, 2.0, 3.0),
    ),
    "almoco": (
        ("arroz_feijao_frango_e_legumes", 12.0, 18.0, 4.0, 3.0),
        ("arroz_lentilha_e_legumes", 6.0, 22.0, 3.0, 4.0),
        ("peixe_batata_e_salada", 12.0, 13.0, 4.5, 2.0),
    ),
    "lanche_tarde": (
        ("sanduiche_integral_de_frango", 12.0, 23.0, 5.0, 2.5),
        ("iogurte_com_frutas_e_aveia", 5.0, 20.0, 3.0, 2.2),
    ),
    "jantar": (
        ("frango_arroz_e_salada", 13.0, 16.0, 4.0, 2.3),
        ("omelete_com_legumes_e_batata", 9.0, 11.0, 7.0, 2.0),
        ("sopa_de_lentilha_e_legumes", 5.0, 13.0, 2.0, 3.5),
    ),
    "ceia": (
        ("iogurte_com_aveia", 5.0, 14.0, 3.0, 1.5),
        ("frutas_com_iogurte", 3.5, 16.0, 1.8, 1.5),
    ),
}
# Horários das refeições em minutos e tamanho das porções em gramas.
REFEICOES = {
    "cafe_da_manha": (360, 539, 160, 300),
    "lanche_manha": (540, 659, 100, 200),
    "almoco": (690, 869, 300, 500),
    "lanche_tarde": (900, 1049, 120, 240),
    "jantar": (1080, 1259, 250, 450),
    "ceia": (1260, 1379, 100, 180),
}
ATIVIDADES = ("sedentario", "leve", "moderado", "intenso")


def decimal2(valor: object) -> str:
    """Deixa o valor com duas casas decimais."""
    return str(Decimal(str(valor)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def perfil_paciente(seed: int, indice: int) -> dict[str, object]:
    """Mantém os mesmos dados para cada paciente."""
    digest = hashlib.sha256(f"nutrimetrics:{VERSAO}:{seed}:{indice}".encode()).hexdigest()
    rng = random.Random(int(digest, 16))
    altura = Decimal(decimal2(rng.uniform(1.45, 2.00)))
    peso = Decimal(decimal2(altura * altura * Decimal(str(rng.uniform(18, 38)))))
    imc = Decimal(decimal2(peso / (altura * altura)))
    objetivos = ("reducao_peso", "manutencao", "ganho_massa")
    # Sorteia o objetivo do paciente, levando o IMC em conta.
    pesos = (7, 2, 1) if imc >= 27 else (1, 5, 4)
    return {
        "paciente_id": "pac_" + digest,
        "idade": rng.randint(18, 80),
        "peso_kg": str(peso),
        "altura_m": str(altura),
        "imc": str(imc),
        "objetivo_nutricional": rng.choices(objetivos, weights=pesos)[0],
        "nivel_atividade_fisica": rng.choice(ATIVIDADES),
    }


def gerar_registros(quantidade: int, seed: int, pacientes: int,
                    inicio: date, fim: date, primeiro_id: int,
                    gerado_em: datetime):
    """Cria uma refeição de cada vez."""
    rng = random.Random(seed)
    dias = (fim - inicio).days + 1
    tipos = tuple(REFEICOES)
    for deslocamento in range(quantidade):
        perfil = perfil_paciente(seed, rng.randrange(pacientes))
        tipo = rng.choices(tipos, weights=(20, 10, 25, 15, 25, 5))[0]
        h_min, h_max, g_min, g_max = REFEICOES[tipo]
        preparo, proteina, carboidrato, gordura, fibra = rng.choice(PREPAROS[tipo])
        fator_objetivo = {"reducao_peso": 0.85, "manutencao": 1.0, "ganho_massa": 1.15}
        fator_atividade = dict(zip(ATIVIDADES, (0.95, 1.0, 1.08, 1.15)))
        quantidade_g = Decimal(decimal2(
            rng.uniform(g_min, g_max)
            * fator_objetivo[perfil["objetivo_nutricional"]]
            * fator_atividade[perfil["nivel_atividade_fisica"]]
        ))
        nutrientes = [Decimal(decimal2(Decimal(str(v)) * quantidade_g / 100))
                      for v in (proteina, carboidrato, gordura, fibra)]
        p, c, g, f = nutrientes
        # Calcula as calorias a partir dos nutrientes da refeição.
        kcal = p * 4 + c * 4 + g * 9
        dia = inicio + timedelta(days=rng.randrange(dias))
        minuto = rng.randint(h_min, h_max)
        instante = datetime.combine(dia, time(minuto // 60, minuto % 60), FUSO_REFEICOES)
        yield {
            "registro_id": primeiro_id + deslocamento,
            **perfil,
            "tipo_refeicao": tipo,
            "alimento_principal": preparo,
            "quantidade_g": str(quantidade_g),
            "calorias_kcal": decimal2(kcal),
            "proteinas_g": str(p), "carboidratos_g": str(c),
            "gorduras_g": str(g), "fibras_g": str(f),
            "agua_ml": rng.randrange(0, 601, 50),
            "data_hora_refeicao": instante.isoformat(),
            "data_hora_geracao": gerado_em.isoformat(timespec="microseconds"),
            "versao_gerador": VERSAO,
        }


@contextmanager
def bloquear(saida: Path):
    """Evita duas gravações ao mesmo tempo no mesmo arquivo."""
    lock = saida.with_name(saida.name + ".lock")
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        raise ValueError(
            f"Arquivo em uso ou bloqueio residual: {lock}. "
            "Se nenhum gerador estiver ativo, remova somente esse .lock e tente novamente."
        ) from None
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as arquivo:
            arquivo.write(str(os.getpid()))
        yield
    finally:
        lock.unlink()


def verificar_existente(saida: Path) -> int:
    """Confere o CSV existente e encontra o último ID."""
    if not saida.exists() or saida.stat().st_size == 0:
        return 0
    ultimo = 0
    with saida.open("r", encoding="utf-8", newline="") as arquivo:
        leitor = csv.reader(arquivo, strict=True)
        if next(leitor, None) != list(COLUNAS):
            raise ValueError("Cabeçalho incompatível. Use outro --saida; o arquivo foi preservado.")
        for linha in leitor:
            if len(linha) != len(COLUNAS) or any(not celula for celula in linha):
                raise ValueError(f"CSV incompleto na linha {leitor.line_num}; arquivo preservado.")
            try:
                identificador = int(linha[0])
            except ValueError:
                raise ValueError(f"ID inválido na linha {leitor.line_num}.") from None
            if identificador <= ultimo or str(identificador) != linha[0]:
                raise ValueError("IDs existentes devem ser inteiros positivos estritamente crescentes.")
            ultimo = identificador
    return ultimo


def executar(quantidade: int, saida: Path, seed: int | None, pacientes: int,
             inicio: date, fim: date, agora: datetime | None = None) -> int:
    agora = agora or datetime.now(timezone.utc)
    if quantidade < 10:
        raise ValueError("--quantidade deve ser pelo menos 10.")
    if pacientes < 1:
        raise ValueError("--pacientes deve ser pelo menos 1.")
    if inicio > fim:
        raise ValueError("--data-inicio não pode ser posterior a --data-fim.")
    if fim >= agora.astimezone(FUSO_REFEICOES).date():
        raise ValueError("--data-fim deve ser anterior ao dia atual (UTC-03:00).")
    saida = saida.expanduser().resolve()
    saida.parent.mkdir(parents=True, exist_ok=True)
    seed = seed if seed is not None else random.SystemRandom().getrandbits(128)
    with bloquear(saida):
        ultimo = verificar_existente(saida)
        tamanho_original = saida.stat().st_size if saida.exists() else 0
        # Confere se é preciso começar uma nova linha antes de gravar.
        precisa_quebra = False
        if tamanho_original:
            with saida.open("rb") as arquivo:
                arquivo.seek(-1, os.SEEK_END)
                precisa_quebra = arquivo.read(1) not in (b"\n", b"\r")
        try:
            with saida.open("a", encoding="utf-8", newline="") as arquivo:
                if precisa_quebra:
                    arquivo.write("\n")
                escritor = csv.DictWriter(arquivo, fieldnames=COLUNAS, lineterminator="\n")
                if not tamanho_original:
                    escritor.writeheader()
                escritor.writerows(gerar_registros(
                    quantidade, seed, pacientes, inicio, fim, ultimo + 1, agora,
                ))
                arquivo.flush()
                os.fsync(arquivo.fileno())
        except BaseException:
            # Se houver erro, mantém o arquivo como estava antes.
            with saida.open("r+b") as arquivo:
                arquivo.truncate(tamanho_original)
            raise
    return seed


def data_iso(texto: str) -> date:
    try:
        resultado = date.fromisoformat(texto)
        if resultado.isoformat() != texto:
            raise ValueError
        return resultado
    except ValueError:
        raise argparse.ArgumentTypeError("Use uma data válida no formato AAAA-MM-DD.") from None


def main(argv: list[str] | None = None) -> int:
    ontem = datetime.now(FUSO_REFEICOES).date() - timedelta(days=1)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--quantidade", type=int, default=10, help="Registros a acrescentar (mínimo 10).")
    parser.add_argument("--saida", type=Path, default=SAIDA_PADRAO, help="CSV de destino.")
    parser.add_argument("--seed", type=int, help="Semente; se omitida, é sorteada e informada.")
    parser.add_argument("--pacientes", type=int, default=100, help="Tamanho da população sintética (padrão 100).")
    parser.add_argument("--data-inicio", type=data_iso, default=ontem - timedelta(days=29))
    parser.add_argument("--data-fim", type=data_iso, default=ontem)
    args = parser.parse_args(argv)
    try:
        seed = executar(args.quantidade, args.saida, args.seed, args.pacientes,
                        args.data_inicio, args.data_fim)
    except (OSError, ValueError, csv.Error) as erro:
        print(f"Erro: {erro}", file=sys.stderr)
        return 1
    print(f"Gerados {args.quantidade} registros em {args.saida.expanduser().resolve()}")
    print(f"Seed: {seed}; período: {args.data_inicio} a {args.data_fim}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
