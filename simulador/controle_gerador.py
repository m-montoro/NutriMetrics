"""Liga e desliga a geração automática de dados."""

import argparse
import json
import os
from pathlib import Path
import sys
import time
from datetime import datetime, timedelta

import gerador_dados as gerador


class Controle:
    def __init__(self, saida):
        self.pasta = saida.parent / (saida.name + ".controle")
        self.pasta.mkdir(parents=True, exist_ok=True)
        self.parada = self.pasta / "parar"
        self.estado = self.pasta / "estado.json"
        self.arquivo = None

    def adquirir(self):
        self.arquivo = (self.pasta / "execucao.lock").open("a+b")
        self.arquivo.seek(0, 2)
        if self.arquivo.tell() == 0:
            self.arquivo.write(b"0")
            self.arquivo.flush()
        self.arquivo.seek(0)
        try:
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(self.arquivo.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(self.arquivo, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            self.arquivo.close()
            self.arquivo = None
            return False
        return True

    def liberar(self):
        if self.arquivo:
            self.arquivo.close()
            self.arquivo = None

    def salvar(self, **dados):
        temporario = self.estado.with_suffix(".tmp")
        temporario.write_text(json.dumps(dados, ensure_ascii=False), encoding="utf-8")
        temporario.replace(self.estado)


def positivo(texto):
    valor = float(texto)
    if not 0.1 <= valor <= 86400:
        raise argparse.ArgumentTypeError("Use um intervalo entre 0.1 e 86400 segundos.")
    return valor


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("acao", choices=("ligar", "desligar", "status"))
    parser.add_argument("--quantidade", type=int, default=10, help="Registros por rodada (mínimo 10).")
    parser.add_argument("--saida", type=Path, default=gerador.SAIDA_PADRAO)
    parser.add_argument("--pacientes", type=int, default=100)
    parser.add_argument("--intervalo-segundos", type=positivo, default=300,
                        help="Intervalo entre rodadas; padrão: 300 segundos (5 minutos).")
    args = parser.parse_args(argv)
    if args.quantidade < 10 or args.pacientes < 1:
        parser.error("A quantidade mínima é 10 e o número de pacientes deve ser positivo.")
    saida = args.saida.expanduser().resolve()
    controle = Controle(saida)
    adquirido = controle.adquirir()
    if args.acao != "ligar":
        try:
            if adquirido:
                print("Gerador desligado.")
            elif args.acao == "desligar":
                controle.parada.touch()
                print("Parada solicitada. O gerador encerra após terminar a rodada atual.")
            else:
                print("Gerador ligado.")
                try:
                    print(controle.estado.read_text(encoding="utf-8"))
                except (OSError, ValueError):
                    print("Inicializando; consulte novamente em instantes.")
        finally:
            controle.liberar()
        return 0
    if not adquirido:
        print("Já existe um gerador ligado para esse CSV.", file=sys.stderr)
        return 1
    rodadas = 0
    try:
        controle.parada.unlink(missing_ok=True)
        print(f"Gerador ligado: {args.quantidade} registros por rodada, a cada {args.intervalo_segundos:g} segundos.", flush=True)
        print(f"CSV: {saida}\nMantenha este terminal aberto. Ctrl+C também desliga.", flush=True)
        proxima = time.monotonic()
        while not controle.parada.exists():
            restante = proxima - time.monotonic()
            if restante > 0:
                time.sleep(min(restante, 0.25))
                continue
            inicio = time.monotonic()
            ontem = datetime.now(gerador.FUSO_REFEICOES).date() - timedelta(days=1)
            # Cada rodada usa uma nova semente para variar os dados.
            seed = gerador.executar(args.quantidade, saida, None, args.pacientes,
                                    ontem - timedelta(days=29), ontem)
            rodadas += 1
            controle.salvar(quantidade=args.quantidade, intervalo_segundos=args.intervalo_segundos,
                            rodadas=rodadas, ultima_geracao=datetime.now().astimezone().isoformat(),
                            seed=seed, saida=str(saida))
            print(f"Rodada {rodadas}: {args.quantidade} registros gravados.", flush=True)
            # Se uma rodada demorar demais, não acumula rodadas atrasadas.
            proxima = max(inicio + args.intervalo_segundos, time.monotonic())
    except KeyboardInterrupt:
        print("Parada pelo teclado.")
    except (OSError, ValueError, gerador.csv.Error) as erro:
        print(f"Erro: {erro}", file=sys.stderr)
        return 1
    finally:
        controle.liberar()
    print("Gerador desligado.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
