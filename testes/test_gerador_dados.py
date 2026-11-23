"""Testes para conferir se o gerador funciona corretamente."""

import csv
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from datetime import date, datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from unittest.mock import patch

from simulador import gerador_dados as g

RAIZ = Path(__file__).resolve().parents[1]
SCRIPT = RAIZ / "simulador/gerador_dados.py"
INICIO, FIM = date(2026, 1, 1), date(2026, 1, 31)
AGORA = datetime(2026, 2, 1, 12, tzinfo=timezone.utc)


class TestGerador(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.saida = Path(self.temp.name) / "pasta_nova/dados.csv"

    def gerar(self, n=10, **kwargs):
        args = dict(quantidade=n, saida=self.saida, seed=42, pacientes=5,
                    inicio=INICIO, fim=FIM, agora=AGORA)
        args.update(kwargs)
        return g.executar(**args)

    def ler(self, saida=None):
        with (saida or self.saida).open(encoding="utf-8", newline="") as f:
            return list(csv.DictReader(f))

    def cli(self, *extras, cwd=None):
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--saida", str(self.saida),
             "--data-inicio", str(INICIO), "--data-fim", str(FIM), *extras],
            cwd=cwd, capture_output=True, encoding="utf-8", errors="replace",
        )

    def test_10_registros_e_criacao_automatica(self):
        self.gerar()
        self.assertEqual(len(self.ler()), 10)
        with self.saida.open(encoding="utf-8", newline="") as f:
            self.assertEqual(next(csv.reader(f)), list(g.COLUNAS))

    def test_1000_registros_consistentes(self):
        self.gerar(1000)
        linhas = self.ler()
        self.assertEqual(len(linhas), 1000)
        perfis = {}
        instantes = set()
        tipos = set()
        for r in linhas:
            self.assertEqual(set(r), set(g.COLUNAS))
            self.assertTrue(all(v is not None and v != "" for v in r.values()))
            perfil = tuple(r[k] for k in g.CAMPOS_PACIENTE)
            pid = r["paciente_id"]
            self.assertEqual(perfis.setdefault(pid, perfil), perfil)
            self.assertTrue(18 <= int(r["idade"]) <= 80)
            peso, altura = Decimal(r["peso_kg"]), Decimal(r["altura_m"])
            self.assertTrue(1.45 <= float(altura) <= 2)
            self.assertTrue(37 <= float(peso) <= 153)
            esperado = (peso / altura ** 2).quantize(Decimal(".01"), rounding=ROUND_HALF_UP)
            self.assertEqual(Decimal(r["imc"]), esperado)
            self.assertTrue(Decimal("17.99") <= esperado <= Decimal("38.01"))
            p, c, gordura, fibra = [Decimal(r[k]) for k in
                                   ("proteinas_g", "carboidratos_g", "gorduras_g", "fibras_g")]
            self.assertEqual(Decimal(r["calorias_kcal"]), p * 4 + c * 4 + gordura * 9)
            quantidade = Decimal(r["quantidade_g"])
            self.assertTrue(Decimal("70") <= quantidade <= Decimal("662"))
            self.assertTrue(0 <= fibra <= c)
            self.assertTrue(p > 0 and c > 0 and gordura > 0)
            self.assertLessEqual(p + c + gordura, quantidade)
            self.assertTrue(0 <= int(r["agua_ml"]) <= 600)
            for k in ("peso_kg", "altura_m", "imc", "quantidade_g", "calorias_kcal",
                      "proteinas_g", "carboidratos_g", "gorduras_g", "fibras_g"):
                self.assertTrue(Decimal(r[k]).is_finite())
                self.assertNotIn(",", r[k])
            instante = datetime.fromisoformat(r["data_hora_refeicao"])
            gerado = datetime.fromisoformat(r["data_hora_geracao"])
            self.assertIsNotNone(instante.tzinfo)
            self.assertEqual(gerado, AGORA)
            self.assertLess(instante, gerado)
            self.assertTrue(INICIO <= instante.date() <= FIM)
            h_min, h_max, _, _ = g.REFEICOES[r["tipo_refeicao"]]
            self.assertTrue(h_min <= instante.hour * 60 + instante.minute <= h_max)
            self.assertIn(r["alimento_principal"], [p[0] for p in g.PREPAROS[r["tipo_refeicao"]]])
            self.assertIn(r["nivel_atividade_fisica"], g.ATIVIDADES)
            instantes.add(instante.date())
            tipos.add(r["tipo_refeicao"])
        self.assertEqual(len(perfis), 5)
        self.assertEqual(len(instantes), 31)
        self.assertEqual(tipos, set(g.REFEICOES))

    def test_append_preserva_bytes_ids_e_perfis(self):
        self.gerar()
        antes = self.saida.read_bytes()
        self.gerar(1000)
        self.assertTrue(self.saida.read_bytes().startswith(antes))
        linhas = self.ler()
        self.assertEqual(len(linhas), 1010)
        ids = [int(r["registro_id"]) for r in linhas]
        self.assertEqual(ids, list(range(1, 1011)))
        perfis = {}
        for r in linhas:
            perfil = tuple(r[k] for k in g.CAMPOS_PACIENTE)
            self.assertEqual(perfis.setdefault(r["paciente_id"], perfil), perfil)

    def test_10000_por_escrita_incremental(self):
        self.gerar(10000)
        with self.saida.open(encoding="utf-8", newline="") as f:
            leitor = csv.DictReader(f)
            for n, linha in enumerate(leitor, 1):
                self.assertEqual(int(linha["registro_id"]), n)
        self.assertEqual(n, 10000)

    def test_seed_reproduz_dados_sinteticos(self):
        self.gerar(100)
        outra = Path(self.temp.name) / "outro.csv"
        self.gerar(100, saida=outra)
        self.assertEqual(self.saida.read_bytes(), outra.read_bytes())

    def test_seeds_diferentes(self):
        self.gerar()
        antes = self.ler()
        self.gerar(seed=43, saida=Path(self.temp.name) / "outra.csv")
        self.assertNotEqual(antes[0]["paciente_id"], self.ler(Path(self.temp.name) / "outra.csv")[0]["paciente_id"])

    def test_perfil_independe_tamanho_populacao(self):
        self.gerar(100, pacientes=2)
        self.gerar(100, pacientes=5)
        perfis = {}
        for r in self.ler():
            perfil = tuple(r[k] for k in g.CAMPOS_PACIENTE)
            self.assertEqual(perfis.setdefault(r["paciente_id"], perfil), perfil)

    def test_parametros_invalidos_nao_criam_csv(self):
        for parametros in ({"quantidade": 9}, {"quantidade": 0}, {"pacientes": 0},
                           {"inicio": FIM, "fim": INICIO}, {"fim": AGORA.date()}):
            with self.subTest(parametros=parametros), self.assertRaises(ValueError):
                self.gerar(**parametros)
            self.assertFalse(self.saida.exists())

    def test_csv_incompativel_preservado(self):
        self.saida.parent.mkdir()
        self.saida.write_text("id,outra_coluna\n1,abc\n", encoding="utf-8")
        antes = self.saida.read_bytes()
        with self.assertRaises(ValueError):
            self.gerar()
        self.assertEqual(antes, self.saida.read_bytes())

    def test_csv_truncado_preservado(self):
        self.gerar()
        with self.saida.open("a", encoding="utf-8") as f:
            f.write("11,pac_incompleto\n")
        antes = self.saida.read_bytes()
        with self.assertRaises(ValueError):
            self.gerar()
        self.assertEqual(antes, self.saida.read_bytes())

    def test_duplicatas_existentes_rejeitadas(self):
        self.gerar()
        linhas = self.saida.read_text(encoding="utf-8").splitlines()
        with self.saida.open("a", encoding="utf-8") as f:
            f.write(linhas[-1] + "\n")
        antes = self.saida.read_bytes()
        with self.assertRaises(ValueError):
            self.gerar()
        self.assertEqual(antes, self.saida.read_bytes())

    def test_arquivo_vazio(self):
        self.saida.parent.mkdir()
        self.saida.touch()
        self.gerar()
        self.assertEqual(len(self.ler()), 10)

    def test_sem_quebra_final(self):
        self.gerar()
        self.saida.write_bytes(self.saida.read_bytes().rstrip(b"\n"))
        self.gerar()
        self.assertEqual(len(self.ler()), 20)

    def test_bloqueio_entre_processos(self):
        self.gerar()
        antes = self.saida.read_bytes()
        with g.bloquear(self.saida):
            resultado = self.cli()
            self.assertNotEqual(resultado.returncode, 0)
        self.assertEqual(antes, self.saida.read_bytes())

    def test_reversao_apos_falha(self):
        self.gerar()
        antes = self.saida.read_bytes()
        original = g.gerar_registros
        def registros_com_falha(*args):
            yield next(original(10, 99, 5, INICIO, FIM, 11, AGORA))
            raise OSError("Falha de escrita simulada")
        with patch.object(g, "gerar_registros", registros_com_falha), self.assertRaises(OSError):
            self.gerar()
        self.assertEqual(antes, self.saida.read_bytes())
        self.assertFalse(self.saida.with_name(self.saida.name + ".lock").exists())

    def test_cli_fora_do_diretorio_projeto(self):
        resultado = self.cli("--quantidade", "1000", "--seed", "42", cwd=self.temp.name)
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertIn("1000", resultado.stdout)
        self.assertEqual(len(self.ler()), 1000)

    def test_cli_argumentos_invalidos(self):
        for args in (("--quantidade", "9"), ("--quantidade", "abc"),
                     ("--data-inicio", "2026-02-30"), ("--pacientes", "0")):
            with self.subTest(args=args):
                self.assertNotEqual(self.cli(*args).returncode, 0)
                self.assertFalse(self.saida.exists())

    def test_importacao_analitica_sqlite(self):
        self.gerar(1000)
        with sqlite3.connect(":memory:") as con:
            con.execute("CREATE TABLE refeicoes (registro_id INTEGER PRIMARY KEY, imc REAL, kcal REAL)")
            with self.saida.open(encoding="utf-8", newline="") as f:
                con.executemany("INSERT INTO refeicoes VALUES (?, ?, ?)",
                                ((int(r["registro_id"]), float(r["imc"]), float(r["calorias_kcal"]))
                                 for r in csv.DictReader(f)))
            total, media = con.execute("SELECT COUNT(*), AVG(kcal) FROM refeicoes").fetchone()
        self.assertEqual(total, 1000)
        self.assertGreater(media, 0)


if __name__ == "__main__":
    unittest.main()
