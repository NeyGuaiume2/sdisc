# Arquivo: c:\pyp\sdisc\app\models.py

# Adicione as seguintes modificações ao arquivo models.py

class DISCResult(db.Model):
    __tablename__ = 'disc_results'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    session_id = db.Column(db.String(50), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Pontuações DISC
    d_score = db.Column(db.Integer, default=0)
    i_score = db.Column(db.Integer, default=0)
    s_score = db.Column(db.Integer, default=0)
    c_score = db.Column(db.Integer, default=0)
    
    # Categorias de intensidade
    d_intensity = db.Column(db.String(10), default="Médio")  # Baixo, Médio, Alto
    i_intensity = db.Column(db.String(10), default="Médio")
    s_intensity = db.Column(db.String(10), default="Médio")
    c_intensity = db.Column(db.String(10), default="Médio")
    
    # Perfil predominante e secundário
    primary_profile = db.Column(db.String(1))
    secondary_profile = db.Column(db.String(1))
    
    # Relação com respostas
    responses = db.relationship('DISCResponse', backref='result', lazy=True)
    
    def __repr__(self):
        return f'<DISCResult {self.id}>'
    
    def set_intensities(self):
        """Define as intensidades com base nos scores"""
        self.d_intensity = self._get_intensity(self.d_score)
        self.i_intensity = self._get_intensity(self.i_score)
        self.s_intensity = self._get_intensity(self.s_score)
        self.c_intensity = self._get_intensity(self.c_score)
    
    def _get_intensity(self, score):
        """Determina a intensidade baseada no score"""
        if score <= 8:
            return "Baixo"
        elif score <= 16:
            return "Médio"
        else:
            return "Alto"
    
    def determine_profiles(self):
        """Determina os perfis predominante e secundário"""
        scores = {
            'D': self.d_score,
            'I': self.i_score,
            'S': self.s_score,
            'C': self.c_score
        }
        
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        self.primary_profile = sorted_scores[0][0]
        self.secondary_profile = sorted_scores[1][0]