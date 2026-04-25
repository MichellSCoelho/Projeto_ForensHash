import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
import sys

# Garante que o módulo core seja encontrado
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.hasher import calcular_hashes
from core.report_builder import gerar_docx, gerar_pdf

# ─── Configurações ────────────────────────────────────────────────────────────
ARQUIVO_CONFIG = os.path.join(os.path.dirname(__file__), "config_perito.json")
COR_FUNDO      = "#1A1A2E"
COR_PAINEL     = "#16213E"
COR_DESTAQUE   = "#0F3460"
COR_ACENTO     = "#E94560"
COR_TEXTO      = "#EAEAEA"
COR_TEXTO2     = "#A0A0B0"
COR_VERDE      = "#4CAF50"
COR_CAMPO      = "#0D1B2A"


# ─── Funções de configuração ──────────────────────────────────────────────────

def salvar_config(dados: dict):
    with open(ARQUIVO_CONFIG, "w") as f:
        json.dump(dados, f, indent=2)

def carregar_config() -> dict:
    if os.path.isfile(ARQUIVO_CONFIG):
        with open(ARQUIVO_CONFIG, "r") as f:
            return json.load(f)
    return {}


# ─── Aplicação Principal ──────────────────────────────────────────────────────

class ForensHashApp:

    def __init__(self, root):
        self.root = root
        self.root.title("ForensHash — Perícia Forense Computacional")
        self.root.geometry("780x780")
        self.root.protocol("WM_DELETE_WINDOW", self.root.destroy)
        self.root.resizable(False, False)
        self.root.configure(bg=COR_FUNDO)

        self.resultado_hash = {}
        self._build_ui()
        self._carregar_dados_perito()

    # ── Interface ──────────────────────────────────────────────────────────────

    def _build_ui(self):

        # ── Título ──────────────────────────────────────────────────────────
        frame_titulo = tk.Frame(self.root, bg=COR_ACENTO, height=60)
        frame_titulo.pack(fill="x")
        frame_titulo.pack_propagate(False)

        tk.Label(
            frame_titulo,
            text="🔍  FORENSHASH — Perícia Forense Computacional",
            font=("Courier New", 14, "bold"),
            bg=COR_ACENTO, fg="white"
        ).pack(expand=True)

        # ── Container principal ──────────────────────────────────────────────
        container = tk.Frame(self.root, bg=COR_FUNDO, padx=20, pady=15)
        container.pack(fill="both", expand=True)

        # ── Seção: Dados do Perito ───────────────────────────────────────────
        self._secao(container, "👤  DADOS DO PERITO")

        frame_perito = tk.Frame(container, bg=COR_PAINEL, padx=15, pady=12)
        frame_perito.pack(fill="x", pady=(0, 12))

        # Nome
        tk.Label(frame_perito, text="Nome do Perito", font=("Courier New", 9),
                 bg=COR_PAINEL, fg=COR_TEXTO2).grid(row=0, column=0, sticky="w")
        self.entry_nome = self._entry(frame_perito)
        self.entry_nome.grid(row=1, column=0, sticky="ew", padx=(0, 10), pady=(2, 8))

        # Registro
        tk.Label(frame_perito, text="Registro / Matrícula", font=("Courier New", 9),
                 bg=COR_PAINEL, fg=COR_TEXTO2).grid(row=0, column=1, sticky="w")
        self.entry_registro = self._entry(frame_perito)
        self.entry_registro.grid(row=1, column=1, sticky="ew", pady=(2, 8))

        # Instituição
        tk.Label(frame_perito, text="Instituição", font=("Courier New", 9),
                 bg=COR_PAINEL, fg=COR_TEXTO2).grid(row=2, column=0, sticky="w")
        self.entry_instituicao = self._entry(frame_perito)
        self.entry_instituicao.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(2, 4))

        frame_perito.columnconfigure(0, weight=1)
        frame_perito.columnconfigure(1, weight=1)

        # Botão salvar perito
        tk.Button(
            frame_perito,
            text="💾  Salvar dados do perito",
            font=("Courier New", 9),
            bg=COR_DESTAQUE, fg=COR_TEXTO,
            relief="flat", cursor="hand2",
            command=self._salvar_perito
        ).grid(row=4, column=0, columnspan=2, sticky="e", pady=(6, 0))

        # ── Seção: Caso e Arquivo ────────────────────────────────────────────
        self._secao(container, "📁  CASO E EVIDÊNCIA")

        frame_caso = tk.Frame(container, bg=COR_PAINEL, padx=15, pady=12)
        frame_caso.pack(fill="x", pady=(0, 12))

        # Número do caso
        tk.Label(frame_caso, text="Número do Caso", font=("Courier New", 9),
                 bg=COR_PAINEL, fg=COR_TEXTO2).grid(row=0, column=0, sticky="w")
        self.entry_caso = self._entry(frame_caso, placeholder="Ex: 2026/IPFA/001")
        self.entry_caso.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(2, 10))

        # Arquivo
        tk.Label(frame_caso, text="Arquivo de Evidência", font=("Courier New", 9),
                 bg=COR_PAINEL, fg=COR_TEXTO2).grid(row=2, column=0, sticky="w")

        frame_arquivo = tk.Frame(frame_caso, bg=COR_PAINEL)
        frame_arquivo.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(2, 0))

        self.entry_arquivo = self._entry(frame_arquivo)
        self.entry_arquivo.pack(side="left", fill="x", expand=True, padx=(0, 8))

        tk.Button(
            frame_arquivo,
            text="📂  Selecionar",
            font=("Courier New", 9),
            bg=COR_DESTAQUE, fg=COR_TEXTO,
            relief="flat", cursor="hand2",
            command=self._selecionar_arquivo
        ).pack(side="right")

        frame_caso.columnconfigure(0, weight=1)

        # ── Botão calcular hash ──────────────────────────────────────────────
        tk.Button(
            container,
            text="⚡  CALCULAR HASH",
            font=("Courier New", 11, "bold"),
            bg=COR_ACENTO, fg="white",
            relief="flat", cursor="hand2",
            pady=10,
            command=self._calcular_hash
        ).pack(fill="x", pady=(0, 12))

        # ── Seção: Resultados ────────────────────────────────────────────────
        self._secao(container, "🔑  VALORES DE HASH")

        frame_hash = tk.Frame(container, bg=COR_PAINEL, padx=15, pady=12)
        frame_hash.pack(fill="x", pady=(0, 12))

        self.labels_hash = {}
        algoritmos = [("MD5", "md5"), ("SHA-1", "sha1"), ("SHA-256", "sha256")]

        for i, (label, chave) in enumerate(algoritmos):
            tk.Label(frame_hash, text=f"{label}:", font=("Courier New", 9, "bold"),
                     bg=COR_PAINEL, fg=COR_ACENTO, width=8, anchor="w"
                     ).grid(row=i, column=0, sticky="w", pady=3)

            var = tk.StringVar(value="—")
            self.labels_hash[chave] = var

            tk.Label(frame_hash, textvariable=var,
                     font=("Courier New", 9),
                     bg=COR_PAINEL, fg=COR_VERDE,
                     anchor="w"
                     ).grid(row=i, column=1, sticky="w", padx=(8, 0))

        # ── Botões gerar laudo ───────────────────────────────────────────────
        frame_botoes = tk.Frame(container, bg=COR_FUNDO)
        frame_botoes.pack(fill="x", pady=(4, 0))

        tk.Button(
            frame_botoes,
            text="📄  Gerar Laudo Word",
            font=("Courier New", 10, "bold"),
            bg="#1B5E20", fg="white",
            relief="flat", cursor="hand2",
            pady=8,
            command=lambda: self._gerar_laudo("docx")
        ).pack(side="left", fill="x", expand=True, padx=(0, 6))

        tk.Button(
            frame_botoes,
            text="📕  Gerar Laudo PDF",
            font=("Courier New", 10, "bold"),
            bg="#B71C1C", fg="white",
            relief="flat", cursor="hand2",
            pady=8,
            command=lambda: self._gerar_laudo("pdf")
        ).pack(side="right", fill="x", expand=True)

        # ── Barra de status ──────────────────────────────────────────────────
        self.status_var = tk.StringVar(value="Pronto.")
        tk.Label(
            self.root,
            textvariable=self.status_var,
            font=("Courier New", 9),
            bg=COR_DESTAQUE, fg=COR_TEXTO2,
            anchor="w", padx=12, pady=5
        ).pack(fill="x", side="bottom")

    # ── Helpers de UI ──────────────────────────────────────────────────────────

    def _secao(self, parent, texto):
        tk.Label(
            parent, text=texto,
            font=("Courier New", 10, "bold"),
            bg=COR_FUNDO, fg=COR_TEXTO2
        ).pack(anchor="w", pady=(4, 4))

    def _entry(self, parent, placeholder=""):
        e = tk.Entry(
            parent,
            font=("Courier New", 10),
            bg=COR_CAMPO, fg=COR_TEXTO,
            insertbackground=COR_TEXTO,
            relief="flat",
            bd=6
        )
        if placeholder:
            e.insert(0, placeholder)
            e.config(fg=COR_TEXTO2)
            e.bind("<FocusIn>",  lambda ev, en=e, ph=placeholder: self._clear_ph(ev, en, ph))
            e.bind("<FocusOut>", lambda ev, en=e, ph=placeholder: self._restore_ph(ev, en, ph))
        return e

    def _clear_ph(self, event, entry, placeholder):
        if entry.get() == placeholder:
            entry.delete(0, tk.END)
            entry.config(fg=COR_TEXTO)

    def _restore_ph(self, event, entry, placeholder):
        if not entry.get():
            entry.insert(0, placeholder)
            entry.config(fg=COR_TEXTO2)

    # ── Ações ──────────────────────────────────────────────────────────────────

    def _carregar_dados_perito(self):
        config = carregar_config()
        if config:
            self.entry_nome.insert(0, config.get("nome", ""))
            self.entry_registro.insert(0, config.get("registro", ""))
            self.entry_instituicao.insert(0, config.get("instituicao", ""))
            self._status(f"✅ Dados do perito carregados: {config.get('nome', '')}")

    def _salvar_perito(self):
        dados = {
            "nome":       self.entry_nome.get().strip(),
            "registro":   self.entry_registro.get().strip(),
            "instituicao":self.entry_instituicao.get().strip(),
        }
        salvar_config(dados)
        self._status("💾 Dados do perito salvos com sucesso!")
        messagebox.showinfo("Salvo", "Dados do perito salvos com sucesso!")

    def _selecionar_arquivo(self):
        caminho = filedialog.askopenfilename(title="Selecione o arquivo de evidência")
        if caminho:
            self.entry_arquivo.delete(0, tk.END)
            self.entry_arquivo.insert(0, caminho)
            self.resultado_hash = {}
            for chave in self.labels_hash:
                self.labels_hash[chave].set("—")
            self._status(f"📂 Arquivo selecionado: {os.path.basename(caminho)}")

    def _calcular_hash(self):
        arquivo = self.entry_arquivo.get().strip()

        if not arquivo or not os.path.isfile(arquivo):
            messagebox.showerror("Erro", "Selecione um arquivo válido antes de calcular.")
            return

        self._status("⏳ Calculando hashes... aguarde.")
        self.root.update()

        try:
            self.resultado_hash = calcular_hashes(arquivo)
            self.labels_hash["md5"].set(self.resultado_hash["md5"])
            self.labels_hash["sha1"].set(self.resultado_hash["sha1"])
            self.labels_hash["sha256"].set(self.resultado_hash["sha256"])
            self._status(f"✅ Hashes calculados: {self.resultado_hash['arquivo']}")
        except Exception as e:
            messagebox.showerror("Erro", str(e))
            self._status("❌ Erro ao calcular hash.")

    def _gerar_laudo(self, formato: str):
        if not self.resultado_hash:
            messagebox.showerror("Erro", "Calcule o hash de um arquivo antes de gerar o laudo.")
            return

        dados_perito = {
            "nome":        self.entry_nome.get().strip(),
            "registro":    self.entry_registro.get().strip(),
            "instituicao": self.entry_instituicao.get().strip(),
        }
        numero_caso = self.entry_caso.get().strip()

        if not numero_caso or numero_caso == "Ex: 2026/IPFA/001":
            messagebox.showerror("Erro", "Informe o número do caso.")
            return

        if not dados_perito["nome"]:
            messagebox.showerror("Erro", "Informe o nome do perito.")
            return

        output_dir = os.path.join(os.path.dirname(__file__), "..", "laudos")

        try:
            self._status(f"⏳ Gerando laudo {formato.upper()}...")
            self.root.update()

            if formato == "docx":
                caminho = gerar_docx(self.resultado_hash, dados_perito, numero_caso, output_dir)
            else:
                caminho = gerar_pdf(self.resultado_hash, dados_perito, numero_caso, output_dir)

            self._status(f"✅ Laudo gerado: {os.path.basename(caminho)}")
            messagebox.showinfo(
                "Laudo gerado!",
                f"Arquivo salvo em:\n{os.path.abspath(caminho)}"
            )
        except Exception as e:
            messagebox.showerror("Erro ao gerar laudo", str(e))
            self._status("❌ Erro ao gerar laudo.")

    def _status(self, mensagem: str):
        self.status_var.set(mensagem)
        self.root.update()


# ─── Inicialização ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    root = tk.Tk()
    app = ForensHashApp(root)
    root.mainloop()