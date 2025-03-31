// Variáveis globais para controle do quiz
let currentQuestionIndex = 0;
let userResponses = {};
let countdownTimer;

// Carregar as perguntas (Mantido - Certifique-se que disc_questions.js é carregado ANTES no HTML)
const questions = typeof discQuestions !== 'undefined' && Array.isArray(discQuestions) && discQuestions.length > 0
    ? discQuestions
    : [ { id: 1, options: [{ id: "A", text: "ERRO" }, { id: "B", text: "QUESTÕES" }, { id: "C", "text": "NÃO" }, { id: "D", text: "CARREGADAS" }] } ];
const totalQuestions = questions.length;

// --- Funções do Quiz (RESTAURADAS/DEFINIDAS AQUI) ---

function startAssessment(introSection, assessmentSection, resultsSection) {
    console.log("startAssessment chamada");
    if (!introSection || !assessmentSection || !resultsSection) {
        console.error("Erro: Seções não encontradas em startAssessment.");
        return;
    }
    introSection.style.display = 'none';
    resultsSection.style.display = 'none';
    assessmentSection.style.display = 'block';
    currentQuestionIndex = 0;
    userResponses = {};
    if (questions.length > 0) {
        loadQuestion(currentQuestionIndex); // Chama a função que agora está definida
    } else {
        console.error("Nenhuma questão carregada para iniciar a avaliação.");
        const optionsList = document.getElementById('options-list');
        if(optionsList) optionsList.innerHTML = '<p class="warning">Erro: Nenhuma questão foi carregada.</p>';
    }
}

function loadQuestion(index) {
    console.log(`--- Entrando em loadQuestion(${index}) ---`);
    const optionsList = document.getElementById('options-list');
    const questionNumberSpan = document.getElementById('question-number');
    const totalQuestionsSpan = document.getElementById('total-questions');
    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn');

    if (!optionsList || !questionNumberSpan || !totalQuestionsSpan || !prevBtn || !nextBtn) {
        console.error("!!! Elemento(s) do DOM não encontrado(s) em loadQuestion: options-list, question-number, total-questions, prev-btn, next-btn !!!");
        return;
    }
    console.log("Elementos do DOM encontrados.");

    if (index < 0 || index >= totalQuestions) {
        console.error(`Índice de questão inválido: ${index}. Total de questões: ${totalQuestions}`);
         if (index >= totalQuestions && totalQuestions > 0) {
             console.log("Tentativa de carregar questão após a última. Finalizando.");
             finishAssessment();
         }
        return;
    }

    const question = questions[index];
    console.log("Dados da questão:", JSON.stringify(question));

    if (!question || !question.options || !Array.isArray(question.options)) {
         console.error(`!!! Dados inválidos para a questão ${index} !!!`, question);
         optionsList.innerHTML = `<p class="warning">Erro ao carregar dados da questão ${index + 1}.</p>`;
         prevBtn.disabled = true;
         nextBtn.disabled = true;
         return;
     }

    currentQuestionIndex = index; // Define o índice atual
    optionsList.innerHTML = ''; // Limpa opções anteriores

    questionNumberSpan.textContent = index + 1;
    totalQuestionsSpan.textContent = totalQuestions;

    console.log("Iniciando loop de opções...");
    question.options.forEach(option => {
         // console.log("Processando opção:", JSON.stringify(option)); // Log detalhado opcional
        const optionItem = document.createElement('div');
        optionItem.classList.add('option-item'); // Garante que a classe para estilo é adicionada

        // Cria a estrutura HTML para cada opção
        optionItem.innerHTML = `
            <div class="option-text">${option.text}</div>
            <div class="radio-container mais">
                <input type="radio" id="most_${question.id}_${option.id}" name="most_${question.id}" value="${option.id}" class="most-option" data-question-id="${question.id}">
                <label for="most_${question.id}_${option.id}" class="radio-label"></label> 
            </div>
            <div class="radio-container menos">
                <input type="radio" id="least_${question.id}_${option.id}" name="least_${question.id}" value="${option.id}" class="least-option" data-question-id="${question.id}">
                <label for="least_${question.id}_${option.id}" class="radio-label"></label>
            </div>
        `;
        optionsList.appendChild(optionItem);
    });
    console.log("Loop de opções concluído.");

    // Restaurar resposta salva, se houver
    const savedResponse = userResponses[question.id];
    if (savedResponse) {
        const mostRadio = optionsList.querySelector(`input.most-option[value="${savedResponse.most}"]`);
        const leastRadio = optionsList.querySelector(`input.least-option[value="${savedResponse.least}"]`);
        if (mostRadio) mostRadio.checked = true;
        if (leastRadio) leastRadio.checked = true;
    }

    // Habilitar/desabilitar botões de navegação
    prevBtn.disabled = (index === 0);
    checkNextButtonState(); // Verifica estado do botão Próximo
    addOptionListeners(); // Adiciona listeners aos novos radio buttons

    console.log("Chamando startCountdown...");
    startCountdown(); // Inicia o contador para esta questão
}

function addOptionListeners() {
    const optionsList = document.getElementById('options-list');
    if (!optionsList) return;
    // Garante que listeners antigos sejam removidos antes de adicionar novos (embora limpar o innerHTML já faça isso)
    const radioButtons = optionsList.querySelectorAll('input[type="radio"]');
    radioButtons.forEach(radio => {
        radio.removeEventListener('change', handleSelectionChange); // Previne duplicatas se chamado mais vezes
        radio.addEventListener('change', handleSelectionChange);
    });
}

function handleSelectionChange(event) {
    const changedRadio = event.target;
    const questionId = changedRadio.getAttribute('data-question-id');
    const currentValue = changedRadio.value;
    const isMost = changedRadio.name.startsWith('most_');
    const optionsList = document.getElementById('options-list');

    if(!optionsList || !questionId) {
        console.error("Erro em handleSelectionChange: optionsList ou questionId faltando.");
        return;
    }

    // Desmarcar a opção conflitante (mesma palavra não pode ser MAIS e MENOS)
    if (isMost) {
        const conflictingLeast = optionsList.querySelector(`input[name="least_${questionId}"][value="${currentValue}"]:checked`);
        if (conflictingLeast) conflictingLeast.checked = false;
    } else { // isLeast
        const conflictingMost = optionsList.querySelector(`input[name="most_${questionId}"][value="${currentValue}"]:checked`);
        if (conflictingMost) conflictingMost.checked = false;
    }
    
    saveCurrentResponse(); // Salva a resposta atual (ou remove se incompleta)
    checkNextButtonState(); // Verifica se o botão Próximo deve ser habilitado
}

function saveCurrentResponse() {
     // Garante que o índice é válido
     if (!questions || currentQuestionIndex < 0 || currentQuestionIndex >= questions.length) {
         console.error("saveCurrentResponse: Índice de questão inválido.");
         return;
     }

    const questionId = questions[currentQuestionIndex].id;
    const optionsList = document.getElementById('options-list');
    if(!optionsList) return;

    const mostChecked = optionsList.querySelector(`input[name="most_${questionId}"]:checked`);
    const leastChecked = optionsList.querySelector(`input[name="least_${questionId}"]:checked`);

    // Só salva se AMBOS estiverem marcados e forem diferentes (já garantido por handleSelectionChange)
    if (mostChecked && leastChecked) {
         userResponses[questionId] = {
             questionId: questionId, // Inclui ID para facilitar no backend se necessário
             most: mostChecked.value,
             least: leastChecked.value
         };
         console.log(`Resposta salva para questão ${questionId}:`, userResponses[questionId]);
    } else {
         // Se a resposta ficar incompleta (ex: desmarcou um), remove do objeto
         delete userResponses[questionId];
         console.log(`Resposta para questão ${questionId} removida (incompleta).`);
    }
     // console.log("Respostas atuais:", userResponses); // Log opcional
}

function checkNextButtonState() {
    const nextBtn = document.getElementById('next-btn');
    const optionsList = document.getElementById('options-list');
     // Garante que o índice e elementos são válidos
     if (!nextBtn || !optionsList || !questions || currentQuestionIndex < 0 || currentQuestionIndex >= questions.length) {
         if(nextBtn) nextBtn.disabled = true; 
         return;
     }

     const questionId = questions[currentQuestionIndex].id;
     const mostChecked = optionsList.querySelector(`input[name="most_${questionId}"]:checked`);
     const leastChecked = optionsList.querySelector(`input[name="least_${questionId}"]:checked`);

    // Habilita o botão Próximo SOMENTE se ambos 'most' e 'least' estiverem selecionados
    nextBtn.disabled = !(mostChecked && leastChecked);
}

function startCountdown() {
    const countdownSpan = document.getElementById('countdown');
    if (!countdownSpan) {
        console.error("Elemento countdown não encontrado.");
        return;
    }

    let timeLeft = 15; // Reinicia o tempo
    countdownSpan.textContent = timeLeft;
    countdownSpan.style.color = ''; // Reseta cor

    clearInterval(countdownTimer); // Limpa timer anterior SEMPRE
    console.log("Timer iniciado.");

    countdownTimer = setInterval(() => {
        timeLeft--;
        // Busca o elemento novamente, pode ter sido recriado (embora improvável aqui)
        const currentCountdownSpan = document.getElementById('countdown');
        if (currentCountdownSpan) {
             currentCountdownSpan.textContent = timeLeft;
             // Mudar cor perto do fim (opcional)
             if (timeLeft <= 5) currentCountdownSpan.style.color = 'red';
        } else {
             console.warn("Elemento countdown desapareceu, parando timer.");
             clearInterval(countdownTimer);
             return;
        }

        if (timeLeft <= 0) {
            clearInterval(countdownTimer);
            console.log("Tempo esgotado para questão:", currentQuestionIndex + 1);
            goToNextQuestion(true); // Força ir para a próxima questão
        }
    }, 1000);
}

function goToNextQuestion(forceNext = false) {
    console.log(`goToNextQuestion chamada. forceNext: ${forceNext}`); 
    saveCurrentResponse(); // Tenta salvar a resposta atual primeiro

     // Garante índice válido
     if (!questions || currentQuestionIndex < 0 || currentQuestionIndex >= questions.length) {
        console.error("Estado inválido em goToNextQuestion.");
        return;
     }

    const currentQuestionId = questions[currentQuestionIndex].id;

    // Só impede de avançar se NÃO for forçado (timer) E a resposta estiver incompleta
    if (!forceNext && !userResponses[currentQuestionId]) {
         console.warn("Tentativa de avançar sem resposta completa (não forçado).");
         // Feedback visual rápido
          const nextBtn = document.getElementById('next-btn');
          if (nextBtn) {
              nextBtn.classList.add('btn-flash-error'); 
              setTimeout(() => nextBtn.classList.remove('btn-flash-error'), 500);
          }
         return; 
    }

    clearInterval(countdownTimer); // Limpa timer atual ANTES de ir para a próxima

    if (currentQuestionIndex < totalQuestions - 1) {
        loadQuestion(currentQuestionIndex + 1); // Carrega a próxima (que reiniciará o timer)
    } else {
        console.log("Última questão respondida/tempo esgotado. Finalizando assessment.");
        finishAssessment(); // Chama a função de finalização
    }
}

function goToPreviousQuestion() {
     console.log("goToPreviousQuestion chamada"); 
    if (currentQuestionIndex > 0) {
        saveCurrentResponse(); // Salva antes de voltar (pode não ser necessário, mas seguro)
        clearInterval(countdownTimer); // Limpa timer atual
        loadQuestion(currentQuestionIndex - 1); // Carrega a anterior (que reiniciará o timer)
    }
}


// --- FUNÇÕES DE FINALIZAÇÃO E ENVIO (Mantidas como corrigidas anteriormente) ---

function finishAssessment() {
     console.log("finishAssessment chamada - Versão com Redirecionamento"); // Log
    const assessmentSection = document.getElementById('assessment');
     if (!assessmentSection) {
         console.error("Seção de avaliação não encontrada para finalizar.");
         return;
     }
    assessmentSection.style.display = 'none'; 
    clearInterval(countdownTimer); 
    const answersArray = Object.values(userResponses);
    document.body.insertAdjacentHTML('beforeend', '<div id="loading-overlay" style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(255,255,255,0.8); z-index: 9999; display: flex; justify-content: center; align-items: center;"><p style="font-size: 1.5em; padding: 20px; background: #fff; border-radius: 5px; box-shadow: 0 0 10px rgba(0,0,0,0.2);">Calculando seus resultados...</p></div>');
    if (answersArray.length < totalQuestions) {
         console.warn(`Avaliação finalizada com ${answersArray.length} de ${totalQuestions} respostas.`);
    }
    console.log("Enviando respostas para cálculo:", answersArray);
    if (answersArray.length > 0) {
        sendAnswersAndRedirect(answersArray); 
    } else {
        console.warn("Nenhuma resposta para enviar.");
        const overlay = document.getElementById('loading-overlay');
        if (overlay) overlay.remove();
        alert("Nenhuma resposta foi registrada. Por favor, comece novamente.");
        window.location.href = '/'; 
    }
}

async function sendAnswersAndRedirect(answers) {
    const overlay = document.getElementById('loading-overlay'); 
    try {
        const response = await fetch('/api/calculate', { 
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ answers: answers }) 
        });
        if (!response.ok) { 
            let errorBody = await response.text(); 
            throw new Error(`Erro do Servidor: ${response.status} ${response.statusText}. Detalhes: ${errorBody}`);
        }
        const result = await response.json(); 
        if (result.success) { 
            console.log("Cálculo bem-sucedido no backend. Redirecionando para /results...");
            window.location.href = '/results'; 
        } else {
            throw new Error(result.error || 'Ocorreu um erro no cálculo no servidor (resposta não indicou sucesso).');
        }
    } catch (error) {
        console.error('Erro ao enviar respostas ou na resposta da API:', error);
        if (overlay) overlay.remove(); 
         alert(`Houve um problema ao processar seus resultados:\n\n${error.message}\n\nPor favor, tente novamente.`);
    }
}

// --- Event Listeners Iniciais (Corrigido para carregar a questão automaticamente) ---
document.addEventListener('DOMContentLoaded', () => {
    console.log("DOM carregado - Versão com Redirecionamento."); 
    const introSection = document.getElementById('intro'); 
    const assessmentSection = document.getElementById('assessment');
    const resultsSection = document.getElementById('results'); 
    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn');
    const totalQuestionsSpan = document.getElementById('total-questions');
    const newAssessmentBtn = document.getElementById('new-assessment'); 
    const startBtn = document.getElementById('start-btn'); 

    // Verifica se a seção de avaliação está visível para iniciar o quiz
    if (assessmentSection && window.getComputedStyle(assessmentSection).display !== 'none') {
        console.log("Seção de avaliação visível. Iniciando quiz.");
        if (totalQuestionsSpan) totalQuestionsSpan.textContent = totalQuestions;
        
        // CORREÇÃO: Chamar loadQuestion(0) diretamente para iniciar o quiz mesmo sem clicar em nenhum botão
        loadQuestion(0);
    // Configura o botão start se a introdução estiver visível
    } else if (introSection && window.getComputedStyle(introSection).display !== 'none') {
         console.log("Seção de introdução visível.");
          if (startBtn && assessmentSection && resultsSection) { 
             // Adiciona listener para o botão start (se existir nesta página)
             startBtn.addEventListener('click', () => startAssessment(introSection, assessmentSection, resultsSection));
         } else {
              console.warn("Botão Start ou seções faltando para configurar o início.");
         }
         if (totalQuestionsSpan) totalQuestionsSpan.textContent = totalQuestions;
    } else {
         console.log("Nem introdução nem avaliação visíveis. Verifique o display inicial das seções no HTML/CSS.");
    }

    // Configura botões de navegação do quiz
    if (nextBtn) nextBtn.addEventListener('click', () => goToNextQuestion(false));
    if (prevBtn) prevBtn.addEventListener('click', goToPreviousQuestion);
    
    // Configura botão Nova Avaliação (se existir)
    if (newAssessmentBtn) {
         newAssessmentBtn.addEventListener('click', () => {
             console.log("Botão Nova Avaliação clicado.");
             window.location.href = '/quiz'; // Simplesmente redireciona para /quiz
         });
    }
    
     console.log("Setup inicial do DISC (JS) concluído.");
});

// Adicionar classe CSS para feedback visual (opcional no styles.css)
/*
.btn-flash-error {
  animation: flash-error 0.5s ease-out;
}
@keyframes flash-error {
  0%, 100% { background-color: transparent; }
  50% { background-color: #dc3545; } 
}
*/