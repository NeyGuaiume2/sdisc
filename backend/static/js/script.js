// Elementos DOM
const startBtn = document.getElementById('start-btn');
const prevBtn = document.getElementById('prev-btn');
const nextBtn = document.getElementById('next-btn');
const countdownEl = document.getElementById('countdown');
const questionNumberEl = document.getElementById('question-number');
const optionsListEl = document.getElementById('options-list');

// Seções
const introSection = document.getElementById('intro');
const assessmentSection = document.getElementById('assessment');
const resultsSection = document.getElementById('results');

// Variáveis de estado
let questions = [];
let currentQuestionIndex = 0;
let responses = {};
let timerInterval;
let timeLeft = 15;

// Evento quando a página carrega
document.addEventListener('DOMContentLoaded', () => {
    // Carregar perguntas da API
    fetch('/api/questions')
        .then(response => response.json())
        .then(data => {
            questions = data;
            console.log('Perguntas carregadas:', questions);
        })
        .catch(error => {
            console.error('Erro ao carregar perguntas:', error);
        });
});

// Iniciar avaliação
startBtn.addEventListener('click', () => {
    introSection.style.display = 'none';
    assessmentSection.style.display = 'block';
    
    // Carregar primeira questão
    loadQuestion(0);
    
    // Iniciar timer
    startTimer();
});

// Carregar questão
function loadQuestion(index) {
    if (!questions.length || index < 0 || index >= questions.length) return;
    
    currentQuestionIndex = index;
    const question = questions[index];
    
    // Atualizar número da questão
    questionNumberEl.textContent = index + 1;
    
    // Limpar opções anteriores
    optionsListEl.innerHTML = '';
    
    // Adicionar novas opções
    question.options.forEach(option => {
        const optionDiv = document.createElement('div');
        optionDiv.className = 'option-item';
        
        // Texto da opção
        const optionText = document.createElement('div');
        optionText.className = 'option-text';
        optionText.textContent = option.text;
        
        // Rádio para MAIS
        const mostRadioContainer = document.createElement('div');
        mostRadioContainer.className = 'radio-container';
        const mostRadio = document.createElement('input');
        mostRadio.type = 'radio';
        mostRadio.name = `most-${question.id}`;
        mostRadio.value = option.id;
        mostRadio.addEventListener('change', () => handleOptionSelect('most', option.id));
        mostRadioContainer.appendChild(mostRadio);
        
        // Rádio para MENOS
        const leastRadioContainer = document.createElement('div');
        leastRadioContainer.className = 'radio-container';
        const leastRadio = document.createElement('input');
        leastRadio.type = 'radio';
        leastRadio.name = `least-${question.id}`;
        leastRadio.value = option.id;
        leastRadio.addEventListener('change', () => handleOptionSelect('least', option.id));
        leastRadioContainer.appendChild(leastRadio);
        
        // Marcar rádios se já foram selecionados anteriormente
        if (responses[question.id]) {
            if (responses[question.id].most === option.id) {
                mostRadio.checked = true;
            }
            if (responses[question.id].least === option.id) {
                leastRadio.checked = true;
            }
        }
        
        // Montar opção completa
        optionDiv.appendChild(optionText);
        optionDiv.appendChild(mostRadioContainer);
        optionDiv.appendChild(leastRadioContainer);
        
        optionsListEl.appendChild(optionDiv);
    });
    
    // Atualizar estado dos botões
    updateButtonState();
    
    // Reiniciar timer
    resetTimer();
}

// Lidar com seleção de opção
function handleOptionSelect(type, optionId) {
    const questionId = questions[currentQuestionIndex].id;
    
    // Inicializar resposta para a questão atual se não existir
    if (!responses[questionId]) {
        responses[questionId] = {};
    }
    
    // Armazenar resposta
    responses[questionId][type] = optionId;
    
    // Impedir que a mesma opção seja selecionada como MAIS e MENOS
    if (type === 'most' && responses[questionId].least === optionId) {
        responses[questionId].least = null;
        const leastRadios = document.getElementsByName(`least-${questionId}`);
        leastRadios.forEach(radio => {
            if (radio.value === optionId) {
                radio.checked = false;
            }
        });
    } else if (type === 'least' && responses[questionId].most === optionId) {
        responses[questionId].most = null;
        const mostRadios = document.getElementsByName(`most-${questionId}`);
        mostRadios.forEach(radio => {
            if (radio.value === optionId) {
                radio.checked = false;
            }
        });
    }
    
    // Atualizar estado dos botões
    updateButtonState();
}

// Atualizar estado dos botões de navegação
function updateButtonState() {
    const questionId = questions[currentQuestionIndex].id;
    const currentResponse = responses[questionId] || {};
    
    // Habilitar próximo se ambos MAIS e MENOS foram selecionados
    nextBtn.disabled = !(currentResponse.most && currentResponse.least);
    
    // Habilitar anterior se não estiver na primeira questão
    prevBtn.disabled = currentQuestionIndex === 0;
    
    // Mudar texto do botão Próximo para Finalizar na última questão
    if (currentQuestionIndex === questions.length - 1) {
        nextBtn.textContent = 'Finalizar';
    } else {
        nextBtn.textContent = 'Próximo';
    }
}

// Eventos de navegação
nextBtn.addEventListener('click', () => {
    // Se for a última questão, finalizar avaliação
    if (currentQuestionIndex === questions.length - 1) {
        finishAssessment();
        return;
    }
    
    // Avançar para próxima questão
    loadQuestion(currentQuestionIndex + 1);
});

prevBtn.addEventListener('click', () => {
    // Voltar para questão anterior
    loadQuestion(currentQuestionIndex - 1);
});

// Timer
function startTimer() {
    timeLeft = 15;
    countdownEl.textContent = timeLeft;
    
    clearInterval(timerInterval);
    timerInterval = setInterval(() => {
        timeLeft--;
        countdownEl.textContent = timeLeft;
        
        if (timeLeft <= 5) {
            countdownEl.style.color = 'red';
        } else {
            countdownEl.style.color = '#e67e22';
        }
        
        if (timeLeft <= 0) {
            // Tempo esgotado, avançar para próxima questão
            clearInterval(timerInterval);
            
            // Se estiver na última questão, finalizar
            if (currentQuestionIndex === questions.length - 1) {
                finishAssessment();
            } else {
                // Se tiver selecionado MAIS e MENOS, avançar
                const questionId = questions[currentQuestionIndex].id;
                const currentResponse = responses[questionId] || {};
                
                if (currentResponse.most && currentResponse.least) {
                    loadQuestion(currentQuestionIndex + 1);
                } else {
                    // Se não tiver selecionado, reiniciar timer para mesma questão
                    resetTimer();
                }
            }
        }
    }, 1000);
}

function resetTimer() {
    timeLeft = 15;
    countdownEl.textContent = timeLeft;
    countdownEl.style.color = '#e67e22';
    
    clearInterval(timerInterval);
    startTimer();
}

// Finalizar avaliação
function finishAssessment() {
    // Parar timer
    clearInterval(timerInterval);
    
    // Verificar se todas as perguntas foram respondidas
    const questionsAnswered = Object.keys(responses).length;
    
    if (questionsAnswered < questions.length) {
        alert(`Você respondeu apenas ${questionsAnswered} de ${questions.length} perguntas. Certifique-se de responder todas as perguntas.`);
        // Voltar para a primeira pergunta não respondida
        for (let i = 0; i < questions.length; i++) {
            const questionId = questions[i].id;
            if (!responses[questionId] || !responses[questionId].most || !responses[questionId].least) {
                loadQuestion(i);
                return;
            }
        }
        return;
    }
    
    // Exibir indicador de carregamento
    resultsSection.innerHTML = '<div class="loading">Calculando seus resultados...</div>';
    assessmentSection.style.display = 'none';
    resultsSection.style.display = 'block';
    
    // Enviar respostas para cálculo
    fetch('/api/calculate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(responses)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`Erro HTTP: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log('Resultados calculados:', data);
        
        // Verificar se há resultados
        if (!data || !data.results) {
            throw new Error('Resultados inválidos recebidos do servidor');
        }
        
        // Exibir resultados
        displayResults(data.results);
        
        // Salvar avaliação
        return fetch('/api/assessment', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                responses: responses,
                results: data.results
            })
        });
    })
    .then(response => response.json())
    .then(data => {
        console.log('Avaliação salva:', data);
    })
    .catch(error => {
        console.error('Erro ao processar avaliação:', error);
        resultsSection.innerHTML = `
            <div class="error-message">
                <h3>Ocorreu um erro ao processar seus resultados</h3>
                <p>${error.message}</p>
                <button class="btn primary" onclick="location.reload()">Tentar novamente</button>
            </div>
        `;
    });
}

// Função para exibir resultados
function displayResults(results) {
    // Elementos para exibir na seção de resultados
    const resultsHTML = `
        <h2>Seus Resultados DISC</h2>
        
        <div class="results-container">
            <div class="chart-container">
                <h3>Seu Perfil DISC</h3>
                <canvas id="disc-chart"></canvas>
                
                <div class="disc-scores">
                    <div class="disc-score">
                        <strong>D (Dominância):</strong> ${results.disc_scores.D} - ${results.disc_levels.D}
                    </div>
                    <div class="disc-score">
                        <strong>I (Influência):</strong> ${results.disc_scores.I} - ${results.disc_levels.I}
                    </div>
                    <div class="disc-score">
                        <strong>S (Estabilidade):</strong> ${results.disc_scores.S} - ${results.disc_levels.S}
                    </div>
                    <div class="disc-score">
                        <strong>C (Conformidade):</strong> ${results.disc_scores.C} - ${results.disc_levels.C}
                    </div>
                </div>
            </div>
            
            <div class="profile-description">
                <h3>Seu Perfil: ${results.primary_type} - ${results.primary_description.title}</h3>
                <p>${results.profile_summary}</p>
            </div>
        </div>
        
        <div class="detailed-report">
            <h3>Relatório Detalhado</h3>
            
            <h4>Pontos Fortes</h4>
            <ul>
                ${results.detailed_report.primary_strengths.map(strength => `<li>${strength}</li>`).join('')}
            </ul>
            
            <h4>Áreas de Desenvolvimento</h4>
            <ul>
                ${results.detailed_report.development_areas_list.map(area => `<li>${area}</li>`).join('')}
            </ul>
            
            <h4>Como Trabalhar com Você</h4>
            <p>${results.primary_description.how_to_work_with}</p>
        </div>
        
        <div class="actions">
            <button class="btn primary" id="download-btn">Baixar Relatório PDF</button>
            <button class="btn secondary" id="restart-btn">Fazer Novo Teste</button>
        </div>
    `;
    
    // Atualizar o conteúdo da seção de resultados
    resultsSection.innerHTML = resultsHTML;
    
    // Adicionar eventos aos novos botões
    document.getElementById('restart-btn').addEventListener('click', () => {
        location.reload();
    });
    
    document.getElementById('download-btn').addEventListener('click', () => {
        // Implementação para download do relatório em PDF
        alert('Funcionalidade de download em desenvolvimento');
    });
    
    // Criar gráfico com Chart.js (assumindo que está incluído na página)
    try {
        if (typeof Chart !== 'undefined') {
            const ctx = document.getElementById('disc-chart').getContext('2d');
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: ['D', 'I', 'S', 'C'],
                    datasets: [{
                        label: 'Pontuação DISC',
                        data: [
                            results.disc_scores.D,
                            results.disc_scores.I,
                            results.disc_scores.S,
                            results.disc_scores.C
                        ],
                        backgroundColor: [
                            'rgba(255, 99, 132, 0.7)',
                            'rgba(255, 206, 86, 0.7)',
                            'rgba(54, 162, 235, 0.7)',
                            'rgba(75, 192, 192, 0.7)'
                        ],
                        borderColor: [
                            'rgba(255, 99, 132, 1)',
                            'rgba(255, 206, 86, 1)',
                            'rgba(54, 162, 235, 1)',
                            'rgba(75, 192, 192, 1)'
                        ],
                        borderWidth: 1
                    }]
                },
                options: {
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        } else {
            console.warn('Chart.js não está disponível. Incluir <script src="https://cdn.jsdelivr.net/npm/chart.js"></script> no HTML.');
            
            // Alternativa simples sem Chart.js
            const chartContainer = document.querySelector('.chart-container');
            const canvas = document.getElementById('disc-chart');
            canvas.remove();
            
            const simpleChart = document.createElement('div');
            simpleChart.className = 'simple-chart';
            simpleChart.innerHTML = `
                <div class="simple-bar" style="--value: ${Math.max(0, results.disc_scores.D * 5 + 50)}%;">D: ${results.disc_scores.D}</div>
                <div class="simple-bar" style="--value: ${Math.max(0, results.disc_scores.I * 5 + 50)}%;">I: ${results.disc_scores.I}</div>
                <div class="simple-bar" style="--value: ${Math.max(0, results.disc_scores.S * 5 + 50)}%;">S: ${results.disc_scores.S}</div>
                <div class="simple-bar" style="--value: ${Math.max(0, results.disc_scores.C * 5 + 50)}%;">C: ${results.disc_scores.C}</div>
            `;
            
            chartContainer.insertBefore(simpleChart, chartContainer.firstChild);
            
            // Adicionar CSS para barras simples
            const style = document.createElement('style');
            style.textContent = `
                .simple-chart {
                    height: 200px;
                    display: flex;
                    align-items: flex-end;
                    justify-content: space-around;
                    margin: 20px 0;
                }
                .simple-bar {
                    width: 40px;
                    height: var(--value);
                    background-color: #3498db;
                    color: white;
                    text-align: center;
                    padding-top: 5px;
                    border-radius: 4px 4px 0 0;
                }
            `;
            document.head.appendChild(style);
        }
    } catch (e) {
        console.error('Erro ao criar gráfico:', e);
    }
}
