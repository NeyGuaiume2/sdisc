// Variáveis globais para controle do quiz
let currentQuestionIndex = 0;
let userResponses = {};
let countdownTimer;
let discChartInstance = null;

// --- IMPORTANTE: Carregar as perguntas reais ---
// Garanta que este array 'questions' seja populado corretamente.
// Se você tem um arquivo disc_questions.js, ele deve ser carregado ANTES deste script no HTML.
// Usando o array de teste como fallback ou se não houver carregamento externo:
const questions = typeof discQuestions !== 'undefined' && Array.isArray(discQuestions) && discQuestions.length > 0
    ? discQuestions
    : [ // Array de teste MÍNIMO se discQuestions não carregar
        { id: 1, options: [{ id: "A", text: "CARREGANDO..." }, { id: "B", text: "POR FAVOR" }, { id: "C", text: "VERIFIQUE" }, { id: "D", text: "SCRIPT" }] }
      ];
// Recalcular totalQuestions baseado no array real (seja ele qual for)
const totalQuestions = questions.length;

// --- Funções do Quiz ---

function startAssessment(introSection, assessmentSection, resultsSection) {
    console.log("startAssessment chamada"); // Log para depuração
    if (!introSection || !assessmentSection || !resultsSection) {
        console.error("Erro: Seções não encontradas em startAssessment.");
        return;
    }
    introSection.style.display = 'none';
    resultsSection.style.display = 'none';
    assessmentSection.style.display = 'block';
    currentQuestionIndex = 0;
    userResponses = {};
    // Chamar loadQuestion para iniciar ou reiniciar o quiz
    if (questions.length > 0) {
        loadQuestion(currentQuestionIndex);
    } else {
        console.error("Nenhuma questão carregada para iniciar a avaliação.");
        // Talvez exibir uma mensagem de erro na interface
        const optionsList = document.getElementById('options-list');
        if(optionsList) optionsList.innerHTML = '<p class="warning">Erro: Nenhuma questão foi carregada. Verifique a configuração.</p>';
    }
}

function loadQuestion(index) {
    console.log(`loadQuestion chamada para índice: ${index}`); // Log
    const optionsList = document.getElementById('options-list');
    const questionNumberSpan = document.getElementById('question-number');
    const totalQuestionsSpan = document.getElementById('total-questions');
    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn'); // Precisa do nextBtn aqui

    if (!optionsList || !questionNumberSpan || !totalQuestionsSpan || !prevBtn || !nextBtn) {
        console.error("Erro: Elementos essenciais da questão não encontrados em loadQuestion (optionsList, spans, prevBtn, nextBtn).");
        return;
    }
    if (index < 0 || index >= totalQuestions) {
        console.error(`Índice de questão inválido: ${index}. Total de questões: ${totalQuestions}`);
        // Poderia finalizar o quiz ou mostrar erro se o índice for inválido
         if (index >= totalQuestions && totalQuestions > 0) {
             console.log("Tentativa de carregar questão após a última. Finalizando.");
             finishAssessment(); // Finaliza se tentar ir além da última
         }
        return;
    }

    const question = questions[index];
     if (!question || !question.options || !Array.isArray(question.options)) {
         console.error(`Dados inválidos para a questão no índice ${index}:`, question);
         // Mostrar erro na interface
         optionsList.innerHTML = `<p class="warning">Erro ao carregar dados da questão ${index + 1}.</p>`;
         // Desabilitar botões para evitar problemas
         prevBtn.disabled = true;
         nextBtn.disabled = true;
         return;
     }

    console.log(`Carregando questão ID: ${question.id}, Texto da primeira opção: ${question.options[0]?.text}`); // Log

    currentQuestionIndex = index;
    optionsList.innerHTML = '';

    questionNumberSpan.textContent = index + 1;
    totalQuestionsSpan.textContent = totalQuestions;

    question.options.forEach(option => {
        const optionItem = document.createElement('div');
        optionItem.classList.add('option-item');

        optionItem.innerHTML = `
            <div class="option-text">${option.text}</div>
            <div class="radio-container mais">
                <input type="radio" name="most_${question.id}" value="${option.id}" class="most-option" data-question-id="${question.id}">
            </div>
            <div class="radio-container menos">
                <input type="radio" name="least_${question.id}" value="${option.id}" class="least-option" data-question-id="${question.id}">
            </div>
        `;
        optionsList.appendChild(optionItem);
    });

    const savedResponse = userResponses[question.id];
    if (savedResponse) {
        const mostRadio = optionsList.querySelector(`input.most-option[value="${savedResponse.most}"]`);
        const leastRadio = optionsList.querySelector(`input.least-option[value="${savedResponse.least}"]`);
        if (mostRadio) mostRadio.checked = true;
        if (leastRadio) leastRadio.checked = true;
    }

    prevBtn.disabled = (index === 0);
    checkNextButtonState();
    addOptionListeners();
    startCountdown(); // Inicia ou reinicia o contador para a nova questão
}

function addOptionListeners() {
    const optionsList = document.getElementById('options-list');
    if (!optionsList) return;
    const radioButtons = optionsList.querySelectorAll('input[type="radio"]');
    radioButtons.forEach(radio => {
        radio.removeEventListener('change', handleSelectionChange);
        radio.addEventListener('change', handleSelectionChange);
    });
}

function handleSelectionChange(event) {
    const changedRadio = event.target;
    const questionId = changedRadio.getAttribute('data-question-id');
    const currentValue = changedRadio.value;
    const isMost = changedRadio.name.startsWith('most_');
    const optionsList = document.getElementById('options-list');

    if(!optionsList || !questionId) return; // Verificação adicional

    // Garantir que a mesma opção não pode ser MAIS e MENOS
    if (isMost) {
        const conflictingLeast = optionsList.querySelector(`input[name="least_${questionId}"][value="${currentValue}"]:checked`);
        if (conflictingLeast) {
            conflictingLeast.checked = false;
        }
    } else { // isLeast
        const conflictingMost = optionsList.querySelector(`input[name="most_${questionId}"][value="${currentValue}"]:checked`);
        if (conflictingMost) {
            conflictingMost.checked = false;
        }
    }
    saveCurrentResponse();
    checkNextButtonState();
}

function saveCurrentResponse() {
     // Adiciona verificação se questions[currentQuestionIndex] existe
     if (!questions || currentQuestionIndex >= questions.length) return;

    const questionId = questions[currentQuestionIndex].id;
    const optionsList = document.getElementById('options-list');
    if(!optionsList) return;

    const mostChecked = optionsList.querySelector(`input[name="most_${questionId}"]:checked`);
    const leastChecked = optionsList.querySelector(`input[name="least_${questionId}"]:checked`);

    if (mostChecked && leastChecked) {
         userResponses[questionId] = {
             questionId: questionId,
             most: mostChecked.value,
             least: leastChecked.value
         };
    } else {
         delete userResponses[questionId];
    }
     // console.log("Respostas atuais:", userResponses);
}

function checkNextButtonState() {
    const nextBtn = document.getElementById('next-btn');
    const optionsList = document.getElementById('options-list');
    // Adiciona verificação se questions[currentQuestionIndex] existe
     if (!nextBtn || !optionsList || !questions || currentQuestionIndex >= questions.length) {
         if(nextBtn) nextBtn.disabled = true; // Desabilita se algo estiver errado
         return;
     }

     const questionId = questions[currentQuestionIndex].id;
     const mostChecked = optionsList.querySelector(`input[name="most_${questionId}"]:checked`);
     const leastChecked = optionsList.querySelector(`input[name="least_${questionId}"]:checked`);

    nextBtn.disabled = !(mostChecked && leastChecked);
}

function startCountdown() {
    const countdownSpan = document.getElementById('countdown');
    if (!countdownSpan) return;

    let timeLeft = 15;
    countdownSpan.textContent = timeLeft;

    clearInterval(countdownTimer); // Limpa timer anterior SEMPRE
    countdownTimer = setInterval(() => {
        timeLeft--;
        // Busca o elemento novamente a cada segundo, caso tenha sido recriado
        const currentCountdownSpan = document.getElementById('countdown');
        if (currentCountdownSpan) {
             currentCountdownSpan.textContent = timeLeft;
        } else {
             console.warn("Elemento countdown não encontrado, parando timer.");
             clearInterval(countdownTimer);
             return;
        }

        if (timeLeft <= 0) {
            clearInterval(countdownTimer);
            console.log("Tempo esgotado para questão:", currentQuestionIndex + 1);
            goToNextQuestion(true); // Força ir para a próxima
        }
    }, 1000);
}

function goToNextQuestion(forceNext = false) {
    console.log(`goToNextQuestion chamada. forceNext: ${forceNext}`); // Log
    saveCurrentResponse();

     // Adiciona verificação se questions[currentQuestionIndex] existe
     if (!questions || currentQuestionIndex >= questions.length) {
        console.error("Estado inválido em goToNextQuestion, currentQuestionIndex fora dos limites.");
        return; // Impede continuação se o índice estiver errado
     }

    const currentQuestionId = questions[currentQuestionIndex].id;

    if (!forceNext && !userResponses[currentQuestionId]) {
         console.warn("Tentativa de avançar sem resposta completa (não forçado).");
         // Mostra um feedback visual rápido para o usuário, se desejar
          const nextBtn = document.getElementById('next-btn');
          if (nextBtn) {
              nextBtn.classList.add('btn-flash-error'); // Classe CSS temporária para piscar o botão
              setTimeout(() => nextBtn.classList.remove('btn-flash-error'), 500);
          }
         return; // Não avançar
    }

    // Limpar timer atual *antes* de potencialmente carregar a próxima questão
    clearInterval(countdownTimer);

    if (currentQuestionIndex < totalQuestions - 1) {
        loadQuestion(currentQuestionIndex + 1); // Carrega a próxima, que reiniciará o timer
    } else {
        console.log("Última questão respondida ou tempo esgotado. Finalizando.");
        finishAssessment(); // Finaliza após a última questão
    }
}

function goToPreviousQuestion() {
     console.log("goToPreviousQuestion chamada"); // Log
    if (currentQuestionIndex > 0) {
        saveCurrentResponse();
        // Limpar timer atual *antes* de carregar a questão anterior
        clearInterval(countdownTimer);
        loadQuestion(currentQuestionIndex - 1); // Carrega a anterior, que reiniciará o timer
    }
}

function finishAssessment() {
     console.log("finishAssessment chamada"); // Log
    const assessmentSection = document.getElementById('assessment');
    const resultsSection = document.getElementById('results');
     if (!assessmentSection || !resultsSection) {
         console.error("Seções de avaliação/resultado não encontradas para finalizar.");
         return;
     }

    assessmentSection.style.display = 'none';
    resultsSection.style.display = 'block';
    clearInterval(countdownTimer); // Parar o timer definitivamente

    const answersArray = Object.values(userResponses);

    if (answersArray.length < totalQuestions) {
         console.warn(`Avaliação finalizada com ${answersArray.length} de ${totalQuestions} respostas.`);
    }

    console.log("Enviando respostas para cálculo:", answersArray);
    // Adiciona verificação se há respostas para enviar
    if (answersArray.length > 0) {
        calculateDiscResult(answersArray);
    } else {
        console.warn("Nenhuma resposta para enviar.");
        // Exibir mensagem na tela de resultados
        const primaryProfile = document.getElementById('primary-profile');
        if(primaryProfile) primaryProfile.innerHTML = "Nenhuma resposta foi registrada.";
    }
}

async function calculateDiscResult(answers) {
    // ... (código da função calculateDiscResult permanece o mesmo) ...
     const primaryProfile = document.getElementById('primary-profile');
     const profileDetails = document.getElementById('profile-details');
     if (!primaryProfile || !profileDetails) return;

     primaryProfile.innerHTML = 'Calculando resultados...';
     profileDetails.innerHTML = '';

     try {
         const response = await fetch('/api/calculate', { // Verifique a URL da API
             method: 'POST',
             headers: { 'Content-Type': 'application/json' },
             body: JSON.stringify({ answers: answers }) // Enviar como objeto com chave 'answers'
         });

         if (!response.ok) {
             // Tenta ler o corpo do erro, se possível
             let errorBody = await response.text();
             try { // Tenta parsear como JSON
                 errorBody = JSON.stringify(JSON.parse(errorBody), null, 2);
             } catch (e) { /* Mantém como texto se não for JSON */ }
             throw new Error(`Erro HTTP: ${response.status} ${response.statusText}\n${errorBody}`);
         }
         const result = await response.json();
         if (result.success && result.results) {
             console.log("Resultados recebidos:", result.results);
             displayResults(result.results);
         } else {
             // Usa o erro da resposta JSON se existir, senão uma mensagem padrão
             throw new Error(result.error || 'Formato de resposta inesperado da API.');
         }
     } catch (error) {
         console.error('Erro na requisição ou processamento:', error);
          primaryProfile.innerHTML = 'Erro ao obter resultados.';
          // Exibe a mensagem de erro de forma mais clara
          profileDetails.innerHTML = `<p class="warning">Detalhes: ${error.message.replace(/\n/g, '<br>')}</p>`;
     }
}

function displayResults(results) {
    // ... (código da função displayResults permanece o mesmo) ...
     const primaryProfile = document.getElementById('primary-profile');
     const profileDetails = document.getElementById('profile-details');
     const chartCanvas = document.getElementById('disc-chart');
     const downloadPdfBtn = document.getElementById('download-pdf');
      if (!primaryProfile || !profileDetails || !chartCanvas) return;

     // Exemplo de exibição (Adapte conforme a estrutura de 'results' do seu backend)
     if (results.predominant && results.normalizedScores) {
         primaryProfile.innerHTML = `Seu perfil predominante: <strong>${results.predominant}</strong>`;
         let detailsHtml = '<ul>';
         detailsHtml += `<li>Dominância (D): ${results.normalizedScores.D ?? 'N/A'}</li>`;
         detailsHtml += `<li>Influência (I): ${results.normalizedScores.I ?? 'N/A'}</li>`;
         detailsHtml += `<li>Estabilidade (S): ${results.normalizedScores.S ?? 'N/A'}</li>`;
         detailsHtml += `<li>Conformidade (C): ${results.normalizedScores.C ?? 'N/A'}</li>`;
         detailsHtml += '</ul>';

         // Adiciona descrições se existirem
         if (results.profileDescription) {
             if (results.profileDescription.levels) {
                  detailsHtml += '<h4>Níveis:</h4><p>';
                  detailsHtml += `D: ${results.profileDescription.levels.D}, `;
                  detailsHtml += `I: ${results.profileDescription.levels.I}, `;
                  detailsHtml += `S: ${results.profileDescription.levels.S}, `;
                  detailsHtml += `C: ${results.profileDescription.levels.C}`;
                  detailsHtml += '</p>';
             }
              if (results.profileDescription.strengths?.length) {
                  detailsHtml += '<h4>Pontos Fortes:</h4><ul>';
                  results.profileDescription.strengths.forEach(s => { detailsHtml += `<li>${s}</li>`; });
                  detailsHtml += '</ul>';
             }
              if (results.profileDescription.weaknesses?.length) {
                  detailsHtml += '<h4>Pontos Fracos:</h4><ul>';
                  results.profileDescription.weaknesses.forEach(w => { detailsHtml += `<li>${w}</li>`; });
                  detailsHtml += '</ul>';
             }
             if (results.profileDescription.recommendations?.length) {
                  detailsHtml += '<h4>Recomendações:</h4><ul>';
                  results.profileDescription.recommendations.forEach(r => { detailsHtml += `<li>${r}</li>`; });
                  detailsHtml += '</ul>';
             }
         }
         profileDetails.innerHTML = detailsHtml;

         renderChart(results.normalizedScores, chartCanvas);

         if (downloadPdfBtn) {
              downloadPdfBtn.disabled = false;
              // downloadPdfBtn.onclick = () => generatePdfReport(results); // Adicionar lógica PDF
         }

     } else {
         primaryProfile.innerHTML = 'Resultados incompletos recebidos.';
         profileDetails.innerHTML = `<pre>${JSON.stringify(results, null, 2)}</pre>`; // Mostrar dados brutos
          if (downloadPdfBtn) downloadPdfBtn.disabled = true;
     }
}

function renderChart(scores, canvasElement) {
    // ... (código da função renderChart permanece o mesmo) ...
     if (!canvasElement || !window.Chart || !scores) {
         console.error("Canvas, Chart.js ou scores não encontrados para renderizar gráfico.");
         return;
     }
     const ctx = canvasElement.getContext('2d');

      if (discChartInstance) {
          discChartInstance.destroy(); // Destruir gráfico anterior
      }

     discChartInstance = new Chart(ctx, {
         type: 'bar',
         data: {
             labels: ['Dominância (D)', 'Influência (I)', 'Estabilidade (S)', 'Conformidade (C)'],
             datasets: [{
                 label: 'Pontuação DISC (Normalizada 1-25)',
                 data: [scores.D ?? 0, scores.I ?? 0, scores.S ?? 0, scores.C ?? 0], // Usar ?? 0 para garantir número
                 backgroundColor: [
                     'rgba(217, 83, 79, 0.6)',  // D - Vermelho
                     'rgba(240, 173, 78, 0.6)', // I - Amarelo/Laranja
                     'rgba(92, 184, 92, 0.6)',  // S - Verde
                     'rgba(59, 133, 185, 0.6)'  // C - Azul
                 ],
                 borderColor: [
                     'rgba(217, 83, 79, 1)',
                     'rgba(240, 173, 78, 1)',
                     'rgba(92, 184, 92, 1)',
                     'rgba(59, 133, 185, 1)'
                 ],
                 borderWidth: 1
             }]
         },
         options: {
             indexAxis: 'y', // Barras horizontais
              scales: {
                  x: { // Eixo X agora representa a pontuação
                      beginAtZero: true,
                      max: 25
                  }
              },
             responsive: true,
             maintainAspectRatio: false,
              plugins: {
                  legend: {
                      display: false
                  },
                  title: {
                      display: true,
                      text: 'Perfil Comportamental DISC'
                  }
              }
         }
     });
}

// --- Event Listeners Iniciais ---
document.addEventListener('DOMContentLoaded', () => {
    console.log("DOM completamente carregado e parseado."); // Log inicial

    // Buscar elementos essenciais UMA VEZ após o DOM carregar
    const introSection = document.getElementById('intro'); // Pode não existir em quiz.html
    const assessmentSection = document.getElementById('assessment');
    const resultsSection = document.getElementById('results');
    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn');
    const totalQuestionsSpan = document.getElementById('total-questions');
    const newAssessmentBtn = document.getElementById('new-assessment');
    const downloadPdfBtn = document.getElementById('download-pdf');
    const startBtn = document.getElementById('start-btn'); // Pode não existir em quiz.html

    // ** CORREÇÃO CENTRAL: Iniciar o quiz se a seção de avaliação estiver visível **
    if (assessmentSection && window.getComputedStyle(assessmentSection).display !== 'none') {
        console.log("Seção de avaliação visível. Iniciando o quiz automaticamente.");
        // Garantir que o total de questões seja exibido
        if (totalQuestionsSpan) {
             totalQuestionsSpan.textContent = totalQuestions;
        } else {
             console.warn("Elemento totalQuestionsSpan não encontrado.");
        }
        // Carregar a primeira questão se houver questões
        if (questions && questions.length > 0) {
            loadQuestion(0); // Chama loadQuestion que por sua vez chama startCountdown
        } else {
            console.error("Nenhuma questão encontrada para carregar. Verifique o array 'questions'.");
             // Exibir erro na interface
             const optionsList = document.getElementById('options-list');
             if(optionsList) optionsList.innerHTML = '<p class="warning">Erro: Nenhuma questão foi carregada. Verifique a configuração.</p>';
              // Desabilitar botões
             if (prevBtn) prevBtn.disabled = true;
             if (nextBtn) nextBtn.disabled = true;
        }
    } else if (introSection && window.getComputedStyle(introSection).display !== 'none') {
         console.log("Seção de introdução visível. Aguardando botão Iniciar.");
          // Configurar botão Iniciar se ele existir nesta página (index.html)
          if (startBtn && assessmentSection && resultsSection) { // Precisa das seções para passar adiante
             startBtn.addEventListener('click', () => startAssessment(introSection, assessmentSection, resultsSection));
         } else if (!startBtn){
              console.warn("Seção de introdução visível, mas botão 'start-btn' não encontrado.");
         } else {
              console.warn("Seção de introdução visível, mas falta assessmentSection ou resultsSection para a função startAssessment.");
         }
         // Exibir total de questões na introdução se o span existir
         if (totalQuestionsSpan) {
            totalQuestionsSpan.textContent = totalQuestions;
        }

    } else {
         console.log("Nem introdução nem avaliação visíveis inicialmente. Estado inesperado?");
    }

    // Configurar botões de navegação e nova avaliação (se existirem)
    if (nextBtn) {
        nextBtn.addEventListener('click', () => goToNextQuestion(false));
    } else {
         console.warn("Botão 'next-btn' não encontrado.");
    }

    if (prevBtn) {
        prevBtn.addEventListener('click', goToPreviousQuestion);
    } else {
         console.warn("Botão 'prev-btn' não encontrado.");
    }

    if (newAssessmentBtn && resultsSection && assessmentSection && introSection) { // Precisa de todas as seções para reiniciar corretamente
        // Ao clicar em Nova Avaliação na tela de resultados, esconde resultados, mostra intro
         newAssessmentBtn.addEventListener('click', () => {
             console.log("Botão Nova Avaliação clicado.");
             resultsSection.style.display = 'none';
             // Decide se volta para intro ou direto para assessment? Vamos para intro.
             introSection.style.display = 'block'; // Mostra intro novamente
             assessmentSection.style.display = 'none'; // Esconde assessment
             // startAssessment seria chamado pelo botão na intro
         });

    } else if (newAssessmentBtn) {
         console.warn("Botão 'new-assessment' encontrado, mas faltam seções (intro, assessment, results) para configurar o reinício completo.");
         // Adicionar um comportamento padrão mínimo se faltar algo:
         newAssessmentBtn.addEventListener('click', () => {
            alert("Recarregando a página para nova avaliação..."); // Solução simples
            window.location.reload(); // Recarrega a página atual
        });
    } else {
         console.warn("Botão 'new-assessment' não encontrado.");
    }


    // Desabilitar botão PDF inicialmente (se existir)
    if (downloadPdfBtn) {
         downloadPdfBtn.disabled = true;
         // downloadPdfBtn.addEventListener('click', () => generatePdfReport(resultadosAtuais));
    }

     console.log("Setup inicial do DISC concluído.");
});

// Adicionar classe CSS para feedback visual (opcional)
// No seu styles.css adicione algo como:
// .btn-flash-error {
//   animation: flash-error 0.5s ease-out;
// }
// @keyframes flash-error {
//   0%, 100% { background-color: /* cor original do botão Próximo */; }
//   50% { background-color: #dc3545; } /* Vermelho para erro */
// }