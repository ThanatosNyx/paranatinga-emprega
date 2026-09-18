import os
import sqlite3
from datetime import datetime, timezone, timedelta
fuso_mt = timezone(timedelta(hours=-4))
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'chave_secreta_paranatinga_emprega'

UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ADMIN_USUARIO = 'admin'
ADMIN_SENHA = 'admin123'

def get_db_connection():
    conn = sqlite3.connect('banco.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Criar tabelas se não existirem
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vagas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            tipo TEXT NOT NULL,
            contratante TEXT NOT NULL,
            contato TEXT NOT NULL,
            categoria TEXT NOT NULL,
            descricao TEXT NOT NULL,
            imagem TEXT,
            status TEXT DEFAULT 'pendente',
            data_postagem TEXT,
            data_expiracao TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS servicos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            titulo_servico TEXT NOT NULL,
            categoria TEXT NOT NULL,
            contato TEXT NOT NULL,
            descricao TEXT NOT NULL,
            imagem TEXT,
            status TEXT DEFAULT 'pendente',
            data_postagem TEXT,
            data_expiracao TEXT
        )
    ''')

    # Garantir adição das colunas novas em banco existente
    cursor.execute("PRAGMA table_info(vagas)")
    colunas_vagas = [col[1] for col in cursor.fetchall()]
    if 'data_postagem' not in colunas_vagas:
        cursor.execute("ALTER TABLE vagas ADD COLUMN data_postagem TEXT")
    if 'data_expiracao' not in colunas_vagas:
        cursor.execute("ALTER TABLE vagas ADD COLUMN data_expiracao TEXT")

    cursor.execute("PRAGMA table_info(servicos)")
    colunas_servicos = [col[1] for col in cursor.fetchall()]
    if 'data_postagem' not in colunas_servicos:
        cursor.execute("ALTER TABLE servicos ADD COLUMN data_postagem TEXT")
    if 'data_expiracao' not in colunas_servicos:
        cursor.execute("ALTER TABLE servicos ADD COLUMN data_expiracao TEXT")

    conn.commit()
    conn.close()

init_db()


# --- ROTAS PÚBLICAS ---

@app.route('/')
def index():
    q = request.args.get('q', '').strip()
    categoria = request.args.get('categoria', '').strip()
    pagina = request.args.get('pagina', 1, type=int)
    por_pagina = 10
    offset = (pagina - 1) * por_pagina
    agora = datetime.now(fuso_mt).strftime('%Y-%m-%d %H:%M:%S')

    conn = get_db_connection()

    # Cláusula base de filtro
    where_clause = """
        WHERE (status = 'aprovado' OR status = 'aprovada')
        AND (data_expiracao IS NULL OR data_expiracao >= ?)
    """
    params = [agora]

    if q:
        where_clause += " AND (titulo LIKE ? OR descricao LIKE ? OR contratante LIKE ?)"
        params.extend([f'%{q}%', f'%{q}%', f'%{q}%'])
    
    if categoria:
        where_clause += " AND categoria = ?"
        params.append(categoria)

    # 1. Contar o total de vagas para calcular o número de páginas
    count_query = f"SELECT COUNT(*) FROM vagas {where_clause}"
    total_vagas = conn.execute(count_query, params).fetchone()[0]
    total_paginas = max(1, (total_vagas + por_pagina - 1) // por_pagina)

    # 2. Buscar apenas as 10 vagas da página solicitada
    query = f"SELECT * FROM vagas {where_clause} ORDER BY id DESC LIMIT ? OFFSET ?"
    params_paginados = params + [por_pagina, offset]
    vagas = conn.execute(query, params_paginados).fetchall()

    conn.close()

    return render_template(
        'index.html', 
        vagas=vagas, 
        q=q, 
        categoria_selecionada=categoria,
        pagina=pagina,
        total_paginas=total_paginas
    )


@app.route('/servicos')
def listar_servicos():
    busca = request.args.get('q', '').strip()
    categoria = request.args.get('categoria', '').strip()
    pagina = request.args.get('pagina', 1, type=int)
    por_pagina = 10
    offset = (pagina - 1) * por_pagina
    agora = datetime.now(fuso_mt).strftime('%Y-%m-%d %H:%M:%S')

    conn = get_db_connection()

    # Cláusula base de filtro
    where_clause = """
        WHERE status = 'aprovado' 
        AND (data_expiracao IS NULL OR data_expiracao >= ?)
    """
    params = [agora]
    
    if busca:
        where_clause += " AND (titulo_servico LIKE ? OR nome LIKE ? OR descricao LIKE ?)"
        params.extend([f'%{busca}%', f'%{busca}%', f'%{busca}%'])

    if categoria:
        where_clause += " AND categoria = ?"
        params.append(categoria)

    # 1. Contar o total de serviços para calcular o número de páginas
    count_query = f"SELECT COUNT(*) FROM servicos {where_clause}"
    total_servicos = conn.execute(count_query, params).fetchone()[0]
    total_paginas = max(1, (total_servicos + por_pagina - 1) // por_pagina)

    # 2. Buscar apenas os 10 serviços da página solicitada
    query = f"SELECT * FROM servicos {where_clause} ORDER BY id DESC LIMIT ? OFFSET ?"
    params_paginados = params + [por_pagina, offset]
    servicos = conn.execute(query, params_paginados).fetchall()

    conn.close()

    return render_template(
        'servicos.html', 
        servicos=servicos, 
        busca=busca, 
        categoria_selecionada=categoria,
        pagina=pagina,
        total_paginas=total_paginas
    )


@app.route('/cadastrar-vaga', methods=['GET', 'POST'])
def cadastrar_vaga():
    if request.method == 'POST':
        titulo = request.form['titulo']
        tipo = request.form['tipo']
        contratante = request.form['contratante']
        contato = request.form['contato']
        categoria = request.form['categoria']
        descricao = request.form['descricao']
        data_postagem = datetime.now(fuso_mt).strftime('%d/%m/%Y às %H:%M')

        file = request.files.get('imagem')
        filename = None
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        conn = get_db_connection()
        conn.execute('''
            INSERT INTO vagas (titulo, tipo, contratante, contato, categoria, descricao, imagem, status, data_postagem)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'pendente', ?)
        ''', (titulo, tipo, contratante, contato, categoria, descricao, filename, data_postagem))
        conn.commit()
        conn.close()

        flash('Vaga enviada com sucesso! Ela passará pela aprovação do administrador.')
        return redirect(url_for('index'))

    return render_template('cadastrar-vaga.html')


@app.route('/oferecer_servico', methods=['GET', 'POST'])
def oferecer_servico():
    if request.method == 'POST':
        nome = request.form.get('nome')
        titulo_servico = request.form.get('titulo_servico')
        categoria = request.form.get('categoria')
        contato = request.form.get('contato')
        descricao = request.form.get('descricao')
        data_postagem = datetime.now(fuso_mt).strftime('%d/%m/%Y às %H:%M')
        
        file = request.files.get('imagem')
        filename = None
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        conn = get_db_connection()
        conn.execute('''
            INSERT INTO servicos (nome, titulo_servico, categoria, contato, descricao, imagem, status, data_postagem)
            VALUES (?, ?, ?, ?, ?, ?, 'pendente', ?)
        ''', (nome, titulo_servico, categoria, contato, descricao, filename, data_postagem))
        conn.commit()
        conn.close()

        flash('Serviço enviado com sucesso! Aguarde a aprovação.')
        return redirect(url_for('listar_servicos'))

    return render_template('cadastrar_servico.html')


@app.route('/sobre')
def sobre():
    return render_template('sobre.html')


# --- ADMIN E AUTENTICAÇÃO ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    # 1. Se já estiver logado, entra direto no Admin sem pedir senha
    if session.get('admin_logado'):
        return redirect(url_for('admin'))

    erro = None
    if request.method == 'POST':
        usuario = request.form.get('usuario')
        senha = request.form.get('senha')

        if usuario == ADMIN_USUARIO and senha == ADMIN_SENHA:
            session['admin_logado'] = True
            session.permanent = True  # Mantém o login salvo no navegador
            return redirect(url_for('admin'))
        else:
            erro = 'Usuário ou senha incorretos!'

    return render_template('login.html', erro=erro)


@app.route('/logout')
def logout():
    session.pop('admin_logado', None)
    return redirect(url_for('index'))


@app.route('/admin')
def admin():
    if not session.get('admin_logado'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    vagas_pendentes = conn.execute("SELECT * FROM vagas WHERE status = 'pendente' OR status IS NULL ORDER BY id DESC").fetchall()
    vagas_aprovadas = conn.execute("SELECT * FROM vagas WHERE status = 'aprovado' OR status = 'aprovada' ORDER BY id DESC").fetchall()
    
    servicos_pendentes = conn.execute("SELECT * FROM servicos WHERE status = 'pendente' OR status IS NULL ORDER BY id DESC").fetchall()
    servicos_aprovados = conn.execute("SELECT * FROM servicos WHERE status = 'aprovado' ORDER BY id DESC").fetchall()
    
    conn.close()
    return render_template('admin.html', 
                           vagas_pendentes=vagas_pendentes, 
                           vagas_aprovadas=vagas_aprovadas,
                           servicos_pendentes=servicos_pendentes, 
                           servicos_aprovados=servicos_aprovados)


# --- AÇÕES DE MODERAÇÃO COM TEMPO DE VALIDADE ---

@app.route('/admin/aprovar_vaga/<int:id>', methods=['POST'])
def aprovar_vaga(id):
    if not session.get('admin_logado'):
        return redirect(url_for('login'))

    dias = int(request.form.get('validade_dias', 30))
    data_expiracao = None
    if dias > 0:
        data_expiracao = (datetime.now(fuso_mt) + timedelta(days=dias)).strftime('%Y-%m-%d %H:%M:%S')

    conn = get_db_connection()
    conn.execute("UPDATE vagas SET status = 'aprovado', data_expiracao = ? WHERE id = ?", (data_expiracao, id))
    conn.commit()
    conn.close()
    return redirect(url_for('admin'))


@app.route('/admin/excluir_vaga/<int:id>', methods=['POST'])
def excluir_vaga(id):
    if not session.get('admin_logado'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    conn.execute("DELETE FROM vagas WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin'))


@app.route('/admin/aprovar_servico/<int:id>', methods=['POST'])
def aprovar_servico(id):
    if not session.get('admin_logado'):
        return redirect(url_for('login'))

    dias = int(request.form.get('validade_dias', 30))
    data_expiracao = None
    if dias > 0:
        data_expiracao = (datetime.now(fuso_mt) + timedelta(days=dias)).strftime('%Y-%m-%d %H:%M:%S')

    conn = get_db_connection()
    conn.execute("UPDATE servicos SET status = 'aprovado', data_expiracao = ? WHERE id = ?", (data_expiracao, id))
    conn.commit()
    conn.close()
    return redirect(url_for('admin'))


@app.route('/admin/excluir_servico/<int:id>', methods=['POST'])
def excluir_servico(id):
    if not session.get('admin_logado'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    conn.execute("DELETE FROM servicos WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin'))


if __name__ == '__main__':
    app.run(debug=True)
