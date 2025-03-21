// Algoritmo de pontuação DISC

/**
 * Calcula a pontuação DISC com base nas respostas do usuário
 * @param {Array} answers - Array de respostas no formato {questionId, most, least}
 * @return {Object} Resultados DISC calculados
 */
function calculateDISCScore(answers) {
    // Inicializar contadores
    const counts = {
        A: { most: 0, least: 0 },
        B: { most: 0, least: 0 },
        C: { most: 0, least: 0 },
        D: { most: 0, least: 0 }
    };
    
    // Contar respostas "MAIS" e "MENOS" para cada letra
    answers.forEach(answer => {
        if (answer.most) {
            counts[answer.most].most += 1;
        }
        if (answer.least) {
            counts[answer.least].least += 1;
        }
    });
    
    // Calcular pontuação final (MAIS - MENOS) para cada letra
    const scores = {
        A: counts.A.most - counts.A.least,
        B: counts.B.most - counts.B.least,
        C: counts.C.most - counts.C.least,
        D: counts.D.most - counts.D.least
    };
    
    // Mapear letras para fatores DISC
    const discScores = {
        D: scores.A, // Dominância
        I: scores.B, // Influência
        S: scores.C, // Estabilidade
        C: scores.D  // Conformidade
    };
    
    // Normalizar pontuações para escala de 1 a 25
    const totalQuestions = answers.length;
    const normalizedScores = {
        D: normalizeScore(discScores.D, totalQuestions),
        I: normalizeScore(discScores.I, totalQuestions),
        S: normalizeScore(discScores.S, totalQuestions),
        C: normalizeScore(discScores.C, totalQuestions)
    };
    
    // Determinar o perfil predominante
    const predominant = Object.entries(normalizedScores)
        .sort((a, b) => b[1] - a[1])[0][0];
    
    // Determinar o perfil secundário (segundo maior)
    const secondary = Object.entries(normalizedScores)
        .sort((a, b) => b[1] - a[1])[1][0];
    
    return {
        rawScores: discScores,
        normalizedScores,
        counts,
        predominant,
        secondary,
        profile: `${predominant}${secondary}`
    };
}

/**
 * Normaliza uma pontuação para a escala de 1 a 25
 * @param {number} score - Pontuação bruta
 * @param {number} totalQuestions - Número total de perguntas
 * @return {number} Pontuação normalizada
 */
function normalizeScore(score, totalQuestions) {
    // A escala base vai de -totalQuestions a +totalQuestions
    // Convertemos para escala 1-25
    const minPossible = -totalQuestions;
    const maxPossible = totalQuestions;
    const range = maxPossible - minPossible;
    
    // Normalização para 1-25
    return Math.round(((score - minPossible) / range) * 24) + 1;
}

/**
 * Interpreta o nível de cada fator DISC
 * @param {number} score - Pontuação normalizada (1-25)
 * @return {string} Interpretação do nível
 */
function interpretLevel(score) {
    if (score <= 8) return "Baixo";
    if (score <= 16) return "Médio";
    return "Alto";
}

/**
 * Retorna a descrição do perfil baseada nos resultados
 * @param {Object} results - Resultados DISC calculados
 * @return {Object} Descrições do perfil
 */
function getProfileDescription(results) {
    const { normalizedScores } = results;
    
    const levelInterpretations = {
        D: interpretLevel(normalizedScores.D),
        I: interpretLevel(normalizedScores.I),
        S: interpretLevel(normalizedScores.S),
        C: interpretLevel(normalizedScores.C)
    };
    
    // Aqui você adicionaria descrições detalhadas para cada combinação
    // Por simplicidade, vamos retornar apenas os níveis
    return {
        levels: levelInterpretations,
        strengths: generateStrengths(levelInterpretations),
        weaknesses: generateWeaknesses(levelInterpretations),
        recommendations: generateRecommendations(levelInterpretations, results.predominant)
    };
}

// Funções auxiliares para gerar descrições
function generateStrengths(levels) {
    // Esta função geraria pontos fortes com base no perfil
    // Simplificado para demonstração
    const strengths = [];
    
    if (levels.D === "Alto") {
        strengths.push("Capacidade de tomar decisões rápidas");
        strengths.push("Foco em resultados");
        strengths.push("Determinação para superar obstáculos");
    }
    
    if (levels.I === "Alto") {
        strengths.push("Excelente comunicação");
        strengths.push("Habilidade para inspirar e motivar outros");
        strengths.push("Criatividade e entusiasmo");
    }
    
    if (levels.S === "Alto") {
        strengths.push("Paciência e consistência");
        strengths.push("Lealdade e confiabilidade");
        strengths.push("Capacidade de trabalhar bem em equipe");
    }
    
    if (levels.C === "Alto") {
        strengths.push("Atenção aos detalhes");
        strengths.push("Análise crítica e precisão");
        strengths.push("Capacidade de seguir padrões e procedimentos");
    }
    
    return strengths;
}

function generateWeaknesses(levels) {
    // Esta função geraria pontos fracos com base no perfil
    // Simplificado para demonstração
    const weaknesses = [];
    
    if (levels.D === "Alto") {
        weaknesses.push("Pode ser percebido como agressivo ou dominador");
        weaknesses.push("Impaciência com processos lentos");
        weaknesses.push("Tendência a ignorar os sentimentos dos outros");
    }
    
    if (levels.I === "Alto") {
        weaknesses.push("Pode ser desorganizado ou disperso");
        weaknesses.push("Tende a falar mais do que ouvir");
        weaknesses.push("Pode tomar decisões impulsivas");
    }
    
    if (levels.S === "Baixo") {
        weaknesses.push("Dificuldade com mudanças rápidas");
        weaknesses.push("Pode evitar conflitos necessários");
        weaknesses.push("Resistência a inovações");
    }
    
    if (levels.C === "Baixo") {
        weaknesses.push("Pode ser crítico ou perfeccionista demais");
        weaknesses.push("Dificuldade em tomar decisões rápidas");
        weaknesses.push("Pode ficar preso em análises excessivas");
    }
    
    return weaknesses;
}

function generateRecommendations(levels, predominant) {
    // Esta função geraria recomendações com base no perfil
    // Simplificado para demonstração
    const recommendations = [];
    
    switch (predominant) {
        case 'D':
            recommendations.push("Pratique a escuta ativa para compreender melhor as necessidades dos outros");
            recommendations.push("Desenvolva paciência para processos que exigem mais tempo");
            recommendations.push("Considere o impacto emocional de suas decisões nos membros da equipe");
            break;
        case 'I':
            recommendations.push("Utilize técnicas de organização e planejamento");
            recommendations.push("Pratique ouvir mais e falar menos em reuniões importantes");
            recommendations.push("Desenvolva disciplina para concluir tarefas antes de iniciar novas");
            break;
        case 'S':
            recommendations.push("Trabalhe em sua adaptabilidade a mudanças");
            recommendations.push("Pratique técnicas de assertividade");
            recommendations.push("Desenvolva habilidades para lidar com conflitos de forma construtiva");
            break;
        case 'C':
            recommendations.push("Trabalhe na tomada de decisões mais ágil");
            recommendations.push("Desenvolva tolerância para ambiguidades");
            recommendations.push("Pratique delegar tarefas em vez de tentar controlar tudo");
            break;
    }
    
    return recommendations;
}

// Exportar funções para uso em outros arquivos
if (typeof module !== 'undefined') {
    module.exports = {
        calculateDISCScore,
        getProfileDescription
    };
}