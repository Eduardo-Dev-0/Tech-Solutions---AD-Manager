import customtkinter as ctk
from tkinter import ttk, filedialog, messagebox
import tkinter as tk
import pandas as pd
import threading
import re
import socket
import os
import sys
import datetime
from PIL import Image
from unidecode import unidecode
from pyad import adquery, aduser, adcontainer, pyad

# =============================
# RESOURCE PATH
# =============================

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# =============================
# ICONES
# =============================

icon_excel    = ctk.CTkImage(Image.open(resource_path("icons/selecionar.ico")),  size=(20,20))
icon_verificar= ctk.CTkImage(Image.open(resource_path("icons/verificar.ico")),   size=(20,20))
icon_criar    = ctk.CTkImage(Image.open(resource_path("icons/criar.ico")),        size=(20,20))
icon_desativar= ctk.CTkImage(Image.open(resource_path("icons/desativar.ico")),    size=(20,20))
icon_ativar   = ctk.CTkImage(Image.open(resource_path("icons/ativar.ico")),       size=(20,20))
icon_remover  = ctk.CTkImage(Image.open(resource_path("icons/remover.ico")),      size=(20,20))

# =============================
# TEMA
# =============================

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# =============================
# PALETA DE CORES
# =============================

COR_PRIMARIA   = "#039BF4"
COR_HOVER      = "#0275C2"
COR_SECUNDARIA = "#0275C2"
COR_SEC_HOVER  = "#015EA0"
COR_NEUTRO     = "#0D2137"
COR_NEU_HOVER  = "#081624"
COR_FUNDO_LOG  = "#010716"
COR_FUNDO_LIST = "#010E1E"
COR_OK         = "#4CAF50"
COR_ERRO       = "#F44336"
COR_AVISO      = "#FFA726"

# =============================
# APP
# =============================

app = ctk.CTk()
app.title("Tech Solutions - AD Manager")
app.geometry("1280x900")

try:
    app.iconbitmap(resource_path("icons/icone_ad_manager.ico"))
except Exception as e:
    print("Erro ao carregar ícone:", e)

# =============================
# ESTADO GLOBAL
# =============================

excel_path  = ""
DOMINIO     = ""
OU_USUARIOS = ""

CHECKED   = "☑"
UNCHECKED = "☐"

# =============================
# CONFIGURAÇÕES DE LOGIN E SENHA
# =============================

# Blocos disponíveis para montar o formato
BLOCOS_LOGIN = [
    "primeiro_nome",
    "ultimo_nome",
    "todos_nomes",
    "cpf_4",
    "cpf_6",
    "cpf_completo",
    "matricula",
]

BLOCOS_SENHA = [
    "cpf_completo",
    "cpf_4",
    "primeiro_nome",
    "ultimo_nome",
    "senha_fixa",
]

# Configuração ativa (pode ser alterada pelo usuário)
config_login = {
    "blocos":    ["primeiro_nome", "ultimo_nome", "cpf_4"],
    "separador": "",           # "" | "." | "_"
}

config_senha = {
    "blocos":      ["cpf_completo"],
    "senha_fixa":  "Tech@2026",    # usado somente se bloco "senha_fixa" estiver ativo
}

# =============================
# GERAÇÃO DE LOGIN / SENHA
# =============================

def remover_acentos(texto):
    return unidecode(str(texto))

def limpar_cpf(cpf):
    return re.sub(r'\D', '', str(cpf))

def _resolver_bloco_login(bloco, nome, cpf):
    partes = nome.strip().split()
    primeiro = remover_acentos(partes[0]).lower()   if partes else ""
    ultimo   = remover_acentos(partes[-1]).lower()  if partes else ""
    todos    = remover_acentos("".join(partes)).lower()
    cpf_lp   = limpar_cpf(cpf)
    mapa = {
        "primeiro_nome": primeiro,
        "ultimo_nome":   ultimo,
        "todos_nomes":   todos,
        "cpf_4":         cpf_lp[:4],
        "cpf_6":         cpf_lp[:6],
        "cpf_completo":  cpf_lp,
        "matricula":     "",          # preenchido na hora se disponível
    }
    return mapa.get(bloco, "")

def gerar_login(nome, cpf, matricula=""):
    sep    = config_login["separador"]
    partes = []
    for bloco in config_login["blocos"]:
        val = _resolver_bloco_login(bloco, nome, cpf)
        if bloco == "matricula":
            val = remover_acentos(matricula).lower()
        if val:
            partes.append(val)
    login = sep.join(partes)
    if len(login) > 20:
        login_orig = login
        login = login[:20]
        adicionar_log(f"⚠ Login ajustado (limite 20 chars): {login_orig} → {login}", "aviso")
    return login

def _resolver_bloco_senha(bloco, nome, cpf):
    partes = nome.strip().split()
    primeiro = remover_acentos(partes[0]).lower() if partes else ""
    ultimo   = remover_acentos(partes[-1]).lower() if partes else ""
    cpf_lp   = limpar_cpf(cpf)
    mapa = {
        "cpf_completo": cpf_lp,
        "cpf_4":        cpf_lp[:4],
        "primeiro_nome":primeiro,
        "ultimo_nome":  ultimo,
        "senha_fixa":   config_senha["senha_fixa"],
    }
    return mapa.get(bloco, "")

def gerar_senha(nome, cpf):
    partes = []
    for bloco in config_senha["blocos"]:
        val = _resolver_bloco_senha(bloco, nome, cpf)
        if val:
            partes.append(val)
    return "".join(partes) or limpar_cpf(cpf)

# =============================
# VALIDAÇÃO DE CPF (dígitos verificadores)
# =============================

def validar_cpf_matematico(cpf_str):
    cpf = limpar_cpf(cpf_str)
    if len(cpf) != 11:
        return False
    if cpf == cpf[0] * 11:          # sequências iguais
        return False
    # Primeiro dígito verificador
    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    d1   = (soma * 10 % 11) % 10
    if d1 != int(cpf[9]):
        return False
    # Segundo dígito verificador
    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    d2   = (soma * 10 % 11) % 10
    return d2 == int(cpf[10])

def validar_linha(nome, cpf, linha_num):
    erros = []
    # Nome
    if not nome or nome.lower() in ("nan", ""):
        erros.append(f"Linha {linha_num}: Nome vazio ou inválido ('{nome}')")
    else:
        partes = nome.strip().split()
        if len(partes) < 2:
            erros.append(
                f"Linha {linha_num}: Nome '{nome}' incompleto "
                f"— necessário ao menos primeiro e último nome"
            )
    # CPF — dígitos verificadores
    cpf_limpo = limpar_cpf(cpf)
    if len(cpf_limpo) != 11:
        erros.append(
            f"Linha {linha_num}: CPF '{cpf}' inválido "
            f"— deve conter 11 dígitos (encontrado: {len(cpf_limpo)})"
        )
    elif not validar_cpf_matematico(cpf):
        erros.append(
            f"Linha {linha_num}: CPF '{cpf}' inválido "
            f"— dígitos verificadores incorretos"
        )
    return erros

# =============================
# LOG COM CORES
# =============================

def adicionar_log(msg, tipo="info"):
    """
    tipo: "info" | "ok" | "aviso" | "erro"
    """
    cores = {
        "info":  "white",
        "ok":    "#66BB6A",
        "aviso": "#FFA726",
        "erro":  "#EF5350",
    }
    cor = cores.get(tipo, "white")

    log_box.configure(state="normal")
    log_box.insert(tk.END, msg + "\n", tipo)
    log_box.tag_configure(tipo, foreground=cor)
    log_box.see(tk.END)
    log_box.configure(state="disabled")
    atualizar_rodape()

def limpar_log():
    log_box.configure(state="normal")
    log_box.delete("1.0", tk.END)
    log_box.configure(state="disabled")

def exportar_log():
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho = filedialog.asksaveasfilename(
        defaultextension=".txt",
        initialfile=f"log_admanager_{agora}.txt",
        filetypes=[("Texto", "*.txt")]
    )
    if caminho:
        conteudo = log_box.get("1.0", tk.END)
        with open(caminho, "w", encoding="utf-8") as f:
            f.write(conteudo)
        adicionar_log(f"✔ Log exportado: {caminho}", "ok")

# =============================
# RODAPÉ / CONTADOR
# =============================

def atualizar_rodape():
    total     = len(table.get_children())
    selecionados = len(itens_selecionados()) if 'table' in globals() else 0
    criados   = sum(1 for i in table.get_children() if "Criado"    in str(table.item(i,"values")))
    erros_tb  = sum(1 for i in table.get_children() if "⚠ Erro"   in str(table.item(i,"values")))
    label_rodape.configure(
        text=f"Total: {total}  |  Selecionados: {selecionados}  |  Criados: {criados}  |  Erros: {erros_tb}"
    )

# =============================
# BARRA DE PROGRESSO
# =============================

def iniciar_progresso(total):
    progress_bar.configure(mode="determinate")
    progress_bar.set(0)
    label_progresso.configure(text=f"0 / {total}")
    frame_progresso.pack(fill="x", padx=20, pady=(0,4))
    app.update_idletasks()

def atualizar_progresso(atual, total):
    if total > 0:
        progress_bar.set(atual / total)
    label_progresso.configure(text=f"{atual} / {total}")
    app.update_idletasks()

def finalizar_progresso():
    frame_progresso.pack_forget()

# =============================
# DETECÇÃO AUTOMÁTICA DE DOMÍNIO
# =============================

def detectar_dominio():
    global DOMINIO
    try:
        fqdn   = socket.getfqdn()
        partes = fqdn.split(".")
        if len(partes) >= 2:
            DOMINIO = ".".join(partes[1:])
            pyad.set_defaults(ldap_server=DOMINIO)
            label_dominio.configure(text=f"Domínio: {DOMINIO}", text_color=COR_OK)
            adicionar_log(f"✔ Domínio detectado: {DOMINIO}", "ok")
            btn_selecionar_ou.configure(state="normal")
        else:
            raise ValueError("FQDN sem domínio suficiente")
    except Exception as e:
        DOMINIO = ""
        label_dominio.configure(text="❌ Domínio não detectado", text_color=COR_ERRO)
        adicionar_log(f"✖ Erro ao detectar domínio: {e}", "erro")
        btn_selecionar_ou.configure(state="disabled")

# =============================
# LISTAR OUs
# =============================

def listar_ous():
    ous = []
    try:
        q = adquery.ADQuery()
        q.execute_query(
            attributes=["distinguishedName","name"],
            where_clause="objectClass = 'organizationalUnit'"
        )
        for r in q.get_results():
            ous.append(r["distinguishedName"])
    except Exception as e:
        adicionar_log(f"✖ Erro ao listar OUs: {e}", "erro")
    return sorted(ous)

# =============================
# JANELA — SELECIONAR OU
# =============================

def abrir_selecao_ou():
    global OU_USUARIOS
    if not DOMINIO:
        messagebox.showwarning("Domínio não detectado", "Detecte o domínio antes de selecionar a OU.")
        return
    adicionar_log("🔍 Consultando OUs...", "info")
    ous = listar_ous()
    if not ous:
        messagebox.showerror("Sem OUs", "Nenhuma OU encontrada.\nVerifique as permissões.")
        adicionar_log("✖ Nenhuma OU encontrada.", "erro")
        return

    win = ctk.CTkToplevel(app)
    win.title("Selecionar Unidade Organizacional (OU)")
    win.geometry("700x500")
    win.grab_set()

    ctk.CTkLabel(win, text="Selecione a OU de destino:", font=("Arial",13,"bold")).pack(padx=20, pady=(15,5))

    frame_busca = ctk.CTkFrame(win)
    frame_busca.pack(fill="x", padx=20, pady=(0,8))
    ctk.CTkLabel(frame_busca, text="Filtrar:").pack(side="left", padx=(8,4))
    entry_busca = ctk.CTkEntry(frame_busca, width=440)
    entry_busca.pack(side="left", padx=4)

    frame_lista = ctk.CTkFrame(win)
    frame_lista.pack(fill="both", expand=True, padx=20)
    scrollbar = tk.Scrollbar(frame_lista)
    scrollbar.pack(side="right", fill="y")
    listbox = tk.Listbox(
        frame_lista, yscrollcommand=scrollbar.set,
        bg=COR_FUNDO_LIST, fg="white", selectbackground=COR_SECUNDARIA,
        font=("Consolas",10), activestyle="none", borderwidth=0, highlightthickness=0
    )
    listbox.pack(fill="both", expand=True)
    scrollbar.config(command=listbox.yview)

    def popular(filtro=""):
        listbox.delete(0, tk.END)
        for ou in ous:
            if filtro.lower() in ou.lower():
                listbox.insert(tk.END, ou)

    popular()
    entry_busca.bind("<KeyRelease>", lambda *_: popular(entry_busca.get()))

    lbl_sel = ctk.CTkLabel(win, text="Nenhuma OU selecionada", text_color="gray", wraplength=660)
    lbl_sel.pack(padx=20, pady=6)

    listbox.bind("<<ListboxSelect>>", lambda *_: lbl_sel.configure(
        text=listbox.get(listbox.curselection()[0]) if listbox.curselection() else "—",
        text_color=COR_OK
    ))

    def confirmar():
        global OU_USUARIOS
        sel = listbox.curselection()
        if not sel:
            messagebox.showwarning("Atenção","Selecione uma OU.", parent=win)
            return
        OU_USUARIOS = listbox.get(sel[0])
        label_ou.configure(text=f"OU: {OU_USUARIOS}", text_color=COR_OK)
        adicionar_log(f"✔ OU selecionada: {OU_USUARIOS}", "ok")
        win.destroy()

    listbox.bind("<Double-Button-1>", lambda e: confirmar())
    ctk.CTkButton(win, text="Confirmar", fg_color=COR_SECUNDARIA, hover_color=COR_SEC_HOVER, command=confirmar).pack(pady=(4,15))

# =============================
# JANELA — CONFIGURAÇÕES DE LOGIN E SENHA
# =============================

LABEL_BLOCOS = {
    "primeiro_nome": "Primeiro Nome",
    "ultimo_nome":   "Último Nome",
    "todos_nomes":   "Todos os Nomes",
    "cpf_4":         "CPF (4 dígitos)",
    "cpf_6":         "CPF (6 dígitos)",
    "cpf_completo":  "CPF completo",
    "matricula":     "Matrícula",
    "senha_fixa":    "Senha Fixa",
}

def abrir_configuracoes():
    win = ctk.CTkToplevel(app)
    win.title("Configurações de Login e Senha")
    win.geometry("700x620")
    win.grab_set()

    ctk.CTkLabel(win, text="⚙ Configurações de Geração", font=("Arial",15,"bold")).pack(pady=(15,5))
    ctk.CTkLabel(win, text="Monte o formato de login e senha arrastando os blocos ou usando os controles abaixo.",
                 text_color="gray", wraplength=660).pack(pady=(0,10))

    # ---------- SEPARADOR DE LOGIN ----------
    frame_sep = ctk.CTkFrame(win)
    frame_sep.pack(fill="x", padx=20, pady=(0,8))
    ctk.CTkLabel(frame_sep, text="Separador de Login:", width=160, anchor="w").pack(side="left", padx=8)
    sep_var = tk.StringVar(value=config_login["separador"] or "nenhum")
    for txt, val in [("Nenhum",""), ("Ponto (.)","." ), ("Underline (_)","_")]:
        ctk.CTkRadioButton(frame_sep, text=txt, variable=sep_var, value=val).pack(side="left", padx=6)

    # ---------- BLOCOS DE LOGIN ----------
    ctk.CTkLabel(win, text="Blocos do Login (ordem importa):", font=("Arial",12,"bold"), anchor="w").pack(fill="x", padx=20)

    frame_login_blocos = ctk.CTkFrame(win)
    frame_login_blocos.pack(fill="x", padx=20, pady=(4,10))

    login_checks = {}
    login_order  = list(config_login["blocos"])

    def rebuild_login_preview():
        # preview com nome/cpf de exemplo
        nome_ex = "Maria Santos"
        cpf_ex  = "12345678901"
        blocos_ativos = [b for b in BLOCOS_LOGIN if login_checks.get(b, tk.BooleanVar()).get() and b != "matricula"]
        sep = "" if sep_var.get() == "nenhum" else sep_var.get()
        partes = [_resolver_bloco_login(b, nome_ex, cpf_ex) for b in blocos_ativos]
        preview = sep.join(p for p in partes if p)
        lbl_login_prev.configure(text=f"Preview: {preview or '—'}")

    row_l = 0
    col_l = 0
    for bloco in BLOCOS_LOGIN:
        var = tk.BooleanVar(value=(bloco in config_login["blocos"]))
        login_checks[bloco] = var
        cb = ctk.CTkCheckBox(frame_login_blocos, text=LABEL_BLOCOS[bloco], variable=var,
                              command=rebuild_login_preview)
        cb.grid(row=row_l, column=col_l, padx=12, pady=4, sticky="w")
        col_l += 1
        if col_l > 2:
            col_l = 0
            row_l += 1

    lbl_login_prev = ctk.CTkLabel(win, text="Preview: —", text_color=COR_PRIMARIA, font=("Consolas",12))
    lbl_login_prev.pack(pady=(0,6))
    sep_var.trace_add("write", lambda *_: rebuild_login_preview())
    rebuild_login_preview()

    # ---------- BLOCOS DE SENHA ----------
    ctk.CTkLabel(win, text="Blocos da Senha:", font=("Arial",12,"bold"), anchor="w").pack(fill="x", padx=20)

    frame_senha_blocos = ctk.CTkFrame(win)
    frame_senha_blocos.pack(fill="x", padx=20, pady=(4,6))

    senha_checks = {}
    row_s = 0
    col_s = 0
    for bloco in BLOCOS_SENHA:
        var = tk.BooleanVar(value=(bloco in config_senha["blocos"]))
        senha_checks[bloco] = var
        cb = ctk.CTkCheckBox(frame_senha_blocos, text=LABEL_BLOCOS[bloco], variable=var)
        cb.grid(row=row_s, column=col_s, padx=12, pady=4, sticky="w")
        col_s += 1
        if col_s > 2:
            col_s = 0
            row_s += 1

    # Senha fixa
    frame_fixa = ctk.CTkFrame(win)
    frame_fixa.pack(fill="x", padx=20, pady=(0,8))
    ctk.CTkLabel(frame_fixa, text="Senha Fixa:", width=100, anchor="w").pack(side="left", padx=8)
    entry_fixa = ctk.CTkEntry(frame_fixa, width=220)
    entry_fixa.insert(0, config_senha["senha_fixa"])
    entry_fixa.pack(side="left", padx=4)
    ctk.CTkLabel(frame_fixa, text="(usada quando bloco 'Senha Fixa' estiver marcado)",
                 text_color="gray", font=("Arial",10)).pack(side="left", padx=6)

    # Preview senha
    def rebuild_senha_preview():
        nome_ex = "Maria Santos"
        cpf_ex  = "12345678901"
        blocos_ativos = [b for b in BLOCOS_SENHA if senha_checks.get(b, tk.BooleanVar()).get()]
        partes = []
        for b in blocos_ativos:
            if b == "senha_fixa":
                partes.append(entry_fixa.get())
            else:
                partes.append(_resolver_bloco_senha(b, nome_ex, cpf_ex))
        lbl_senha_prev.configure(text=f"Preview senha: {''.join(partes) or '—'}")

    for v in senha_checks.values():
        v.trace_add("write", lambda *_: rebuild_senha_preview())
    entry_fixa.bind("<KeyRelease>", lambda *_: rebuild_senha_preview())

    lbl_senha_prev = ctk.CTkLabel(win, text="Preview senha: —", text_color=COR_PRIMARIA, font=("Consolas",12))
    lbl_senha_prev.pack(pady=(0,6))
    rebuild_senha_preview()

    # ---------- BOTÕES ----------
    frame_btns = ctk.CTkFrame(win, fg_color="transparent")
    frame_btns.pack(pady=10)

    def restaurar_padrao():
        config_login["blocos"]    = ["primeiro_nome", "ultimo_nome", "cpf_4"]
        config_login["separador"] = ""
        config_senha["blocos"]    = ["cpf_completo"]
        config_senha["senha_fixa"]= "Tech@2026"
        adicionar_log("↺ Configurações restauradas para o padrão.", "aviso")
        win.destroy()
        # Recarregar planilha para regenerar logins
        if excel_path:
            carregar_preview()

    def salvar():
        config_login["blocos"]    = [b for b in BLOCOS_LOGIN if login_checks[b].get()]
        config_login["separador"] = "" if sep_var.get() == "nenhum" else sep_var.get()
        config_senha["blocos"]    = [b for b in BLOCOS_SENHA if senha_checks[b].get()]
        config_senha["senha_fixa"]= entry_fixa.get()
        if not config_login["blocos"]:
            messagebox.showwarning("Atenção","Selecione ao menos um bloco para o login.", parent=win)
            return
        adicionar_log("✔ Configurações de login/senha salvas.", "ok")
        win.destroy()
        if excel_path:
            carregar_preview()

    ctk.CTkButton(frame_btns, text="↺ Restaurar Padrão", fg_color=COR_NEUTRO, hover_color=COR_NEU_HOVER,
                  width=160, command=restaurar_padrao).pack(side="left", padx=8)
    ctk.CTkButton(frame_btns, text="✔ Salvar", fg_color=COR_SECUNDARIA, hover_color=COR_SEC_HOVER,
                  width=120, command=salvar).pack(side="left", padx=8)

# =============================
# CHECKBOXES / SELEÇÃO
# =============================

def toggle_check(event):
    region = table.identify_region(event.x, event.y)
    col    = table.identify_column(event.x)
    item   = table.identify_row(event.y)
    if region == "cell" and col == "#1" and item:
        vals    = list(table.item(item, "values"))
        vals[0] = CHECKED if vals[0] == UNCHECKED else UNCHECKED
        table.item(item, values=vals)
        atualizar_rodape()

def selecionar_todos():
    for item in table.get_children():
        vals    = list(table.item(item, "values"))
        vals[0] = CHECKED
        table.item(item, values=vals)
    atualizar_rodape()

def desselecionar_todos():
    for item in table.get_children():
        vals    = list(table.item(item, "values"))
        vals[0] = UNCHECKED
        table.item(item, values=vals)
    atualizar_rodape()

def itens_selecionados():
    return [i for i in table.get_children() if table.item(i,"values")[0] == CHECKED]

# =============================
# VERIFICAR DUPLICATAS NA PLANILHA
# =============================

def verificar_duplicatas_planilha(logins_gerados):
    """Retorna dict login → [linhas] para logins que aparecem mais de uma vez."""
    contagem = {}
    for idx, login in logins_gerados:
        contagem.setdefault(login, []).append(idx)
    return {k: v for k, v in contagem.items() if len(v) > 1}

# =============================
# VERIFICAR EXISTÊNCIA AD
# =============================

def usuario_existe(login):
    try:
        q = adquery.ADQuery()
        q.execute_query(attributes=["sAMAccountName"], where_clause=f"sAMAccountName = '{login}'")
        return len(list(q.get_results())) > 0
    except:
        return False

# =============================
# SELECIONAR EXCEL
# =============================

def selecionar_excel():
    global excel_path
    excel_path = filedialog.askopenfilename(filetypes=[("Excel","*.xlsx *.xls")])
    if excel_path:
        label_arquivo.configure(text=excel_path)
        carregar_preview()

# =============================
# DETECTAR HEADER
# =============================

def detectar_header(df):
    for i, row in df.iterrows():
        linha = row.astype(str).str.lower()
        if "nome" in linha.values and "cpf" in linha.values:
            return i
    return None

# =============================
# CARREGAR PLANILHA + VALIDAÇÃO
# =============================

def carregar_preview():
    try:
        df     = pd.read_excel(excel_path, header=None)
        header = detectar_header(df)

        if header is None:
            adicionar_log("✖ Colunas 'Nome' e 'CPF' não encontradas na planilha.", "erro")
            return

        dados = pd.read_excel(excel_path, header=header)
        table.delete(*table.get_children())

        erros_encontrados = []
        logins_gerados    = []   # (linha_num, login) para checar duplicatas
        total = 0
        ok    = 0

        # Detecta se há coluna Matrícula
        tem_matricula = "Matrícula" in dados.columns or "Matricula" in dados.columns
        col_mat = "Matrícula" if "Matrícula" in dados.columns else ("Matricula" if "Matricula" in dados.columns else None)

        for index, row in dados.iterrows():
            nome      = str(row.get("Nome", "")).strip()
            cpf       = str(row.get("CPF",  "")).strip()
            matricula = str(row.get(col_mat,"")).strip() if col_mat else ""
            linha_num = index + 2

            if nome.lower().startswith("total"):
                adicionar_log("📋 Fim da planilha detectado (linha 'Total').", "info")
                break

            total += 1
            erros  = validar_linha(nome, cpf, linha_num)

            if erros:
                erros_encontrados.extend(erros)
                table.insert("", "end",
                    values=(UNCHECKED, nome, cpf, "—", "—", "⚠ Erro"),
                    tags=("erro_dados",))
            else:
                login = gerar_login(nome, cpf, matricula)
                senha = gerar_senha(nome, cpf)
                logins_gerados.append((linha_num, login))
                table.insert("", "end",
                    values=(UNCHECKED, nome, cpf, login, senha, "Carregado"),
                    tags=("disponivel",))
                ok += 1

        # 15 — Detectar duplicatas de login na própria planilha
        dups = verificar_duplicatas_planilha(logins_gerados)
        if dups:
            adicionar_log("─"*55, "info")
            adicionar_log(f"⚠ {len(dups)} login(s) duplicado(s) detectado(s) na planilha:", "aviso")
            for login, linhas in dups.items():
                adicionar_log(f"   • Login '{login}' gerado nas linhas: {linhas}", "aviso")
            adicionar_log("─"*55, "info")

        adicionar_log(f"✔ Planilha carregada: {ok}/{total} linhas válidas.", "ok")

        if erros_encontrados:
            adicionar_log("─"*55, "info")
            adicionar_log(f"⚠ {len(erros_encontrados)} problema(s) encontrado(s):", "aviso")
            for err in erros_encontrados:
                adicionar_log(f"   • {err}", "aviso")
            adicionar_log("─"*55, "info")
            messagebox.showwarning(
                "Problemas na Planilha",
                f"{len(erros_encontrados)} linha(s) com problema(s).\n"
                "Verifique o log para detalhes."
            )

        atualizar_rodape()

    except Exception as e:
        adicionar_log(f"✖ Erro ao carregar planilha: {e}", "erro")

# =============================
# EXPORTAR RELATÓRIO
# =============================

def exportar_relatorio():
    itens = table.get_children()
    if not itens:
        adicionar_log("⚠ Tabela vazia — nada para exportar.", "aviso")
        return

    agora   = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho = filedialog.asksaveasfilename(
        defaultextension=".xlsx",
        initialfile=f"relatorio_usuarios_{agora}.xlsx",
        filetypes=[("Excel","*.xlsx")]
    )
    if not caminho:
        return

    linhas = []
    for item in itens:
        v = table.item(item, "values")
        # colunas: Sel(0) Nome(1) CPF(2) Login(3) Senha(4) Status(5)
        linhas.append({
            "Nome":   v[1],
            "CPF":    v[2],
            "Login":  v[3],
            "Senha":  v[4],
            "Status": v[5],
        })

    df = pd.DataFrame(linhas)
    df.to_excel(caminho, index=False)
    adicionar_log(f"✔ Relatório exportado: {caminho}", "ok")

# =============================
# VERIFICAR USUÁRIOS
# =============================

def verificar():
    alvos = itens_selecionados()
    if not alvos:
        adicionar_log("⚠ Nenhum usuário selecionado.", "aviso")
        return
    adicionar_log(f"🔍 Verificando {len(alvos)} usuário(s)...", "info")
    iniciar_progresso(len(alvos))

    for idx, item in enumerate(alvos, 1):
        dados = table.item(item)["values"]
        login = dados[3]
        if login == "—":
            atualizar_progresso(idx, len(alvos))
            continue
        if usuario_existe(login):
            table.item(item, values=(dados[0],dados[1],dados[2],login,dados[4],"Já existe"), tags=("existe",))
        else:
            table.item(item, values=(dados[0],dados[1],dados[2],login,dados[4],"Disponível"), tags=("disponivel",))
        atualizar_progresso(idx, len(alvos))

    finalizar_progresso()
    atualizar_rodape()

# =============================
# CRIAR USUÁRIOS
# =============================

def criar():
    if not OU_USUARIOS:
        adicionar_log("✖ Selecione uma OU antes de criar usuários.", "erro")
        messagebox.showerror("OU não selecionada","Selecione a OU de destino.")
        return
    alvos = itens_selecionados()
    if not alvos:
        adicionar_log("⚠ Nenhum usuário selecionado.", "aviso")
        return

    container = adcontainer.ADContainer.from_dn(OU_USUARIOS)
    iniciar_progresso(len(alvos))

    for idx, item in enumerate(alvos, 1):
        dados = table.item(item)["values"]
        nome  = dados[1]
        cpf   = limpar_cpf(dados[2])
        login = dados[3]
        senha = dados[4]

        if login == "—" or usuario_existe(login):
            atualizar_progresso(idx, len(alvos))
            continue
        try:
            user = aduser.ADUser.create(login, container, password=senha)
            user.update_attribute("displayName", nome)
            user.update_attribute("userPrincipalName", f"{login}@{DOMINIO}")
            table.item(item, values=(dados[0],nome,cpf,login,senha,"Criado"), tags=("criado",))
            adicionar_log(f"✔ Usuário criado: {login}", "ok")
        except Exception as e:
            adicionar_log(f"✖ Erro ao criar {login}: {e}", "erro")
        atualizar_progresso(idx, len(alvos))

    finalizar_progresso()
    atualizar_rodape()

# =============================
# REDEFINIR SENHA EM LOTE
# =============================

def redefinir_senha():
    alvos = itens_selecionados()
    if not alvos:
        adicionar_log("⚠ Nenhum usuário selecionado.", "aviso")
        return
    if not messagebox.askyesno("Confirmar","Redefinir senha dos usuários selecionados para o padrão configurado?"):
        return

    iniciar_progresso(len(alvos))
    for idx, item in enumerate(alvos, 1):
        dados = table.item(item)["values"]
        login = dados[3]
        senha = dados[4]
        if login == "—":
            atualizar_progresso(idx, len(alvos))
            continue
        try:
            q = adquery.ADQuery()
            q.execute_query(attributes=["distinguishedName"], where_clause=f"sAMAccountName='{login}'")
            res = list(q.get_results())
            if res:
                user = aduser.ADUser.from_dn(res[0]["distinguishedName"])
                user.set_password(senha)
                adicionar_log(f"✔ Senha redefinida: {login}", "ok")
            else:
                adicionar_log(f"⚠ Usuário não encontrado no AD: {login}", "aviso")
        except Exception as e:
            adicionar_log(f"✖ Erro ao redefinir senha de {login}: {e}", "erro")
        atualizar_progresso(idx, len(alvos))

    finalizar_progresso()

# =============================
# MOVER USUÁRIO DE OU
# =============================

def mover_ou():
    alvos = itens_selecionados()
    if not alvos:
        adicionar_log("⚠ Nenhum usuário selecionado.", "aviso")
        return
    if not DOMINIO:
        adicionar_log("✖ Domínio não detectado.", "erro")
        return

    adicionar_log("🔍 Consultando OUs para mover...", "info")
    ous = listar_ous()
    if not ous:
        adicionar_log("✖ Nenhuma OU encontrada.", "erro")
        return

    win = ctk.CTkToplevel(app)
    win.title("Mover Usuários — Selecionar OU de Destino")
    win.geometry("700x460")
    win.grab_set()

    ctk.CTkLabel(win, text=f"Mover {len(alvos)} usuário(s) para a OU:",
                 font=("Arial",13,"bold")).pack(padx=20, pady=(15,5))

    frame_busca = ctk.CTkFrame(win)
    frame_busca.pack(fill="x", padx=20, pady=(0,8))
    ctk.CTkLabel(frame_busca, text="Filtrar:").pack(side="left", padx=(8,4))
    entry_busca = ctk.CTkEntry(frame_busca, width=440)
    entry_busca.pack(side="left", padx=4)

    frame_lista = ctk.CTkFrame(win)
    frame_lista.pack(fill="both", expand=True, padx=20)
    scrollbar = tk.Scrollbar(frame_lista)
    scrollbar.pack(side="right", fill="y")
    listbox = tk.Listbox(
        frame_lista, yscrollcommand=scrollbar.set,
        bg=COR_FUNDO_LIST, fg="white", selectbackground=COR_SECUNDARIA,
        font=("Consolas",10), activestyle="none", borderwidth=0, highlightthickness=0
    )
    listbox.pack(fill="both", expand=True)
    scrollbar.config(command=listbox.yview)

    def popular(filtro=""):
        listbox.delete(0, tk.END)
        for ou in ous:
            if filtro.lower() in ou.lower():
                listbox.insert(tk.END, ou)

    popular()
    entry_busca.bind("<KeyRelease>", lambda *_: popular(entry_busca.get()))

    lbl_sel = ctk.CTkLabel(win, text="Nenhuma OU selecionada", text_color="gray", wraplength=660)
    lbl_sel.pack(padx=20, pady=6)
    listbox.bind("<<ListboxSelect>>", lambda *_: lbl_sel.configure(
        text=listbox.get(listbox.curselection()[0]) if listbox.curselection() else "—",
        text_color=COR_OK
    ))

    def confirmar_mover():
        sel = listbox.curselection()
        if not sel:
            messagebox.showwarning("Atenção","Selecione uma OU.", parent=win)
            return
        ou_destino = listbox.get(sel[0])
        win.destroy()
        _executar_mover(alvos, ou_destino)

    listbox.bind("<Double-Button-1>", lambda e: confirmar_mover())
    ctk.CTkButton(win, text="Mover Usuários", fg_color=COR_SECUNDARIA,
                  hover_color=COR_SEC_HOVER, command=confirmar_mover).pack(pady=(4,15))

def _executar_mover(alvos, ou_destino):
    iniciar_progresso(len(alvos))
    container_destino = adcontainer.ADContainer.from_dn(ou_destino)

    for idx, item in enumerate(alvos, 1):
        login = table.item(item)["values"][3]
        if login == "—":
            atualizar_progresso(idx, len(alvos))
            continue
        try:
            q = adquery.ADQuery()
            q.execute_query(attributes=["distinguishedName"], where_clause=f"sAMAccountName='{login}'")
            res = list(q.get_results())
            if res:
                user = aduser.ADUser.from_dn(res[0]["distinguishedName"])
                user.move(container_destino)
                adicionar_log(f"✔ {login} movido para {ou_destino}", "ok")
            else:
                adicionar_log(f"⚠ {login} não encontrado no AD.", "aviso")
        except Exception as e:
            adicionar_log(f"✖ Erro ao mover {login}: {e}", "erro")
        atualizar_progresso(idx, len(alvos))

    finalizar_progresso()

# =============================
# DESATIVAR / ATIVAR / REMOVER
# =============================

def _acao_em_lote(acao_fn, label_ok, label_erro):
    alvos = itens_selecionados()
    if not alvos:
        adicionar_log("⚠ Nenhum usuário selecionado.", "aviso")
        return
    iniciar_progresso(len(alvos))
    for idx, item in enumerate(alvos, 1):
        login = table.item(item)["values"][3]
        if login == "—":
            atualizar_progresso(idx, len(alvos))
            continue
        try:
            q = adquery.ADQuery()
            q.execute_query(attributes=["distinguishedName"], where_clause=f"sAMAccountName='{login}'")
            res = list(q.get_results())
            if res:
                acao_fn(aduser.ADUser.from_dn(res[0]["distinguishedName"]))
                adicionar_log(f"✔ {label_ok}: {login}", "ok")
        except Exception as e:
            adicionar_log(f"✖ {label_erro} {login}: {e}", "erro")
        atualizar_progresso(idx, len(alvos))
    finalizar_progresso()
    atualizar_rodape()

def desativar():
    _acao_em_lote(lambda u: u.disable(), "Usuário desativado", "Erro ao desativar")

def ativar():
    _acao_em_lote(lambda u: u.enable(), "Usuário ativado", "Erro ao ativar")

def remover():
    alvos = itens_selecionados()
    if not alvos:
        adicionar_log("⚠ Nenhum usuário selecionado.", "aviso")
        return
    if not messagebox.askyesno("Confirmar Remoção",
            f"Deseja remover {len(alvos)} usuário(s) permanentemente do AD?"):
        return
    _acao_em_lote(lambda u: u.delete(), "Usuário removido", "Erro ao remover")

# =============================
# THREAD
# =============================

def executar_thread(func):
    threading.Thread(target=func, daemon=True).start()

# ======================================================
# ==================== INTERFACE =======================
# ======================================================

# ---------- TOPO ----------
frame_top = ctk.CTkFrame(app)
frame_top.pack(fill="x", padx=20, pady=10)

ctk.CTkLabel(frame_top, text="Tech Solutions - Gerenciador AD",
             font=("Arial",20,"bold")).pack(side="left", padx=10)

# Botão configurações no topo direito
ctk.CTkButton(
    frame_top, text="⚙ Configurações",
    fg_color=COR_NEUTRO, hover_color=COR_NEU_HOVER, width=150,
    command=abrir_configuracoes
).pack(side="right", padx=10)

# ---------- DOMÍNIO / OU ----------
frame_dominio = ctk.CTkFrame(app)
frame_dominio.pack(fill="x", padx=20, pady=(0,6))

ctk.CTkButton(frame_dominio, text="🔎 Detectar Domínio",
              fg_color=COR_SECUNDARIA, hover_color=COR_SEC_HOVER, width=180,
              command=lambda: executar_thread(detectar_dominio)
).pack(side="left", padx=(10,8), pady=8)

label_dominio = ctk.CTkLabel(frame_dominio, text="Domínio: não detectado",
                              text_color="gray", width=300, anchor="w")
label_dominio.pack(side="left", padx=4)

ctk.CTkLabel(frame_dominio, text="|", text_color="gray").pack(side="left", padx=8)

btn_selecionar_ou = ctk.CTkButton(frame_dominio, text="📂 Selecionar OU",
                                   fg_color=COR_SECUNDARIA, hover_color=COR_SEC_HOVER,
                                   width=160, state="disabled", command=abrir_selecao_ou)
btn_selecionar_ou.pack(side="left", padx=8)

label_ou = ctk.CTkLabel(frame_dominio, text="OU: nenhuma selecionada",
                         text_color="gray", anchor="w", wraplength=380)
label_ou.pack(side="left", padx=4)

# ---------- PLANILHA + EXPORTAR ----------
frame_excel = ctk.CTkFrame(app)
frame_excel.pack(fill="x", padx=20, pady=(0,6))

ctk.CTkButton(frame_excel, text="Selecionar Planilha",
              image=icon_excel, compound="left",
              fg_color=COR_PRIMARIA, hover_color=COR_HOVER,
              command=selecionar_excel
).pack(side="left", padx=10, pady=8)

label_arquivo = ctk.CTkLabel(frame_excel, text="Nenhum arquivo selecionado")
label_arquivo.pack(side="left", padx=4)

ctk.CTkButton(frame_excel, text="📊 Exportar Relatório",
              fg_color=COR_NEUTRO, hover_color=COR_NEU_HOVER, width=170,
              command=exportar_relatorio
).pack(side="right", padx=10)

# ---------- SELEÇÃO RÁPIDA ----------
frame_sel = ctk.CTkFrame(app)
frame_sel.pack(fill="x", padx=20, pady=(0,4))

ctk.CTkLabel(frame_sel, text="Seleção rápida:", font=("Arial",11)).pack(side="left", padx=(10,6), pady=4)

ctk.CTkButton(frame_sel, text="☑ Selecionar Todos",
              fg_color=COR_NEUTRO, hover_color=COR_NEU_HOVER, width=150,
              command=selecionar_todos).pack(side="left", padx=4)

ctk.CTkButton(frame_sel, text="☐ Desselecionar Todos",
              fg_color=COR_NEUTRO, hover_color=COR_NEU_HOVER, width=175,
              command=desselecionar_todos).pack(side="left", padx=4)

# ---------- TABELA ----------
frame_table = ctk.CTkFrame(app)
frame_table.pack(fill="both", expand=True, padx=20)

# Agora com coluna Senha
columns = ("Sel","Nome","CPF","Login","Senha","Status")
table   = ttk.Treeview(frame_table, columns=columns, show="headings")

table.heading("Sel",    text="☑",     anchor="center")
table.heading("Nome",   text="Nome")
table.heading("CPF",    text="CPF")
table.heading("Login",  text="Login")
table.heading("Senha",  text="Senha Inicial")
table.heading("Status", text="Status")

table.column("Sel",    width=40,  anchor="center", stretch=False)
table.column("Nome",   width=260)
table.column("CPF",    width=150)
table.column("Login",  width=200)
table.column("Senha",  width=180)
table.column("Status", width=110)

table.pack(fill="both", expand=True)

table.tag_configure("criado",     foreground="#66BB6A")
table.tag_configure("existe",     foreground="#EF5350")
table.tag_configure("disponivel", foreground="#FFA726")
table.tag_configure("erro_dados", foreground="#FF7043")

table.bind("<Button-1>", toggle_check)

# ---------- BOTÕES DE AÇÃO ----------
frame_buttons = ctk.CTkFrame(app)
frame_buttons.pack(fill="x", padx=20, pady=6)

for texto, icone, func in [
    ("Verificar",  icon_verificar, verificar),
    ("Criar",      icon_criar,     criar),
    ("Desativar",  icon_desativar, desativar),
    ("Ativar",     icon_ativar,    ativar),
    ("Remover",    icon_remover,   remover),
]:
    ctk.CTkButton(frame_buttons, text=texto, image=icone, compound="left",
                  fg_color=COR_PRIMARIA, hover_color=COR_HOVER,
                  command=lambda f=func: executar_thread(f)
    ).pack(side="left", padx=5, pady=6)

# Botões extras
ctk.CTkButton(frame_buttons, text="🔑 Redefinir Senha",
              fg_color=COR_NEUTRO, hover_color=COR_NEU_HOVER, width=150,
              command=lambda: executar_thread(redefinir_senha)
).pack(side="left", padx=5)

ctk.CTkButton(frame_buttons, text="📁 Mover OU",
              fg_color=COR_NEUTRO, hover_color=COR_NEU_HOVER, width=130,
              command=lambda: executar_thread(mover_ou)
).pack(side="left", padx=5)

# ---------- BARRA DE PROGRESSO ----------
frame_progresso = ctk.CTkFrame(app)
# Começa escondida — aparece só durante operações

progress_bar = ctk.CTkProgressBar(frame_progresso, mode="determinate", width=800)
progress_bar.pack(side="left", padx=(10,8), pady=6)
progress_bar.set(0)

label_progresso = ctk.CTkLabel(frame_progresso, text="0 / 0", width=80)
label_progresso.pack(side="left", padx=4)

# ---------- LOG ----------
frame_log = ctk.CTkFrame(app)
frame_log.pack(fill="both", padx=20, pady=(0,4))

frame_log_header = ctk.CTkFrame(frame_log, fg_color="transparent")
frame_log_header.pack(fill="x")

ctk.CTkLabel(frame_log_header, text="📋 Log de Operações",
             font=("Arial",11,"bold")).pack(side="left", padx=8, pady=(4,2))

ctk.CTkButton(frame_log_header, text="💾 Exportar Log",
              fg_color=COR_NEUTRO, hover_color=COR_NEU_HOVER,
              width=120, height=26, command=exportar_log
).pack(side="right", padx=4, pady=(4,2))

ctk.CTkButton(frame_log_header, text="🗑 Limpar Log",
              fg_color=COR_NEUTRO, hover_color=COR_NEU_HOVER,
              width=110, height=26, command=limpar_log
).pack(side="right", padx=4, pady=(4,2))

log_box = tk.Text(frame_log, height=7, bg=COR_FUNDO_LOG, fg="white", font=("Consolas",9))
log_box.pack(fill="both", expand=True, padx=4, pady=(0,4))
log_box.configure(state="disabled")

# ---------- RODAPÉ ----------
frame_rodape = ctk.CTkFrame(app, height=28, fg_color=COR_NEUTRO)
frame_rodape.pack(fill="x", padx=20, pady=(0,8))

label_rodape = ctk.CTkLabel(
    frame_rodape,
    text="Total: 0  |  Selecionados: 0  |  Criados: 0  |  Erros: 0",
    font=("Arial",10),
    text_color="gray"
)
label_rodape.pack(side="left", padx=12, pady=4)

# ---------- INICIALIZAR ----------
adicionar_log("Tech Solutions - AD Manager iniciado.", "info")
adicionar_log("→ Clique em 'Detectar Domínio' para começar.", "info")

app.mainloop()