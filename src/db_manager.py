# src/db_manager.py

import sqlite3
import datetime
import os
from src.config import DB_NAME, IMAGES_DIR # Importa DB_NAME e IMAGES_DIR de config

def criar_tabela():
    """Cria a tabela de historico_qr_codes se ela não existir."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS historico_qr_codes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            texto_qr TEXT NOT NULL,
            nome_arquivo TEXT NOT NULL,
            caminho_completo TEXT NOT NULL,
            data_criacao TEXT NOT NULL,
            cor_frente TEXT,
            cor_fundo TEXT,
            nivel_erro TEXT
        )
    ''')
    conn.commit()
    conn.close()

def migrar_tabela():
    """Adiciona colunas para cor e nível de erro se não existirem."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE historico_qr_codes ADD COLUMN cor_frente TEXT")
        conn.commit()
    except sqlite3.OperationalError as e:
        if "duplicate column name: cor_frente" not in str(e): pass

    try:
        cursor.execute("ALTER TABLE historico_qr_codes ADD COLUMN cor_fundo TEXT")
        conn.commit()
    except sqlite3.OperationalError as e:
        if "duplicate column name: cor_fundo" not in str(e): pass

    try:
        cursor.execute("ALTER TABLE historico_qr_codes ADD COLUMN nivel_erro TEXT")
        conn.commit()
    except sqlite3.OperationalError as e:
        if "duplicate column name: nivel_erro" not in str(e): pass
    finally:
        conn.close()

def registrar_historico(texto_qr, nome_arquivo, caminho_completo, cor_frente, cor_fundo, nivel_erro):
    """Registra a geração do QR Code no banco de dados, incluindo cores e nível de erro."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    data_hora_atual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO historico_qr_codes (texto_qr, nome_arquivo, caminho_completo, data_criacao, cor_frente, cor_fundo, nivel_erro) VALUES (?, ?, ?, ?, ?, ?, ?)",
                   (texto_qr, nome_arquivo, caminho_completo, data_hora_atual, cor_frente, cor_fundo, nivel_erro))
    conn.commit()
    conn.close()

def atualizar_registro_historico(record_id, texto_qr, nome_arquivo, caminho_completo, cor_frente, cor_fundo, nivel_erro):
    """Atualiza um registro existente no banco de dados."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    data_hora_atual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("UPDATE historico_qr_codes SET texto_qr=?, nome_arquivo=?, caminho_completo=?, data_criacao=?, cor_frente=?, cor_fundo=?, nivel_erro=? WHERE id=?",
                   (texto_qr, nome_arquivo, caminho_completo, data_hora_atual, cor_frente, cor_fundo, nivel_erro, record_id))
    conn.commit()
    conn.close()

def buscar_historico():
    """Retorna todos os registros do histórico, incluindo novas colunas."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, texto_qr, nome_arquivo, caminho_completo, data_criacao, cor_frente, cor_fundo, nivel_erro FROM historico_qr_codes ORDER BY data_criacao DESC")
    registros = cursor.fetchall()
    conn.close()
    return registros

def deletar_registro_historico(registro_id):
    """Deleta um registro do histórico pelo ID."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM historico_qr_codes WHERE id = ?", (registro_id,))
    conn.commit()
    conn.close()

# As chamadas de criação e migração de tabela serão feitas pela aplicação principal ou ao importar
# criar_tabela()
# migrar_tabela()