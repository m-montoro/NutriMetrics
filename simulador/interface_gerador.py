"""Uma janela simples para controlar o gerador."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tkinter as tk
from tkinter import messagebox

from controle_gerador import Controle, encontrar_r
from gerador_dados import SAIDA_PADRAO

RAIZ = Path(__file__).resolve().parents[1]


class Interface:
    def __init__(self, janela):
        self.janela = janela
        self.processo = None
        self.log = None
        self.fechando = False
        self.parando = False
        janela.title("NutriMetrics")
        janela.geometry("460x390")
        janela.resizable(False, False)
        janela.configure(bg="#F6F7F9")
        janela.protocol("WM_DELETE_WINDOW", self.fechar)
        painel = tk.Frame(janela, bg="#F6F7F9", padx=30, pady=25)
        painel.pack(fill="both", expand=True)
        def texto(conteudo, tamanho=11, cor="#626873"):
            item = tk.Label(painel, text=conteudo, bg="#F6F7F9", fg=cor,
                            font=("Segoe UI", tamanho), anchor="w")
            item.pack(fill="x", pady=(0, 10))
            return item
        texto("NutriMetrics", 23, "#20262E")
        texto("Geração de dados simulados")
        texto("Registros por rodada", 10)
        self.quantidade = tk.Entry(painel, font=("Segoe UI", 15), relief="solid", bd=1)
        self.quantidade.insert(0, "100")
        self.quantidade.pack(fill="x", ipady=7, pady=(0, 12))
        texto("A cada 5 minutos · organização automática pelo R", 10)
        botoes = tk.Frame(painel, bg="#F6F7F9")
        botoes.pack(fill="x", pady=(3, 16))
        self.ligar = tk.Button(botoes, text="Ligar", command=self.iniciar,
                              bg="#28634E", fg="white", relief="flat", bd=0,
                              font=("Segoe UI", 11), pady=9)
        self.ligar.pack(side="left", fill="x", expand=True, padx=(0, 6))
        self.desligar = tk.Button(botoes, text="Desligar", command=self.parar,
                                 relief="flat", bd=0, bg="#E4E7EB",
                                 font=("Segoe UI", 11), pady=9)
        self.desligar.pack(side="left", fill="x", expand=True, padx=(6, 0))
        self.status = texto("Verificando…", 11, "#20262E")
        self.detalhe = texto("", 10)
        tk.Button(painel, text="Abrir pasta dos CSVs", command=self.abrir_pasta,
                  relief="flat", bg="#F6F7F9", fg="#28634E",
                  font=("Segoe UI", 10), cursor="hand2").pack(anchor="w")
        self.atualizar()

    def ativo(self):
        controle = Controle(SAIDA_PADRAO)
        try:
            return not controle.adquirir()
        finally:
            controle.liberar()

    def iniciar(self):
        try:
            quantidade = int(self.quantidade.get())
            if quantidade < 10:
                raise ValueError("Informe pelo menos 10 registros.")
            encontrar_r()
            if self.ativo():
                return
            pasta = Controle(SAIDA_PADRAO).pasta
            self.log = (pasta / "interface.log").open("w", encoding="utf-8")
            executavel = Path(sys.executable)
            if executavel.name.lower() == "pythonw.exe":
                executavel = executavel.with_name("python.exe")
            self.processo = subprocess.Popen(
                [str(executavel), str(RAIZ / "simulador/controle_gerador.py"),
                 "ligar", "--quantidade", str(quantidade), "--filtrar"],
                cwd=RAIZ, stdout=self.log, stderr=subprocess.STDOUT,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
            self.parando = False
            self.ligar.config(state="disabled")
        except (ValueError, OSError) as erro:
            if self.log:
                self.log.close()
                self.log = None
            messagebox.showerror("Não foi possível ligar", str(erro), parent=self.janela)

    def parar(self):
        if self.ativo() or (self.processo and self.processo.poll() is None):
            Controle(SAIDA_PADRAO).parada.touch()
            self.parando = True

    def atualizar(self):
        try:
            ligado = self.ativo()
            iniciando = self.processo is not None and self.processo.poll() is None
            ocupado = ligado or iniciando
            if self.processo and self.processo.poll() is not None:
                codigo = self.processo.returncode
                self.processo = None
                if self.log:
                    self.log.close()
                    self.log = None
                if codigo:
                    registro = Controle(SAIDA_PADRAO).pasta / "interface.log"
                    mensagem = registro.read_text(encoding="utf-8", errors="replace")[-1800:]
                    messagebox.showerror("O gerador parou", mensagem, parent=self.janela)
            # Repete o pedido se a janela foi fechada durante a inicializacao.
            if self.parando and ocupado:
                Controle(SAIDA_PADRAO).parada.touch()
            self.ligar.config(state="disabled" if ocupado or self.fechando else "normal")
            self.desligar.config(state="normal" if ocupado and not self.parando else "disabled")
            self.quantidade.config(state="disabled" if ocupado else "normal")
            titulo = "Desligado"
            detalhe = "Pronto para gerar."
            if ocupado:
                titulo = "Encerrando após a rodada…" if self.parando else "Ligado"
                detalhe = "Iniciando…"
                try:
                    dados = json.loads(Controle(SAIDA_PADRAO).estado.read_text(encoding="utf-8"))
                    etapa = "Organizando no R" if dados.get("etapa") == "filtrando" else "Aguardando próxima rodada"
                    detalhe = f"{etapa} · rodada {dados.get('rodadas', 0)}"
                except (OSError, ValueError):
                    pass
            else:
                self.parando = False
            self.status.config(text=titulo)
            self.detalhe.config(text=detalhe)
            if self.fechando and not ocupado:
                self.janela.destroy()
                return
        except OSError as erro:
            self.status.config(text="Não foi possível consultar o gerador")
            self.detalhe.config(text=str(erro)[:55])
        self.janela.after(700, self.atualizar)

    def abrir_pasta(self):
        pasta = RAIZ / "dados"
        pasta.mkdir(exist_ok=True)
        if os.name == "nt":
            os.startfile(pasta)
        else:
            subprocess.Popen(["xdg-open", str(pasta)])

    def fechar(self):
        self.fechando = True
        self.parar()


if __name__ == "__main__":
    janela = tk.Tk()
    Interface(janela)
    janela.mainloop()
