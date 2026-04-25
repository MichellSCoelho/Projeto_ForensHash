import os
import sys
import uuid

from flask import (Flask, render_template, request, redirect,
                   url_for, session, flash, send_file)
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.hasher import calcular_hashes
from core.report_builder import gerar_docx, gerar_pdf
from core.models import db, Usuario, Caso, Verificacao
from web.auth import login_required, admin_required

# ─── Configuração Flask ───────────────────────────────────────────────────────
app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = "forenshash-chave-secreta-2026"

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://forenshash:forenshash2026@localhost/forenshash_db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "uploads_tmp")
LAUDOS_DIR = os.path.join(os.path.dirname(__file__), "..", "laudos")
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(LAUDOS_DIR, exist_ok=True)


# ─── Inicialização do banco ───────────────────────────────────────────────────
def inicializar_banco():
    with app.app_context():
        db.create_all()
        if not Usuario.query.filter_by(username="admin").first():
            admin = Usuario(
                username    = "admin",
                password    = generate_password_hash("forenshash@2026"),
                nome        = "Administrador",
                perfil      = "admin",
                ativo       = True,
            )
            db.session.add(admin)
            db.session.commit()
            print("✅ Usuário admin criado no banco!")


# ─── Autenticação ─────────────────────────────────────────────────────────────
@app.route("/", methods=["GET"])
def index():
    if "usuario" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        user = Usuario.query.filter_by(username=username, ativo=True).first()
        if user and check_password_hash(user.password, password):
            session["usuario"]    = user.username
            session["nome"]       = user.nome
            session["perfil"]     = user.perfil
            session["usuario_id"] = user.id
            flash(f"Bem-vindo, {user.nome}!", "success")
            return redirect(url_for("dashboard"))
        flash("Usuário ou senha incorretos.", "danger")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Sessão encerrada com segurança.", "info")
    return redirect(url_for("login"))


# ─── Dashboard ────────────────────────────────────────────────────────────────
@app.route("/dashboard")
@login_required
def dashboard():
    total_casos  = Caso.query.filter_by(usuario_id=session["usuario_id"]).count()
    ultimos      = Caso.query.filter_by(usuario_id=session["usuario_id"])\
                             .order_by(Caso.criado_em.desc()).limit(5).all()
    return render_template("dashboard.html", total_casos=total_casos, ultimos=ultimos)


# ─── Calcular hash ────────────────────────────────────────────────────────────
@app.route("/calcular", methods=["POST"])
@login_required
def calcular():
    arquivo     = request.files.get("arquivo")
    numero_caso = request.form.get("numero_caso", "").strip()
    nome_perito = request.form.get("nome_perito", "").strip()
    registro    = request.form.get("registro", "").strip()
    instituicao = request.form.get("instituicao", "").strip()

    if not arquivo or arquivo.filename == "":
        flash("Selecione um arquivo para análise.", "danger")
        return redirect(url_for("dashboard"))

    if not numero_caso:
        flash("Informe o número do caso.", "danger")
        return redirect(url_for("dashboard"))

    # Salva arquivo temporariamente
    nome_seguro = secure_filename(arquivo.filename)
    id_unico    = str(uuid.uuid4())[:8]
    caminho_tmp = os.path.join(UPLOAD_DIR, f"{id_unico}_{nome_seguro}")
    arquivo.save(caminho_tmp)

    # Calcula hashes
    resultado = calcular_hashes(caminho_tmp)
    resultado["arquivo"] = nome_seguro

    # Atualiza dados do perito no banco
    user = Usuario.query.get(session["usuario_id"])
    if nome_perito:   user.nome        = nome_perito
    if registro:      user.registro    = registro
    if instituicao:   user.instituicao = instituicao
    db.session.commit()

    # Salva caso no banco
    caso = Caso(
        numero_caso  = numero_caso,
        arquivo_nome = nome_seguro,
        arquivo_path = caminho_tmp,
        tamanho      = resultado["tamanho_legivel"],
        md5          = resultado["md5"],
        sha1         = resultado["sha1"],
        sha256       = resultado["sha256"],
        usuario_id   = session["usuario_id"],
    )
    db.session.add(caso)
    db.session.commit()

    session["resultado_hash"] = resultado
    session["dados_perito"]   = {
        "nome":        user.nome,
        "registro":    user.registro or registro,
        "instituicao": user.instituicao or instituicao,
    }
    session["numero_caso"] = numero_caso
    session["caso_id"]     = caso.id

    return redirect(url_for("resultado"))


# ─── Resultado ────────────────────────────────────────────────────────────────
@app.route("/resultado")
@login_required
def resultado():
    dados_hash   = session.get("resultado_hash")
    dados_perito = session.get("dados_perito")
    numero_caso  = session.get("numero_caso")

    if not dados_hash:
        flash("Nenhuma análise encontrada.", "warning")
        return redirect(url_for("dashboard"))

    return render_template("resultado.html",
                           dados_hash=dados_hash,
                           dados_perito=dados_perito,
                           numero_caso=numero_caso)


# ─── Histórico de casos ───────────────────────────────────────────────────────
@app.route("/historico")
@login_required
def historico():
    if session.get("perfil") == "admin":
        casos = Caso.query.order_by(Caso.criado_em.desc()).all()
    else:
        casos = Caso.query.filter_by(usuario_id=session["usuario_id"])\
                          .order_by(Caso.criado_em.desc()).all()
    return render_template("historico.html", casos=casos)


# ─── Download laudos ──────────────────────────────────────────────────────────
@app.route("/download/<formato>")
@login_required
def download(formato):
    dados_hash   = session.get("resultado_hash")
    dados_perito = session.get("dados_perito")
    numero_caso  = session.get("numero_caso")

    if not dados_hash:
        flash("Sessão expirada. Refaça a análise.", "warning")
        return redirect(url_for("dashboard"))

    if formato == "docx":
        caminho  = gerar_docx(dados_hash, dados_perito, numero_caso, output_dir=LAUDOS_DIR)
        mimetype = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    elif formato == "pdf":
        caminho  = gerar_pdf(dados_hash, dados_perito, numero_caso, output_dir=LAUDOS_DIR)
        mimetype = "application/pdf"
    else:
        flash("Formato inválido.", "danger")
        return redirect(url_for("resultado"))

    return send_file(os.path.abspath(caminho),
                     mimetype=mimetype,
                     as_attachment=True,
                     download_name=os.path.basename(caminho))

# ─── Verificação de Integridade ───────────────────────────────────────────────
@app.route("/verificar", methods=["GET"])
@login_required
def verificar():
    if session.get("perfil") == "admin":
        casos = Caso.query.order_by(Caso.criado_em.desc()).all()
    else:
        casos = Caso.query.filter_by(usuario_id=session["usuario_id"])\
                          .order_by(Caso.criado_em.desc()).all()
    return render_template("verificar.html", casos=casos)


@app.route("/verificar/<int:caso_id>", methods=["POST"])
@login_required
def verificar_caso(caso_id):
    caso    = Caso.query.get_or_404(caso_id)
    arquivo = request.files.get("arquivo")

    if not arquivo or arquivo.filename == "":
        flash("Selecione o arquivo para verificação.", "danger")
        return redirect(url_for("verificar"))

    # Salva temporariamente
    nome_seguro = secure_filename(arquivo.filename)
    id_unico    = str(uuid.uuid4())[:8]
    caminho_tmp = os.path.join(UPLOAD_DIR, f"{id_unico}_{nome_seguro}")
    arquivo.save(caminho_tmp)

    # Calcula hashes do arquivo enviado
    resultado = calcular_hashes(caminho_tmp)

    # Compara com o banco
    md5_ok    = resultado["md5"]    == caso.md5
    sha1_ok   = resultado["sha1"]   == caso.sha1
    sha256_ok = resultado["sha256"] == caso.sha256
    integro   = md5_ok and sha1_ok and sha256_ok

    # Salva verificação no banco
    verificacao = Verificacao(
        caso_id         = caso.id,
        algoritmo       = "MULTIPLO",
        hash_referencia = caso.sha256,
        hash_calculado  = resultado["sha256"],
        integro         = integro,
        verificado_por  = session["usuario_id"],
    )
    db.session.add(verificacao)
    db.session.commit()

    # Remove arquivo temporário
    os.remove(caminho_tmp)

    return render_template("resultado_verificacao.html",
                           caso=caso,
                           resultado=resultado,
                           integro=integro,
                           md5_ok=md5_ok,
                           sha1_ok=sha1_ok,
                           sha256_ok=sha256_ok,
                           verificacao=verificacao)

# ─── Painel Admin ─────────────────────────────────────────────────────────────
@app.route("/admin")
@admin_required
def admin_panel():
    usuarios = Usuario.query.order_by(Usuario.criado_em.desc()).all()
    casos    = Caso.query.order_by(Caso.criado_em.desc()).all()
    total_usuarios = Usuario.query.count()
    total_casos    = Caso.query.count()
    return render_template("admin.html",
                           usuarios=usuarios,
                           casos=casos,
                           total_usuarios=total_usuarios,
                           total_casos=total_casos)


@app.route("/admin/usuario/novo", methods=["POST"])
@admin_required
def novo_usuario():
    username    = request.form.get("username", "").strip()
    password    = request.form.get("password", "").strip()
    nome        = request.form.get("nome", "").strip()
    perfil      = request.form.get("perfil", "perito")

    if Usuario.query.filter_by(username=username).first():
        flash("Usuário já existe.", "danger")
        return redirect(url_for("admin_panel"))

    user = Usuario(
        username = username,
        password = generate_password_hash(password),
        nome     = nome,
        perfil   = perfil,
        ativo    = True,
    )
    db.session.add(user)
    db.session.commit()
    flash(f"Usuário {nome} criado com sucesso!", "success")
    return redirect(url_for("admin_panel"))


@app.route("/admin/usuario/<int:uid>/excluir")
@admin_required
def excluir_usuario(uid):
    user = Usuario.query.get_or_404(uid)
    if user.username == "admin":
        flash("Não é possível excluir o admin principal.", "danger")
        return redirect(url_for("admin_panel"))
    if user.id == session["usuario_id"]:
        flash("Não é possível excluir o próprio usuário.", "danger")
        return redirect(url_for("admin_panel"))
    nome = user.nome
    db.session.delete(user)
    db.session.commit()
    flash(f"Usuário {nome} excluído com sucesso!", "success")
    return redirect(url_for("admin_panel"))


# ─── Inicialização ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    inicializar_banco()
    app.run(debug=True, host="0.0.0.0", port=5000)