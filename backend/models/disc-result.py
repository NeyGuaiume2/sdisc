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
    __tablename__ = 'disc_results'
    
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
        
        # Garante que raw_responses seja convertido para string JSON
        if isinstance(raw_responses, dict):
            self.raw_responses = json.dumps(raw_responses)
        else:
            self.raw_responses = raw_responses or '{}'
        
        if disc_result:
            if isinstance(disc_result['disc_scores'], dict):
                self.disc_scores = json.dumps(disc_result['disc_scores'])
            else:
                self.disc_scores = disc_result['disc_scores']
                
            self.primary_type = disc_result['primary_type']
            self.secondary_type = disc_result['secondary_type']
            
            if isinstance(disc_result['disc_levels'], dict):
                self.disc_levels = json.dumps(disc_result['disc_levels'])
            else:
                self.disc_levels = disc_result['disc_levels']
    
    def get_raw_responses(self):
        """Retorna as respostas brutas como dicionário Python."""
        if isinstance(self.raw_responses, dict):
            return self.raw_responses
        return json.loads(self.raw_responses)
    
    def get_disc_scores(self):
        """Retorna os scores DISC como dicionário Python."""
        if isinstance(self.disc_scores, dict):
            return self.disc_scores
        return json.loads(self.disc_scores)
    
    def get_disc_levels(self):
        """Retorna os níveis DISC como dicionário Python."""
        if isinstance(self.disc_levels, dict):
            return self.disc_levels
        return json.loads(self.disc_levels)
    
    def to_dict(self):
        """Converte o objeto em dicionário para serialização."""
        return {
            'id': self.id,
            'user_name': self.user_name,
            'user_email': self.user_email,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'primary_type': self.primary_type,
            'secondary_type': self.secondary_type,
            'disc_scores': self.get_disc_scores(),
            'disc_levels': self.get_disc_levels()
        }