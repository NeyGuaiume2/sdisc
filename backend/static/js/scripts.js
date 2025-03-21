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
    
    // Enviar respostas para cálculo
    fetch('/api/calculate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(responses)
    })
    .then(response => response.json())
    .then(data => {
        console.log('Resultados calculados:', data);
        
        // Exibir resultados
        displayResults(data);
        
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
    });
    
    // Esconder seção de avaliação e mostrar resultados
    assessmentSection.style.display = 'none';
    resultsSection.style.display = 'block';
}

// Ex