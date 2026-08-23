import sqlite3
import bcrypt

DB_NAME = "terminal_b3.db"

def init_db():
    """Cria as tabelas de usuários e pesquisas caso não existam."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha_hash TEXT NOT NULL,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS historico_pesquisas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            ticker TEXT NOT NULL,
            data_pesquisa TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES usuarios (id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS favoritos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            ticker TEXT NOT NULL,
            data_adicao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES usuarios (id),
            UNIQUE(user_id, ticker)
        )
    """)
    conn.commit()
    conn.close()

def gerar_hash_senha(senha: str) -> str:
    """Transforma a senha digitada em um hash seguro."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(senha.encode('utf-8'), salt).decode('utf-8')

def verificar_senha(senha: str, senha_hash: str) -> bool:
    """Valida se a senha informada bate com o hash salvo."""
    return bcrypt.checkpw(senha.encode('utf-8'), senha_hash.encode('utf-8'))

def criar_usuario(username, email, senha):
    """Cadastra um novo usuário no banco de dados."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    senha_hash = gerar_hash_senha(senha)
    try:
        cursor.execute(
            "INSERT INTO usuarios (username, email, senha_hash) VALUES (?, ?, ?)",
            (username, email, senha_hash)
        )
        conn.commit()
        return True, "Usuário cadastrado com sucesso!"
    except sqlite3.IntegrityError:
        return False, "Usuário ou E-mail já cadastrado."
    finally:
        conn.close()

def autenticar_usuario(username, senha):
    """Autentica o login do usuário."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, senha_hash FROM usuarios WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    
    if user and verificar_senha(senha, user[2]):
        return {"id": user[0], "username": user[1]}
    return None

def salvar_pesquisa(user_id, ticker):
    """Salva a busca no histórico vinculado ao ID do usuário."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO historico_pesquisas (user_id, ticker) VALUES (?, ?)",
        (user_id, ticker)
    )
    conn.commit()
    conn.close()

def obter_historico_usuario(user_id):
    """Busca os últimos 10 tickers pesquisados pelo usuário."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT ticker, data_pesquisa 
        FROM historico_pesquisas 
        WHERE user_id = ? 
        ORDER BY data_pesquisa DESC 
        LIMIT 10
    """, (user_id,))
    resultados = cursor.fetchall()
    conn.close()
    return resultados

# --- FUNÇÕES DE FAVORITOS ---
def adicionar_favorito(usuario_id, ticker):
    conn = sqlite3.connect("terminal_b3.db")
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT OR IGNORE INTO favoritos (usuario_id, ticker) VALUES (?, ?)",
            (usuario_id, ticker.upper())
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"Erro ao favoritar: {e}")
        return False
    finally:
        conn.close()

def remover_favorito(usuario_id, ticker):
    conn = sqlite3.connect("terminal_b3.db")
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM favoritos WHERE usuario_id = ? AND ticker = ?",
        (usuario_id, ticker.upper())
    )
    conn.commit()
    conn.close()

def listar_favoritos(usuario_id):
    conn = sqlite3.connect("terminal_b3.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT ticker, data_adicao FROM favoritos WHERE usuario_id = ? ORDER BY data_adicao DESC",
        (usuario_id,)
    )
    favoritos = cursor.fetchall()
    conn.close()
    return favoritos

def eh_favorito(usuario_id, ticker):
    conn = sqlite3.connect("terminal_b3.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT 1 FROM favoritos WHERE usuario_id = ? AND ticker = ?",
        (usuario_id, ticker.upper())
    )
    resultado = cursor.fetchone()
    conn.close()
    return resultado is not None

# --- FUNÇÕES DE FAVORITOS ---
def adicionar_favorito(user_id, ticker):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT OR IGNORE INTO favoritos (user_id, ticker) VALUES (?, ?)",
            (user_id, ticker.upper())
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"Erro ao favoritar: {e}")
        return False
    finally:
        conn.close()

def remover_favorito(user_id, ticker):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM favoritos WHERE user_id = ? AND ticker = ?",
        (user_id, ticker.upper())
    )
    conn.commit()
    conn.close()

def listar_favoritos(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT ticker, data_adicao FROM favoritos WHERE user_id = ? ORDER BY data_adicao DESC",
        (user_id,)
    )
    favoritos = cursor.fetchall()
    conn.close()
    return favoritos

def eh_favorito(user_id, ticker):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT 1 FROM favoritos WHERE user_id = ? AND ticker = ?",
        (user_id, ticker.upper())
    )
    resultado = cursor.fetchone()
    conn.close()
    return resultado is not None