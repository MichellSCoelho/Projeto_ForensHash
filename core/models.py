from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


# ─── Modelo de Usuário ────────────────────────────────────────────────────────
class Usuario(db.Model):
    __tablename__ = "usuarios"

    id          = db.Column(db.Integer, primary_key=True)
    username    = db.Column(db.String(80), unique=True, nullable=False)
    password    = db.Column(db.String(256), nullable=False)
    nome        = db.Column(db.String(150), nullable=False)
    registro    = db.Column(db.String(50))
    instituicao = db.Column(db.String(200))
    perfil      = db.Column(db.String(20), default="perito")  # admin ou perito
    ativo       = db.Column(db.Boolean, default=True)
    criado_em   = db.Column(db.DateTime, default=datetime.utcnow)

    casos = db.relationship("Caso", backref="perito", lazy=True)

    def to_dict(self):
        return {
            "id":          self.id,
            "username":    self.username,
            "nome":        self.nome,
            "registro":    self.registro,
            "instituicao": self.instituicao,
            "perfil":      self.perfil,
            "ativo":       self.ativo,
            "criado_em":   self.criado_em.strftime("%d/%m/%Y %H:%M"),
        }


# ─── Modelo de Caso Pericial ──────────────────────────────────────────────────
class Caso(db.Model):
    __tablename__ = "casos"

    id           = db.Column(db.Integer, primary_key=True)
    numero_caso  = db.Column(db.String(100), nullable=False)
    arquivo_nome = db.Column(db.String(300), nullable=False)
    arquivo_path = db.Column(db.String(500))
    tamanho      = db.Column(db.String(50))
    md5          = db.Column(db.String(32), nullable=False)
    sha1         = db.Column(db.String(40), nullable=False)
    sha256       = db.Column(db.String(64), nullable=False)
    status       = db.Column(db.String(20), default="ativo")  # ativo, arquivado
    criado_em    = db.Column(db.DateTime, default=datetime.utcnow)

    usuario_id   = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    verificacoes = db.relationship("Verificacao", backref="caso", lazy=True)

    def to_dict(self):
        return {
            "id":           self.id,
            "numero_caso":  self.numero_caso,
            "arquivo_nome": self.arquivo_nome,
            "tamanho":      self.tamanho,
            "md5":          self.md5,
            "sha1":         self.sha1,
            "sha256":       self.sha256,
            "status":       self.status,
            "criado_em":    self.criado_em.strftime("%d/%m/%Y %H:%M"),
            "perito":       self.perito.nome if self.perito else "—",
        }


# ─── Modelo de Verificação de Integridade ─────────────────────────────────────
class Verificacao(db.Model):
    __tablename__ = "verificacoes"

    id              = db.Column(db.Integer, primary_key=True)
    caso_id         = db.Column(db.Integer, db.ForeignKey("casos.id"), nullable=False)
    algoritmo       = db.Column(db.String(10), nullable=False)
    hash_referencia = db.Column(db.String(64), nullable=False)
    hash_calculado  = db.Column(db.String(64), nullable=False)
    integro         = db.Column(db.Boolean, nullable=False)
    verificado_em   = db.Column(db.DateTime, default=datetime.utcnow)
    verificado_por  = db.Column(db.Integer, db.ForeignKey("usuarios.id"))

    def to_dict(self):
        return {
            "id":              self.id,
            "caso_id":         self.caso_id,
            "algoritmo":       self.algoritmo,
            "hash_referencia": self.hash_referencia,
            "hash_calculado":  self.hash_calculado,
            "integro":         self.integro,
            "verificado_em":   self.verificado_em.strftime("%d/%m/%Y %H:%M"),
        }