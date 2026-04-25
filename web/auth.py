import json
import os
from functools import wraps
from flask import session, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash

# ─── Configurações ────────────────────────────────────────────────────────────
ARQUIVO_USERS = os.path.join(os.path.dirname(__file__), "users.json")


# ─── Funções de usuários ──────────────────────────────────────────────────────

def carregar_users() -> dict:
    if os.path.isfile(ARQUIVO_USERS):
        with open(ARQUIVO_USERS, "r") as f:
            return json.load(f)
    return {}


def salvar_users(users: dict):
    with open(ARQUIVO_USERS, "w") as f:
        json.dump(users, f, indent=2)


def criar_usuario(username: str, password: str, nome: str = "", perfil: str = "perito") -> bool:
    """Cria um novo usuário. Retorna False se já existir."""
    users = carregar_users()
    if username in users:
        return False
    users[username] = {
        "username":  username,
        "password":  generate_password_hash(password),
        "nome":      nome,
        "perfil":    perfil,  # "admin" ou "perito"
        "ativo":     True,
    }
    salvar_users(users)
    return True


def autenticar(username: str, password: str) -> dict | None:
    """Verifica login. Retorna dados do usuário ou None."""
    users = carregar_users()
    user  = users.get(username)
    if not user:
        return None
    if not user.get("ativo", True):
        return None
    if not check_password_hash(user["password"], password):
        return None
    return user


# ─── Decorator de proteção de rotas ──────────────────────────────────────────

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "usuario" not in session:
            flash("Faça login para acessar o sistema.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "usuario" not in session:
            flash("Faça login para acessar o sistema.", "warning")
            return redirect(url_for("login"))
        if session.get("perfil") != "admin":
            flash("Acesso restrito a administradores.", "danger")
            return redirect(url_for("dashboard"))
        return f(*args, **kwargs)
    return decorated


# ─── Criar usuário admin padrão se não existir ────────────────────────────────

def inicializar_users():
    """Cria o usuário admin padrão na primeira execução."""
    users = carregar_users()
    if not users:
        criar_usuario(
            username = "admin",
            password = "forenshash@2026",
            nome     = "Administrador",
            perfil   = "admin"
        )
        print("✅ Usuário admin criado — senha: forenshash@2026")
        print("⚠️  Altere a senha após o primeiro login!")