cat > README.md << 'ENDOFFILE'
# 🔍 ForensHash — Sistema de Perícia Forense Computacional

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Flask](https://img.shields.io/badge/Flask-3.1-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue)
![Status](https://img.shields.io/badge/Status-Em%20Desenvolvimento-yellow)

Sistema completo de perícia forense computacional desenvolvido em Python, com interface desktop e versão web, para cálculo de hashes criptográficos, geração de laudos periciais e verificação de integridade de evidências digitais.

## 🎯 Funcionalidades

- 🔑 Calculadora de Hash — MD5, SHA-1 e SHA-256 simultâneos
- 📄 Gerador de Laudos — Word e PDF profissionais
- 🖥️ Interface Desktop — App offline com Tkinter
- 🌐 Interface Web — Sistema Flask com autenticação
- 🔐 Controle de Acesso — Login com perfis admin e perito
- 📋 Histórico de Casos — Banco de dados PostgreSQL
- ✅ Verificação de Integridade — Detecta adulteração de evidências
- ⚙️ Painel Administrativo — Gestão de usuários e casos

## 🛠️ Tecnologias

- Python 3.12
- Flask 3.1
- PostgreSQL + SQLAlchemy
- Tkinter
- python-docx + ReportLab
- Werkzeug Security

## 🚀 Como Executar

### Pré-requisitos
- Python 3.12+
- PostgreSQL 16+

### Instalação

\`\`\`bash
git clone https://github.com/seu-usuario/ForensHash.git
cd ForensHash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
\`\`\`

### Banco de Dados

\`\`\`bash
sudo -u postgres psql -c "CREATE USER forenshash WITH PASSWORD 'sua_senha';"
sudo -u postgres psql -c "CREATE DATABASE forenshash_db OWNER forenshash;"
\`\`\`

### Executar

\`\`\`bash
python3 web/app.py
\`\`\`

Acesse: http://localhost:5000

## 🔬 Contexto Forense

- Cadeia de custódia com registro de data/hora e perito responsável
- Múltiplos algoritmos de hash simultâneos
- Hashes registrados no banco para comparação futura
- Laudos em formato Word e PDF para uso jurídico

## 👩‍💻 Desenvolvedora

Desenvolvido como projeto de portfólio na área de Perícia Forense Computacional.

## 📄 Licença

MIT