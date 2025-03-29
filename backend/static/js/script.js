// Variáveis globais para controle do quiz
let currentQuestionIndex = 0;
let totalQuestions = 4;  // Reduzido para 4 questões para testes
let responses = {};
let countdownTimer;

// Perguntas do quiz (temporárias para testes)
const questions = [
    {
        "id": 1,
        "options": [
            {"id": "A", "text": "DETERMINADO"},
            {"id": "B", "text": "CONFIANTE"},
            {"id": "C", "text": "CONSISTENTE"},
            {"id": "D", "text": "PRECISO"}
        ]
    },
    {
        "id": 2,
        "options": [
            {"id": "A", "text": "DIRETO"},
            {"id": "B", "text": "PERSUASIVO"},
            {"id": "C", "text": "LEAL"},
            {"id": "D", "text": "CUIDADOSO"}
        ]
    },
    {
        "id": 3,
        "options": [
            {"id": "A", "text": "COMPETITIVO"},
            {"id": "B", "text": "SOCIÁVEL"},
            {"id": "C", "text": "PACIENTE"},
            {"id": "D", "text": "ANALÍTICO"}
        ]
    },
    {
        "id": 4,
        "options": [
            {"id": "A", "text": "ASSERTIVO"},
            {"id": "B", "text": "EXPRESSIVO"},
            {"id": "C", "text": "AMIGÁVEL"},
            {"id": "D", "text": "PRUDENTE"}
        ]
    }
];

document.addEventListener('DOMContentLoaded', () => {
    const startBtn = document.getElementById('start-btn');
    const introSection = document.getElementById('intro');
    const assessmentSection = document.getElementById('assessment');
    const resultsSection = document.getElementById('results');
    const optionsList = document.getElementById('options-list');
    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn');
    const questionNumber = document.getElementById('question-number');
    const countdown = document.getElementById('countdown');
    const newAssessmentBtn = document.getElementById('new-assessment');

    // Função para iniciar a avaliação
    function startAssessment() {
        introSection.style.display = 'none';
        assessmentSection.style.display = 'block';
        loadQuestion(0);
        startCountdown();
    }

    // Carregar pergunta
    function loadQuestion(index) {
        const question = questions[index];
        optionsList.innerHTML = '';
        currentQuestionIndex = index;

        // Atualizar número da questão
        questionNumber.textContent = index + 1;

        // Criar opções para a pergunta atual
        question.options.forEach(option => {
            const optionRow = document.createElement('div');
            optionRow.classList.add('option-row');
            optionRow.innerHTML = `
                <div class="option-text">${option.text}</div>
                <div class="option-selector">
                    <input type="radio" name="most" value="${option.id}" class="most-option">
                    <input type="radio" name="least" value="${option.id}" class="least-option">
                </div>
            `;
            optionsList.appendChild(optionRow);
        });

        // Habilitar/desabilitar botões de navegação
        prevBtn.disabled = (index === 0);
        nextBtn.disabled = !hasSelectedOptions();

        // Adicionar event listeners para as opções
        const mostOptions = document.querySelectorAll('.most-option');
        const leastOptions = document.querySelectorAll('.least-option');

        mostOptions.forEach(radio => {
            radio.addEventListener('change', () => {
                checkNextButton();
                radio.closest('.option-row').classList.add('most-selected');
                mostOptions.forEach(otherRadio => {
                    if (otherRadio !== radio) {
                        otherRadio.closest('.option-row').classList.remove('most-selected');
                    }
                });
            });
        });

        leastOptions.forEach(radio => {
            radio.addEventListener('change', () => {
                checkNextButton();
                radio.closest('.option-row').classList.add('least-selected');
                leastOptions.forEach(otherRadio => {
                    if (otherRadio !== radio) {
                        otherRadio.closest('.option-row').classList.remove('least-selected');
                    }
                });
            });
        });
    }

    // Verificar se opções foram selecionadas
    function hasSelectedOptions() {
        const currentMost = document.querySelector('input[name="most"]:checked');
        const currentLeast = document.querySelector('input[name="least"]:checked');
        return currentMost && currentLeast && currentMost !== currentLeast;
    }

    // Checar botão próximo
    function checkNextButton() {
        nextBtn.disabled = !hasSelectedOptions();
    }

    // Iniciar contagem regressiva
    function startCountdown() {
        let timeLeft = 15;
        countdown.textContent = timeLeft;

        clearInterval(countdownTimer);
        countdownTimer = setInterval(() => {
            timeLeft--;
            countdown.textContent = timeLeft;

            if (timeLeft === 0) {
                clearInterval(countdownTimer);
                goToNextQuestion();
            }
        }, 1000);
    }

    // Ir para próxima questão
    function goToNextQuestion() {
        // Salvar respostas
        const currentMost = document.querySelector('input[name="most"]:checked');
        const currentLeast = document.querySelector('input[name="least"]:checked');

        if (currentMost && currentLeast) {
            responses[currentQuestionIndex + 1] = {
                most: currentMost.value,
                least: currentLeast.value
            };
        }

        // Ir para próxima questão
        if (currentQuestionIndex < totalQuestions - 1) {
            loadQuestion(currentQuestionIndex + 1);
            startCountdown();
        } else {
            // Finalizar avaliação
            finishAssessment();
        }
    }

    // Ir para questão anterior
    function goToPreviousQuestion() {
        if (currentQuestionIndex > 0) {
            loadQuestion(currentQuestionIndex - 1);
            startCountdown();
        }
    }

    // Finalizar avaliação
    function finishAssessment() {
        assessmentSection.style.display = 'none';
        resultsSection.style.display = 'block';
        clearInterval(countdownTimer);

        // Aqui você faria a chamada à API para calcular o resultado
        calculateDiscResult(responses);
    }

    // Calcular resultado DISC
    async function calculateDiscResult(responses) {
        try {
            const response = await fetch('/api/calculate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(responses)
            });

            const result = await response.json();
            
            if (result.success) {
                // Exibir resultados
                displayResults(result.results);
            } else {
                console.error('Erro ao calcular resultado:', result.error);
            }
        } catch (error) {
            console.error('Erro na requisição:', error);
        }
    }

    // Exibir resultados
    function displayResults(results) {
        const primaryProfile = document.getElementById('primary-profile');
        const profileDetails = document.getElementById('profile-details');

        // Implemente a lógica para exibir os resultados
        primaryProfile.innerHTML = `Seu perfil principal: ${results.profile_summary}`;
        profileDetails.innerHTML = `Detalhes: ${JSON.stringify(results)}`;
    }

    // Botão para nova avaliação
    function startNewAssessment() {
        // Resetar variáveis
        currentQuestionIndex = 0;
        responses = {};

        // Ocultar resultados e mostrar introdução
        resultsSection.style.display = 'none';
        introSection.style.display = 'block';
    }

    // Event Listeners
    startBtn.addEventListener('click', startAssessment);
    nextBtn.addEventListener('click', goToNextQuestion);
    prevBtn.addEventListener('click', goToPreviousQuestion);
    newAssessmentBtn.addEventListener('click', startNewAssessment);
});