// CHANGE: Versão 1.0.9 + Debug Logs - Tela de conclusão com botão "Ver Resultado"
// Variáveis globais
let currentQuestionIndex = 0;
let userResponses = {};
let countdownTimer;
let isTransitioning = false;

// Carregar as perguntas
const questions = typeof discQuestions !== 'undefined' && Array.isArray(discQuestions) && discQuestions.length > 0
    ? discQuestions
    : [ { id: 1, options: [{ id: "A", text: "ERRO" }, { id: "B", text: "QUESTÕES" }, { id: "C", "text": "NÃO" }, { id: "D", text: "CARREGADAS" }] } ];
const totalQuestions = questions.length;

// --- Elementos do DOM ---
const assessmentSection = document.getElementById('assessment');
const resultsSection = document.getElementById('results');
const questionContentWrapper = document.getElementById('question-content-wrapper');
const optionsList = document.getElementById('options-list');
const questionNumberSpan = document.getElementById('question-number');
const totalQuestionsSpan = document.getElementById('total-questions');
const countdownSpan = document.getElementById('countdown');
const quizHeader = document.querySelector('.quiz-header');
const timerContainer = document.querySelector('.moved-timer');
const quizCompletionSection = document.getElementById('quiz-completion');
const viewResultsBtn = document.getElementById('view-results-btn');

// --- Funções do Quiz ---

function startAssessment() {
    console.log("startAssessment chamada"); // Log
    if (!assessmentSection || !resultsSection || !quizCompletionSection ) {
        console.error("Erro: Seções não encontradas."); // Log Erro
        return;
    }
    resultsSection.style.display = 'none';
    quizCompletionSection.style.display = 'none';
    assessmentSection.style.display = 'block';
    if(quizHeader) quizHeader.classList.remove('hidden');
    if(timerContainer) timerContainer.classList.remove('hidden');
    if(questionContentWrapper) {
        questionContentWrapper.style.display = ''; // Ou 'block'
        questionContentWrapper.classList.remove('fading-out');
    }

    currentQuestionIndex = 0;
    userResponses = {};
    isTransitioning = false;
    if (questions.length > 0) {
        if (totalQuestionsSpan) totalQuestionsSpan.textContent = totalQuestions;
        loadQuestion(currentQuestionIndex);
    } else {
        console.error("Nenhuma questão carregada."); // Log Erro
        if(optionsList) optionsList.innerHTML = '<p class="warning">Erro: Nenhuma questão foi carregada.</p>';
    }
}

function loadQuestion(index) {
    console.log(`--- loadQuestion: Iniciando para índice ${index} ---`); // Log Adicionado
     // Reset da flag DEPOIS que a nova questão começar a carregar, exceto na primeira
     if (isTransitioning && index !== 0) {
         isTransitioning = false;
         console.log("loadQuestion: Resetando isTransitioning para FALSE."); // Log Adicionado
     } else if (index === 0) {
        isTransitioning = false; // Garante que na primeira carga não está em transição
        console.log("loadQuestion: Índice 0, garantindo isTransitioning = FALSE."); // Log Adicionado
     }

    if (!optionsList || !questionNumberSpan || !totalQuestionsSpan || !questionContentWrapper || !countdownSpan) {
        console.error("!!! loadQuestion: Elemento(s) do DOM não encontrado(s) !!!"); // Log Erro
        return;
    }

    // Adicionado verificação de índice ANTES de acessar questions[index]
     if (index < 0 || index >= totalQuestions) {
         console.error(`loadQuestion: Índice de questão inválido: ${index}. Total: ${totalQuestions}.`); // Log Erro Adicionado
         // Não avançar para tela final aqui, erro deve ser tratado.
         return;
     }


    const question = questions[index];
    console.log("loadQuestion: Dados da questão:", JSON.stringify(question)); // Log Adicionado

    if (!question || !question.options || !Array.isArray(question.options)) {
         console.error(`!!! loadQuestion: Dados inválidos para a questão ${index} !!!`, question); // Log Erro Adicionado
         optionsList.innerHTML = `<p class="warning">Erro ao carregar dados da questão ${index + 1}.</p>`;
         return;
     }

    currentQuestionIndex = index; // Define o índice atual
    console.log(`loadQuestion: currentQuestionIndex atualizado para ${currentQuestionIndex}`); // Log Adicionado

    console.log("loadQuestion: Limpando optionsList (innerHTML = '')."); // Log Adicionado
    optionsList.innerHTML = '';

    questionNumberSpan.textContent = index + 1;

    console.log("loadQuestion: Iniciando loop para adicionar opções."); // Log Adicionado
    question.options.forEach(option => {
        const optionItem = document.createElement('div');
        optionItem.classList.add('option-item');
        optionItem.innerHTML = `
            <div class="option-text">${option.text}</div>
            <div class="radio-container mais">
                <input type="radio" id="most_${question.id}_${option.id}" name="most_${question.id}" value="${option.id}" class="most-option" data-question-id="${question.id}">
            </div>
            <div class="radio-container menos">
                <input type="radio" id="least_${question.id}_${option.id}" name="least_${question.id}" value="${option.id}" class="least-option" data-question-id="${question.id}">
            </div>
        `;
        optionsList.appendChild(optionItem);
    });
     console.log("loadQuestion: Loop de opções concluído."); // Log Adicionado

    const savedResponse = userResponses[question.id];
    if (savedResponse) {
         console.log("loadQuestion: Restaurando resposta salva para questão:", question.id); // Log Adicionado
        const mostRadio = optionsList.querySelector(`input.most-option[value="${savedResponse.most}"]`);
        const leastRadio = optionsList.querySelector(`input.least-option[value="${savedResponse.least}"]`);
        if (mostRadio) mostRadio.checked = true;
        if (leastRadio) leastRadio.checked = true;
    }

    console.log("loadQuestion: Adicionando listeners de opção."); // Log Adicionado
    addOptionListeners();

    console.log("loadQuestion: Removendo 'fading-out' e forçando reflow para fade-in."); // Log Adicionado
    questionContentWrapper.classList.remove('fading-out');
    void questionContentWrapper.offsetWidth; // Reflow

    console.log("loadQuestion: Chamando startCountdown."); // Log Adicionado
    startCountdown();

    console.log(`--- loadQuestion: Concluído para índice ${index} ---`); // Log Adicionado
}

function addOptionListeners() {
    const radioButtons = optionsList.querySelectorAll('input[type="radio"]');
    radioButtons.forEach(radio => {
        radio.removeEventListener('change', handleSelectionChange);
        radio.addEventListener('change', handleSelectionChange);
    });
    const radioContainers = optionsList.querySelectorAll('.radio-container');
    radioContainers.forEach(container => {
         container.removeEventListener('click', handleContainerClick);
         container.addEventListener('click', handleContainerClick);
    });
}

function handleContainerClick(event) {
    if (event.target.tagName === 'INPUT') return;
    const input = event.currentTarget.querySelector('input[type="radio"]');
    if (input && !input.checked) {
        input.checked = true;
        input.dispatchEvent(new Event('change', { bubbles: true }));
    }
}

function handleSelectionChange(event) {
    if (isTransitioning) return;
    const changedRadio = event.target;
    const questionId = changedRadio.getAttribute('data-question-id');
    const currentValue = changedRadio.value;
    const isMost = changedRadio.name.startsWith('most_');
    if(!optionsList || !questionId) return;

    if (isMost) {
        const conflictingLeast = optionsList.querySelector(`input[name="least_${questionId}"][value="${currentValue}"]:checked`);
        if (conflictingLeast) conflictingLeast.checked = false;
    } else {
        const conflictingMost = optionsList.querySelector(`input[name="most_${questionId}"][value="${currentValue}"]:checked`);
        if (conflictingMost) conflictingMost.checked = false;
    }
    saveCurrentResponse();
    checkAndAdvance();
}

function saveCurrentResponse() {
     if (!questions || currentQuestionIndex < 0 || currentQuestionIndex >= questions.length) {
         console.error("saveCurrentResponse: Índice de questão inválido."); // Log Erro
         return;
     }
    const questionId = questions[currentQuestionIndex].id;
    if(!optionsList) return;
    const mostChecked = optionsList.querySelector(`input[name="most_${questionId}"]:checked`);
    const leastChecked = optionsList.querySelector(`input[name="least_${questionId}"]:checked`);
    if (mostChecked && leastChecked) {
         userResponses[questionId] = { questionId: questionId, most: mostChecked.value, least: leastChecked.value };
         console.log(`saveCurrentResponse: Resposta salva para questão ${questionId}:`, userResponses[questionId]); // Log
    } else {
         delete userResponses[questionId];
         console.log(`saveCurrentResponse: Resposta para questão ${questionId} removida (incompleta).`); // Log
    }
}

function startCountdown() {
    if (!countdownSpan) return;
    let timeLeft = 15;
    countdownSpan.textContent = timeLeft;
    if(timerContainer) timerContainer.style.backgroundColor = '#f0f0f0';

    clearInterval(countdownTimer);
    console.log("startCountdown: Timer iniciado para questão:", currentQuestionIndex + 1); // Log

    countdownTimer = setInterval(() => {
        timeLeft--;
        const currentCountdownSpan = document.getElementById('countdown');
        if (currentCountdownSpan) {
             currentCountdownSpan.textContent = timeLeft;
             if (timeLeft <= 5) {
                 if(timerContainer) timerContainer.style.backgroundColor = '#fdd';
                 currentCountdownSpan.style.color = '#c00';
             } else {
                 if(timerContainer) timerContainer.style.backgroundColor = '#f0f0f0';
                 currentCountdownSpan.style.color = '#c0392b';
             }
        } else {
             clearInterval(countdownTimer); return;
        }

        if (timeLeft <= 0) {
            clearInterval(countdownTimer);
            console.log("startCountdown: Tempo esgotado para questão:", currentQuestionIndex + 1); // Log
            if (currentQuestionIndex >= totalQuestions - 1) {
                 console.log("startCountdown: Tempo esgotado na última questão. Chamando showCompletionScreen()."); // Log
                 showCompletionScreen();
            } else {
                 console.log("startCountdown: Tempo esgotado (não última). Chamando advanceQuestion(true)."); // Log
                 advanceQuestion(true);
            }
        }
    }, 1000);
}

function checkAndAdvance() {
     console.log("checkAndAdvance: Verificando se pode avançar..."); // Log Adicionado
     if (isTransitioning) {
         console.log("checkAndAdvance: Transição em andamento, aguardando."); // Log Adicionado
         return;
     }
     if (!questions || currentQuestionIndex < 0 || currentQuestionIndex >= questions.length) return;
     const questionId = questions[currentQuestionIndex].id;
     const mostChecked = optionsList.querySelector(`input[name="most_${questionId}"]:checked`);
     const leastChecked = optionsList.querySelector(`input[name="least_${questionId}"]:checked`);

     if (mostChecked && leastChecked) {
         console.log(`checkAndAdvance: Resposta completa para questão ${currentQuestionIndex + 1}.`); // Log Adicionado
         if (currentQuestionIndex >= totalQuestions - 1) {
             console.log("checkAndAdvance: É a última questão. Chamando showCompletionScreen()."); // Log Adicionado
             showCompletionScreen();
         } else {
             console.log("checkAndAdvance: Não é a última questão. Chamando advanceQuestion(false)."); // Log Adicionado
             advanceQuestion(false);
         }
     } else {
         console.log("checkAndAdvance: Resposta ainda incompleta."); // Log Adicionado
     }
}

function advanceQuestion(forceNext = false) {
    console.log(`advanceQuestion: Iniciando. forceNext=${forceNext}, isTransitioning=${isTransitioning}`); // Log Adicionado
    if (isTransitioning) {
        console.log("advanceQuestion: Já em transição, retornando."); // Log Adicionado
        return;
    }
    saveCurrentResponse();

    clearInterval(countdownTimer);
    isTransitioning = true;
    console.log("advanceQuestion: isTransitioning definida como TRUE. Iniciando fade-out..."); // Log Adicionado
    questionContentWrapper.classList.add('fading-out');

    const transitionDuration = 400;
    console.log(`advanceQuestion: Agendando próxima ação em ${transitionDuration}ms.`); // Log Adicionado

    setTimeout(() => {
        console.log("advanceQuestion: Dentro do setTimeout (após fade-out)."); // Log Adicionado
        const nextIndex = currentQuestionIndex + 1;
        console.log(`advanceQuestion: Tentando carregar próxima questão, índice: ${nextIndex}`); // Log Adicionado
        loadQuestion(nextIndex);

        // Flag isTransitioning é resetada dentro de loadQuestion agora
    }, transitionDuration);
}

function showCompletionScreen() {
    console.log("showCompletionScreen: Mostrando tela de conclusão..."); // Log
    if (isTransitioning) {
        console.log("showCompletionScreen: Já em transição, retornando."); // Log
        return;
    }
    isTransitioning = true;
    console.log("showCompletionScreen: isTransitioning definida como TRUE."); // Log

    saveCurrentResponse();
    clearInterval(countdownTimer);
    console.log("showCompletionScreen: Timer parado."); // Log

    if(quizHeader) quizHeader.classList.add('hidden');
    if(timerContainer) timerContainer.classList.add('hidden');
    if(questionContentWrapper) questionContentWrapper.classList.add('fading-out');
    console.log("showCompletionScreen: Elementos do quiz escondidos/fading out."); // Log

    const fadeOutDuration = 400;
    setTimeout(() => {
        console.log("showCompletionScreen: Dentro do setTimeout (após fade-out)."); // Log
        if(questionContentWrapper) questionContentWrapper.style.display = 'none';
        if(quizCompletionSection) quizCompletionSection.style.display = 'block';
        console.log("showCompletionScreen: Seção de conclusão exibida."); // Log

        if (viewResultsBtn) {
            viewResultsBtn.disabled = false; // Garante que está habilitado
            viewResultsBtn.removeEventListener('click', handleViewResultsClick);
            viewResultsBtn.addEventListener('click', handleViewResultsClick);
            console.log("showCompletionScreen: Listener adicionado ao botão 'Ver Resultado'."); // Log
        } else {
            console.error("showCompletionScreen: Botão 'Ver Resultado' não encontrado!"); // Log Erro
        }
         isTransitioning = false;
         console.log("showCompletionScreen: isTransitioning definida como FALSE."); // Log
         console.log("Tela de conclusão exibida."); // Log (Duplicado, mas ok)
    }, fadeOutDuration);
}

function handleViewResultsClick() {
    console.log("handleViewResultsClick: Botão 'Ver Resultado' clicado."); // Log
    if(viewResultsBtn) {
        viewResultsBtn.disabled = true;
        console.log("handleViewResultsClick: Botão desabilitado."); // Log
    }
    finishAssessment();
}

function finishAssessment() {
     console.log("finishAssessment: Iniciando envio de dados."); // Log

     const answersArray = Object.values(userResponses);

     let overlay = document.getElementById('loading-overlay');
     if (!overlay) {
          document.body.insertAdjacentHTML('beforeend', '<div id="loading-overlay" style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(255,255,255,0.8); z-index: 9999; display: flex; justify-content: center; align-items: center;"><p style="font-size: 1.5em; padding: 20px; background: #fff; border-radius: 5px; box-shadow: 0 0 10px rgba(0,0,0,0.2);">Calculando seus resultados...</p></div>');
          console.log("finishAssessment: Overlay criado."); // Log
     } else {
         overlay.style.display = 'flex';
         console.log("finishAssessment: Overlay reutilizado."); // Log
     }

     if (answersArray.length < totalQuestions) {
          console.warn(`finishAssessment: Avaliação finalizada com ${answersArray.length} de ${totalQuestions} respostas.`); // Log Aviso
     }
     console.log("finishAssessment: Enviando respostas para cálculo:", answersArray); // Log

     if (answersArray.length > 0) {
         sendAnswersAndRedirect(answersArray);
     } else {
         console.warn("finishAssessment: Nenhuma resposta para enviar."); // Log Aviso
         const currentOverlay = document.getElementById('loading-overlay');
         if (currentOverlay) currentOverlay.remove();
         alert("Nenhuma resposta foi registrada. Por favor, tente novamente.");
         if(viewResultsBtn) viewResultsBtn.disabled = false; // Reabilita
     }
}

async function sendAnswersAndRedirect(answers) {
    const overlay = document.getElementById('loading-overlay');
    console.log("sendAnswersAndRedirect: Tentando POST para /api/calculate"); // Log
    try {
        const response = await fetch('/api/calculate', { // Garanta que a rota está correta!
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ answers: answers })
        });
        console.log(`sendAnswersAndRedirect: Resposta recebida, status: ${response.status}`); // Log
        if (!response.ok) {
            let errorBody = await response.text();
            console.error(`sendAnswersAndRedirect: Erro ${response.status}. Corpo: ${errorBody}`); // Log Erro
            throw new Error(`Erro do Servidor: ${response.status} ${response.statusText}. Detalhes: ${errorBody}`);
        }
        const result = await response.json();
        console.log("sendAnswersAndRedirect: Resposta JSON:", result); // Log
        if (result.success) {
            console.log("sendAnswersAndRedirect: Sucesso no backend. Redirecionando para /results..."); // Log
            window.location.href = '/results';
        } else {
             console.error("sendAnswersAndRedirect: Backend retornou sucesso=false ou erro:", result.error); // Log Erro
            throw new Error(result.error || 'Ocorreu um erro no cálculo (resposta não indicou sucesso).');
        }
    } catch (error) {
        console.error('sendAnswersAndRedirect: Erro no fetch ou processamento:', error); // Log Erro
        if (overlay) overlay.remove();
        alert(`Houve um problema ao processar seus resultados:\n\n${error.message}\n\nPor favor, tente novamente.`);
        if(viewResultsBtn) viewResultsBtn.disabled = false; // Reabilita
    }
}

// --- Event Listeners Iniciais ---
document.addEventListener('DOMContentLoaded', () => {
    console.log("DOMContentLoaded: Evento disparado - v1.0.9 + Debug Logs"); // Log

    const newAssessmentBtn = document.getElementById('new-assessment');

    if (assessmentSection) {
        console.log("DOMContentLoaded: Seção de avaliação encontrada. Chamando startAssessment()..."); // Log
        startAssessment();
    } else if (document.getElementById('results')) {
         console.log("DOMContentLoaded: Página de resultados carregada."); // Log
    } else {
         console.warn("DOMContentLoaded: Nenhuma seção de quiz ou resultados principal detectada."); // Log Aviso
    }

    if (newAssessmentBtn) {
         newAssessmentBtn.addEventListener('click', () => {
             console.log("Botão Nova Avaliação clicado."); // Log
             window.location.href = '/quiz';
         });
    }

    console.log("DOMContentLoaded: Setup inicial concluído."); // Log
});