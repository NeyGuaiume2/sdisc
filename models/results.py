import sqlite3
import json
from datetime import datetime
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'disc.db')

def init_db():
    """Inicializa o banco de dados de resultados"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Criar tabela para armazenar os resultados
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS disc_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_name TEXT,
        email TEXT,
        answers TEXT,  -- Armazenado como JSON
        scores TEXT,   -- Armazenado como JSON
        predominant TEXT,
        secondary TEXT,
        profile TEXT,
        created_at TIMESTAMP
    )
    ''')
    
    conn.commit()
    conn.close()

def save_results(user_data, answers, results):
    """
    Salva os resultados da avaliação DISC no banco de dados
    
    Args:
        user_data (dict): Dados do usuário (nome, email)
        answers (list): Lista de respostas às perguntas
        results (dict): Resultados calculados da avaliação DISC
    
    Returns:
        int: ID do resultado salvo
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
    INSERT INTO disc_results 
    (user_name, email, answers, scores, predominant, secondary, profile, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        user_data.get('name', 'Anônimo'),
        user_data.get('email', ''),
        json.dumps(answers),
        json.dumps(results.get('normalizedScores', {})),
        results.get('predominant', ''),
        results.get('secondary', ''),
        results.get('profile', ''),
        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ))
    
    result_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return result_id

def get_result(result_id):
    """
    Recupera um resultado pelo ID
    
    Args:
        result_id (int): ID do resultado
    
    Returns:
        dict: Dados do resultado
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM disc_results WHERE id = ?', (result_id,))
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        return None
    
    result = dict(row)
    
    # Converter JSON para dicionários Python
    result['answers'] = json.loads(result['answers'])
    result['scores'] = json.loads(result['scores'])
    
    conn.close()
    return result