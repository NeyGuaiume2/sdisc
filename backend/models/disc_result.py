"""
Modelo de banco de dados para armazenar resultados da avaliação DISC.
"""

from datetime import datetime
import json
from backend.db import db

class DISCResult(db.Model):
    """
    Modelo para armazenar resultados da avaliação DISC no banco de dados.
    """
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100), nullable=True)
    user_email = db.Column(db.String(100), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Respostas brutas (formato JSON)
    raw_responses = db.Column(db.Text, nullable=False)
    
    # Resultados calculados (formato JSON)
    disc_scores = db.Column(db.Text, nullable=False)
    
    # Tipos primário e secundário
    primary_type = db.Column(db.String(1), nullable=False)
    secondary_type = db.Column(db.String(1), nullable=False)
    
    # Níveis DISC (formato JSON)
    disc_levels = db.Column(db.Text, nullable=False)
    
    def __init__(self, user_name=None, user_email=None, raw_responses=None, disc_result=None):
        self.user_name = user_name
        self.user_email = user_email
        self.raw_responses = json.dumps(raw_responses)
        
        if disc_result:
            self.disc_scores = json.dumps(disc_result['disc_scores'])
            self.primary_type = disc_result['primary_type']
            self.secondary_type = disc_result['secondary_type']
            self.disc_levels = json.dumps(disc_result['disc_levels'])
    
    def get_raw_responses(self):
        """Retorna as respostas brutas como dicionário Python."""
        return json.loads(self.raw_responses)
    
    def get_disc_scores(self):
        """Retorna os scores DISC como dicionário Python."""
        return json.loads(self.disc_scores)
    
    def get_disc_levels(self):
        """Retorna os níveis DISC como dicionário Python."""
        return json.loads(self.disc_levels)
    
    def to_dict(self):
        """Converte o objeto em dicionário para serialização."""
        return {
            'id': self.id,
            'user_name': self.user_name,
            'user_email': self.user_email,
            'timestamp': self.timestamp.isoformat(),
            'primary_type': self.primary_type,
            'secondary_type': self.secondary_type,
            'disc_scores': self.get_disc_scores(),
            'disc_levels': self.get_disc_levels()
        } 
