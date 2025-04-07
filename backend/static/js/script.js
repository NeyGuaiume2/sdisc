// backend/static/js/script.js
// Versão 1.1.3 - Coleta nome/email e envia para API

// --- Variáveis Globais e Elementos DOM (como antes) ---
let currentQuestionIndex = 0;
let userResponses = {};
let countdownTimer;
let isTransitioning = false;
let questions = [];
let totalQuestions = 0;
const assessmentSection = document.getElementById('assessment');
const resultsSection = document.getElementById('results');
const questionContentWrapper = document.getElementById('question-content-wrapper');
const optionsList = document.getElementById('options-list');
const countdownSpan = document.getElementById('countdown');
const timerContainer = document.querySelector('.moved-timer');
const quizCompletionSection = document.getElementById('quiz-completion');
const viewResultsBtn = document.getElementById('view-results-btn');
const loadingIndicator = document.getElementById('loading-indicator');
const progressBar = document.getElementById('quiz-progress-bar');
const progressText = document.getElementById('progress-text');
const instructionsDiv = document.querySelector('.instructions');
const instructionsFooterDiv = document.querySelector('.instructions-footer');
// NOVOS Elementos para Nome/Email
const userNameInput = document.getElementById('user-name');
const userEmailInput = document.getElementById('user-email');


// --- Funções fetchQuestions, startAssessment, loadQuestion, addOptionListeners, ---
// --- handleContainerClick, handleSelectionChange, saveCurrentResponse, startCountdown, ---
// --- checkAndAdvance, advanceQuestion (permanecem iguais à resposta anterior) ---

async function fetchQuestions() { console.log("fetchQuestions: Buscando questões..."); if(loadingIndicator) loadingIndicator.style.display = 'block'; try { const response = await fetch('/api/questions'); if (!response.ok) throw new Error(`Erro HTTP ${response.status}`); questions = await response.json(); totalQuestions = questions.length; console.log(`fetchQuestions: ${totalQuestions} questões carregadas.`); if (totalQuestions > 0) { if(progressText) progressText.textContent = `Questão 1 / ${totalQuestions}`; return true; } else { console.error("fetchQuestions: Nenhuma questão recebida."); if(optionsList) optionsList.innerHTML = '<p class="warning">Erro: Nenhuma questão carregada.</p>'; const progressContainer = document.querySelector('.progress-container'); if(progressContainer) progressContainer.style.display = 'none'; return false; } } catch (error) { console.error("fetchQuestions: Falha:", error); if(optionsList) optionsList.innerHTML = `<p class="warning">Erro ao carregar: ${error.message}.</p>`; const progressContainer = document.querySelector('.progress-container'); if(progressContainer) progressContainer.style.display = 'none'; return false; } finally { if(loadingIndicator) loadingIndicator.style.display = 'none'; } }
function startAssessment() { console.log("startAssessment: Iniciando..."); if (!assessmentSection || !quizCompletionSection ) { console.error("Erro Crítico: Seções assessment/quizCompletion não encontradas."); return; } if(resultsSection) resultsSection.style.display = 'none'; quizCompletionSection.classList.remove('visible'); quizCompletionSection.style.display = 'none'; assessmentSection.style.display = 'block'; if(instructionsDiv) instructionsDiv.style.display = 'block'; if(instructionsFooterDiv) instructionsFooterDiv.style.display = 'block'; const progressContainer = document.querySelector('.progress-container'); if(progressContainer) progressContainer.style.display = 'block'; if(timerContainer) timerContainer.classList.remove('hidden'); if(questionContentWrapper) { questionContentWrapper.style.display = ''; questionContentWrapper.classList.remove('fading-out', 'hidden'); } currentQuestionIndex = 0; userResponses = {}; isTransitioning = false; if (questions.length > 0) { console.log("startAssessment: Iniciando com a primeira questão."); loadQuestion(currentQuestionIndex); } else { console.error("startAssessment: NENHUMA questão carregada."); if(optionsList) optionsList.innerHTML = '<p class="warning">Erro: Questões não carregadas.</p>'; if(progressContainer) progressContainer.style.display = 'none'; } }
function loadQuestion(index) { console.log(`--- loadQuestion: Índice ${index} ---`); if (isTransitioning) { isTransitioning = false; } if (!optionsList || !questionContentWrapper || !countdownSpan || !progressBar || !progressText) { console.error("!!! loadQuestion: Elemento(s) DOM essenciais não encontrado(s) !!!"); return; } if (index < 0 || index >= totalQuestions) { console.error(`loadQuestion: Índice inválido: ${index}.`); return; } const question = questions[index]; if (!question || typeof question !== 'object' || !question.id || !question.D || !question.I || !question.S || !question.C) { console.error(`!!! loadQuestion: Dados inválidos q ${index} !!!`, question); optionsList.innerHTML = `<p class="warning">Erro dados questão ${index + 1}.</p>`; clearInterval(countdownTimer); return; } currentQuestionIndex = index; const progressPercentage = totalQuestions > 0 ? ((index + 1) / totalQuestions) * 100 : 0; progressBar.style.width = `${progressPercentage}%`; progressBar.setAttribute('aria-valuenow', progressPercentage); progressText.textContent = `Questão ${index + 1} / ${totalQuestions}`; optionsList.innerHTML = ''; const profiles = ['D', 'I', 'S', 'C']; profiles.forEach(profileKey => { const word = question[profileKey]; const optionItem = document.createElement('div'); optionItem.classList.add('option-item'); optionItem.innerHTML = ` <div class="option-text">${word}</div> <div class="radio-container mais"> <input type="radio" id="most_${question.id}_${profileKey}" name="most_${question.id}" value="${word}" class="most-option" data-question-id="${question.id}"> </div> <div class="radio-container menos"> <input type="radio" id="least_${question.id}_${profileKey}" name="least_${question.id}" value="${word}" class="least-option" data-question-id="${question.id}"> </div>`; optionsList.appendChild(optionItem); }); const savedResponse = userResponses[question.id]; if (savedResponse) { const mostRadio = optionsList.querySelector(`.most-option[value="${CSS.escape(savedResponse.mais)}"]`); const leastRadio = optionsList.querySelector(`.least-option[value="${CSS.escape(savedResponse.menos)}"]`); if (mostRadio) mostRadio.checked = true; if (leastRadio) leastRadio.checked = true; } addOptionListeners(); questionContentWrapper.classList.remove('fading-out'); void questionContentWrapper.offsetWidth; startCountdown(); console.log(`--- loadQuestion: Concluído ${index} ---`); }
function addOptionListeners() { optionsList.querySelectorAll('input[type="radio"]').forEach(radio => { radio.removeEventListener('change', handleSelectionChange); radio.addEventListener('change', handleSelectionChange); }); optionsList.querySelectorAll('.radio-container').forEach(container => { container.removeEventListener('click', handleContainerClick); container.addEventListener('click', handleContainerClick); }); }
function handleContainerClick(event) { if (event.target.tagName === 'INPUT') return; const input = event.currentTarget.querySelector('input[type="radio"]'); if (input && !input.checked) { input.checked = true; input.dispatchEvent(new Event('change', { bubbles: true })); } }
function handleSelectionChange(event) { if (isTransitioning) return; const changedRadio = event.target; const questionId = changedRadio.getAttribute('data-question-id'); const selectedWord = changedRadio.value; const isMost = changedRadio.classList.contains('most-option'); if (!optionsList || !questionId) return; console.log(`handleSelectionChange: Q${questionId}, Palavra: "${selectedWord}", Tipo: ${isMost ? 'MAIS' : 'MENOS'}`); const otherTypeClass = isMost ? '.least-option' : '.most-option'; const conflictingRadio = optionsList.querySelector(`${otherTypeClass}[value="${CSS.escape(selectedWord)}"]`); if (conflictingRadio && conflictingRadio.checked) { conflictingRadio.checked = false; } saveCurrentResponse(); checkAndAdvance(); }
function saveCurrentResponse() { if (!questions || currentQuestionIndex < 0 || currentQuestionIndex >= questions.length) return; const questionId = questions[currentQuestionIndex].id; if(!optionsList) return; const mostChecked = optionsList.querySelector(`input.most-option[name="most_${questionId}"]:checked`); const leastChecked = optionsList.querySelector(`input.least-option[name="least_${questionId}"]:checked`); if (mostChecked && leastChecked) { userResponses[questionId] = { questionId: questionId, mais: mostChecked.value, menos: leastChecked.value }; console.log(`saveCurrentResponse: COMPLETA salva Q${questionId}`); } else { if (userResponses[questionId]) { delete userResponses[questionId]; console.log(`saveCurrentResponse: INCOMPLETA removida Q${questionId}.`); } } }
function startCountdown() { if (!countdownSpan || !timerContainer) return; let timeLeft = 15; countdownSpan.textContent = timeLeft; countdownSpan.style.color = ''; timerContainer.style.backgroundColor = ''; clearInterval(countdownTimer); console.log("startCountdown: Timer Q:", currentQuestionIndex + 1); countdownTimer = setInterval(() => { timeLeft--; const currentCountdownSpan = document.getElementById('countdown'); if (currentCountdownSpan) { currentCountdownSpan.textContent = timeLeft; if (timeLeft <= 5 && timeLeft > 0) { timerContainer.style.backgroundColor = '#ffe0e0'; currentCountdownSpan.style.color = '#d9534f'; } else if (timeLeft <=0 ) { timerContainer.style.backgroundColor = '#f8d7da'; currentCountdownSpan.style.color = '#721c24'; } else { timerContainer.style.backgroundColor = ''; currentCountdownSpan.style.color = ''; } } else { clearInterval(countdownTimer); return; } if (timeLeft <= 0) { clearInterval(countdownTimer); console.log("startCountdown: Tempo esgotado Q:", currentQuestionIndex + 1); if (currentQuestionIndex >= totalQuestions - 1) { showCompletionScreen(); } else { advanceQuestion(true); } } }, 1000); }
function checkAndAdvance() { console.log("checkAndAdvance: Verificando..."); if (isTransitioning) return; if (!questions || currentQuestionIndex < 0 || currentQuestionIndex >= questions.length) return; const questionId = questions[currentQuestionIndex].id; if (userResponses.hasOwnProperty(questionId)) { console.log(`checkAndAdvance: Completa Q${currentQuestionIndex + 1}.`); if (currentQuestionIndex >= totalQuestions - 1) { showCompletionScreen(); } else { advanceQuestion(false); } } }
function advanceQuestion(forceNext = false) { console.log(`advanceQuestion: force=${forceNext}, isTransitioning=${isTransitioning}`); if (isTransitioning) return; saveCurrentResponse(); clearInterval(countdownTimer); isTransitioning = true; questionContentWrapper.classList.add('fading-out'); const transitionDuration = 400; setTimeout(() => { const nextIndex = currentQuestionIndex + 1; if (nextIndex < totalQuestions) { loadQuestion(nextIndex); } else { showCompletionScreen(); } }, transitionDuration); }

function showCompletionScreen() {
    console.log("showCompletionScreen: Preparando...");
    const isWrapperVisible = questionContentWrapper && questionContentWrapper.style.display !== 'none' && !questionContentWrapper.classList.contains('fading-out');
    if (isTransitioning && !isWrapperVisible) return;
    isTransitioning = true;

    saveCurrentResponse();
    clearInterval(countdownTimer);

    // Esconde elementos do quiz
    const progressContainer = document.querySelector('.progress-container');
    if(progressContainer) progressContainer.style.display = 'none';
    if(timerContainer) timerContainer.classList.add('hidden');
    if(instructionsDiv) instructionsDiv.style.display = 'none';
    if(instructionsFooterDiv) instructionsFooterDiv.style.display = 'none';

    if(isWrapperVisible) {
        questionContentWrapper.classList.add('fading-out');
    }

    const fadeOutDuration = isWrapperVisible ? 400 : 0;
    setTimeout(() => {
        if(questionContentWrapper) questionContentWrapper.style.display = 'none';

        if(quizCompletionSection) {
            const completionParagraph = quizCompletionSection.querySelector('p.completion-message');
            if (completionParagraph) {
                const finalAnswerCount = Object.keys(userResponses).length;
                if (finalAnswerCount < totalQuestions) {
                     completionParagraph.innerHTML = `<strong>Atenção:</strong> Foram respondidas ${finalAnswerCount} de ${totalQuestions} questões.<br>Preencha seus dados (opcional) e clique abaixo para ver seu perfil com base nas respostas fornecidas.`; // Ajuste texto
                     completionParagraph.classList.add('text-warning');
                } else {
                     completionParagraph.textContent = "Suas respostas foram registradas com sucesso. Preencha seus dados (opcional) e clique abaixo para ver o seu perfil comportamental."; // Ajuste texto
                     completionParagraph.classList.remove('text-warning');
                }
            }
            quizCompletionSection.style.display = 'block';
            quizCompletionSection.classList.add('visible');
        }

        if (viewResultsBtn) {
            viewResultsBtn.disabled = false;
            viewResultsBtn.textContent = "Ver Meus Resultados"; // Garante texto correto
            viewResultsBtn.removeEventListener('click', handleViewResultsClick);
            viewResultsBtn.addEventListener('click', handleViewResultsClick);
        } else {
            console.error("showCompletionScreen: Botão 'Ver Resultado' não encontrado!");
        }
         isTransitioning = false;
    }, fadeOutDuration);
}

// ATUALIZADO para pegar nome/email
function handleViewResultsClick() {
    console.log("handleViewResultsClick: Botão clicado.");

    // Coleta nome e email
    const userName = userNameInput ? userNameInput.value.trim() : '';
    const userEmail = userEmailInput ? userEmailInput.value.trim() : '';
    console.log(`handleViewResultsClick: Nome: "${userName}", Email: "${userEmail}"`);

    // Validação simples de email (opcional, mas recomendada)
    if (userEmail && !validateEmail(userEmail)) {
         alert("Por favor, insira um endereço de email válido ou deixe o campo em branco.");
         return; // Impede o envio se o email for inválido
    }

    if(viewResultsBtn) {
        viewResultsBtn.disabled = true; viewResultsBtn.textContent = "Processando...";
    }
    // Passa nome e email para finishAssessment
    finishAssessment(userName, userEmail);
}

// Função simples de validação de email
function validateEmail(email) {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(String(email).toLowerCase());
}


// ATUALIZADO para aceitar nome/email
function finishAssessment(userName, userEmail) {
     console.log("finishAssessment: Finalizando e enviando.");
     const answersArray = Object.values(userResponses);

     let overlay = document.getElementById('loading-overlay');
     // Cria overlay (código anterior omitido por brevidade, mas deve existir)
     if (!overlay && document.body) { document.body.insertAdjacentHTML('beforeend', `<div id="loading-overlay">...</div>`); overlay = document.getElementById('loading-overlay'); }
     if (overlay) overlay.style.display = 'flex';

     console.log("finishAssessment: Enviando respostas e userInfo:", JSON.stringify({ answers: answersArray, userInfo: { name: userName, email: userEmail }}));

     if (answersArray.length > 0) {
         // Passa userName e userEmail para a função de envio
         sendAnswersAndRedirect(answersArray, { name: userName, email: userEmail });
     } else {
         console.warn("finishAssessment: Nenhuma resposta para enviar.");
         if (overlay) overlay.style.display = 'none';
         alert("Nenhuma resposta foi registrada.");
         if(viewResultsBtn) { viewResultsBtn.disabled = false; viewResultsBtn.textContent = "Ver Meus Resultados"; }
     }
}

// ATUALIZADO para enviar userInfo
async function sendAnswersAndRedirect(answers, userInfo) {
    const overlay = document.getElementById('loading-overlay');
    console.log("sendAnswersAndRedirect: Tentando POST com userInfo:", userInfo);
    try {
        const response = await fetch('/api/calculate', {
            method: 'POST', headers: {'Content-Type': 'application/json'},
            // Envia a estrutura completa { answers: [], userInfo: {} }
            body: JSON.stringify({ answers: answers, userInfo: userInfo })
        });
        if (!response.ok) {
            let errorBody = "Erro"; try { errorBody = await response.text(); } catch (e) {}
            throw new Error(`Erro Servidor: ${response.status}. ${errorBody.substring(0, 150)}`);
        }
        const result = await response.json();
        if (result.success) { window.location.href = '/results'; }
        else { throw new Error(result.error || 'Erro no processamento.'); }
    } catch (error) {
        console.error('sendAnswersAndRedirect: Falha:', error);
        if (overlay) overlay.style.display = 'none';
        alert(`Problema ao enviar/processar:\n${error.message}\nTente novamente.`);
        if(viewResultsBtn) { viewResultsBtn.disabled = false; viewResultsBtn.textContent = "Ver Meus Resultados"; }
    }
}

// --- Event Listener Inicial ---
document.addEventListener('DOMContentLoaded', async () => {
    console.log("DOMContentLoaded: v1.1.3"); // Atualiza versão log
    const questionsLoaded = await fetchQuestions();
    if (questionsLoaded && document.getElementById('assessment')) {
        startAssessment();
    } else if (!questionsLoaded) {
        console.error("DOMContentLoaded: Falha ao carregar questões.");
    }
    // Listener do botão refazer (como antes)
    const newAssessmentBtn = document.getElementById('new-assessment');
    if (newAssessmentBtn) {
         newAssessmentBtn.addEventListener('click', (e) => {
             e.preventDefault(); window.location.href = e.target.href || '/quiz';
         });
    }
    console.log("DOMContentLoaded: Setup concluído.");
});