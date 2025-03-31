// backend/static/js/script.js
// Versão 1.1.0 - Busca questões da API, usa palavras como valor, ajusta fluxo

// --- Variáveis Globais ---
let currentQuestionIndex = 0;
let userResponses = {}; // { questionId: { questionId: id, mais: "palavra", menos: "palavra" }, ... }
let countdownTimer;
let isTransitioning = false;
let questions = []; // Array para armazenar as questões buscadas da API
let totalQuestions = 0; // Será definido após buscar as questões

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
const loadingIndicator = document.getElementById('loading-indicator'); // Adicione um indicador de carregamento no HTML se desejar

// --- Funções do Quiz ---

async function fetchQuestions() {
    console.log("fetchQuestions: Buscando questões da API...");
    if(loadingIndicator) loadingIndicator.style.display = 'block'; // Mostra indicador
    try {
        const response = await fetch('/api/questions'); // Chama a nova rota
        if (!response.ok) {
            throw new Error(`Erro HTTP ${response.status} ao buscar questões.`);
        }
        questions = await response.json();
        totalQuestions = questions.length;
        console.log(`fetchQuestions: ${totalQuestions} questões carregadas com sucesso.`);

        if (totalQuestions > 0) {
             if (totalQuestionsSpan) totalQuestionsSpan.textContent = totalQuestions; // Atualiza o total no HTML
             return true; // Indica sucesso
        } else {
            console.error("fetchQuestions: Nenhuma questão recebida da API.");
            if(optionsList) optionsList.innerHTML = '<p class="warning">Erro: Nenhuma questão foi carregada do servidor.</p>';
            return false; // Indica falha
        }
    } catch (error) {
        console.error("fetchQuestions: Falha ao buscar ou processar questões:", error);
        if(optionsList) optionsList.innerHTML = `<p class="warning">Erro ao carregar questões: ${error.message}. Tente recarregar a página.</p>`;
        return false; // Indica falha
    } finally {
         if(loadingIndicator) loadingIndicator.style.display = 'none'; // Esconde indicador
    }
}


function startAssessment() {
    console.log("startAssessment: Iniciando avaliação...");
    if (!assessmentSection || !resultsSection || !quizCompletionSection ) {
        console.error("Erro Crítico: Seções principais do DOM não encontradas.");
        return;
    }
    // Garante que estamos no estado inicial visualmente
    resultsSection.style.display = 'none';
    quizCompletionSection.style.display = 'none';
    assessmentSection.style.display = 'block'; // Mostra a seção do quiz
    if(quizHeader) quizHeader.classList.remove('hidden');
    if(timerContainer) timerContainer.classList.remove('hidden');
    if(questionContentWrapper) {
        questionContentWrapper.style.display = '';
        questionContentWrapper.classList.remove('fading-out', 'hidden');
    }

    currentQuestionIndex = 0;
    userResponses = {};
    isTransitioning = false;

    // Verifica se as questões já foram carregadas (devem ter sido pelo DOMContentLoaded)
    if (questions.length > 0) {
        console.log("startAssessment: Questões já carregadas, iniciando com a primeira.");
        loadQuestion(currentQuestionIndex);
    } else {
        // Isso não deveria acontecer se o fetch no DOMContentLoaded funcionou
        console.error("startAssessment: Tentando iniciar, mas NENHUMA questão está carregada.");
        if(optionsList) optionsList.innerHTML = '<p class="warning">Erro: Não foi possível carregar as questões. Por favor, recarregue a página.</p>';
    }
}

function loadQuestion(index) {
    console.log(`--- loadQuestion: Iniciando para índice ${index} ---`);
     // Reset da flag de transição
     if (isTransitioning) {
        isTransitioning = false;
        console.log("loadQuestion: Resetando isTransitioning para FALSE.");
     }

    if (!optionsList || !questionNumberSpan || !questionContentWrapper || !countdownSpan) {
        console.error("!!! loadQuestion: Elemento(s) do DOM essenciais não encontrado(s) !!!");
        return;
    }

    if (index < 0 || index >= totalQuestions) {
         console.error(`loadQuestion: Índice de questão inválido: ${index}. Total: ${totalQuestions}. Não carregando.`);
         // Poderia chamar showCompletionScreen aqui se index >= totalQuestions,
         // mas é melhor que a lógica de avanço trate isso.
         return;
     }

    const question = questions[index];
    console.log(`loadQuestion: Carregando dados para questão ID ${question.id}:`, question);

     // Validação da estrutura da questão recebida da API
     if (!question || typeof question !== 'object' || !question.id || !question.D || !question.I || !question.S || !question.C) {
          console.error(`!!! loadQuestion: Dados inválidos ou incompletos para a questão no índice ${index} !!!`, question);
          optionsList.innerHTML = `<p class="warning">Erro ao carregar dados da questão ${index + 1}. Estrutura inesperada.</p>`;
          // Considerar parar o quiz ou pular para a próxima? Parar é mais seguro.
          clearInterval(countdownTimer); // Para o timer se houver erro grave
          return;
      }


    currentQuestionIndex = index;
    console.log(`loadQuestion: currentQuestionIndex atualizado para ${currentQuestionIndex}`);

    optionsList.innerHTML = ''; // Limpa opções anteriores
    questionNumberSpan.textContent = index + 1; // Atualiza número da questão

    console.log("loadQuestion: Gerando opções...");
    // ---- Adaptação para a estrutura {id, D, I, S, C} ----
    const profiles = ['D', 'I', 'S', 'C'];
    // Opcional: Embaralhar a ordem das palavras exibidas
    // profiles.sort(() => Math.random() - 0.5);

    profiles.forEach(profileKey => {
        const word = question[profileKey]; // Pega a palavra (ex: question['D'])
        const optionItem = document.createElement('div');
        optionItem.classList.add('option-item');

        // O value do radio agora é a PALAVRA
        optionItem.innerHTML = `
            <div class="option-text">${word}</div>
            <div class="radio-container mais">
                <input type="radio" id="most_${question.id}_${profileKey}" name="most_${question.id}" value="${word}" class="most-option" data-question-id="${question.id}" data-profile="${profileKey}">
            </div>
            <div class="radio-container menos">
                <input type="radio" id="least_${question.id}_${profileKey}" name="least_${question.id}" value="${word}" class="least-option" data-question-id="${question.id}" data-profile="${profileKey}">
            </div>
        `;
        optionsList.appendChild(optionItem);
    });
    // --------------------------------------------------
    console.log("loadQuestion: Opções geradas.");

    // Restaurar resposta salva (se houver) para esta questão
    const savedResponse = userResponses[question.id];
    if (savedResponse) {
         console.log("loadQuestion: Restaurando resposta salva:", savedResponse);
        // Busca pelo VALUE (palavra) agora
        const mostRadio = optionsList.querySelector(`.most-option[value="${CSS.escape(savedResponse.mais)}"]`);
        const leastRadio = optionsList.querySelector(`.least-option[value="${CSS.escape(savedResponse.menos)}"]`);
        if (mostRadio) mostRadio.checked = true;
        if (leastRadio) leastRadio.checked = true;
        console.log("loadQuestion: Radios restaurados (checked):", mostRadio, leastRadio);
    }

    addOptionListeners(); // Adiciona listeners aos novos radios

    // Fade-in da nova questão
    questionContentWrapper.classList.remove('fading-out');
    void questionContentWrapper.offsetWidth; // Força reflow para garantir que a animação ocorra

    startCountdown(); // Inicia o timer para a nova questão

    console.log(`--- loadQuestion: Concluído para índice ${index} ---`);
}


function addOptionListeners() {
    const radioButtons = optionsList.querySelectorAll('input[type="radio"]');
    radioButtons.forEach(radio => {
        // Remove listener antigo para evitar duplicação
        radio.removeEventListener('change', handleSelectionChange);
        // Adiciona o novo
        radio.addEventListener('change', handleSelectionChange);
    });

    // Listener para clicar no container (melhora usabilidade)
    const radioContainers = optionsList.querySelectorAll('.radio-container');
    radioContainers.forEach(container => {
         container.removeEventListener('click', handleContainerClick);
         container.addEventListener('click', handleContainerClick);
    });
}

function handleContainerClick(event) {
    // Se o clique foi diretamente no input, o 'change' já trata
    if (event.target.tagName === 'INPUT') return;
    // Acha o input dentro do container clicado
    const input = event.currentTarget.querySelector('input[type="radio"]');
    // Se achou e não está marcado, marca e dispara o evento 'change'
    if (input && !input.checked) {
        input.checked = true;
        // Dispara o evento para que handleSelectionChange seja chamado
        input.dispatchEvent(new Event('change', { bubbles: true }));
    }
}


function handleSelectionChange(event) {
    if (isTransitioning) return; // Ignora cliques durante a transição

    const changedRadio = event.target;
    const questionId = changedRadio.getAttribute('data-question-id');
    const selectedWord = changedRadio.value; // O VALOR AGORA É A PALAVRA
    const isMost = changedRadio.classList.contains('most-option');

    if (!optionsList || !questionId) {
        console.error("handleSelectionChange: Não foi possível obter optionsList ou questionId.");
        return;
    }

    console.log(`handleSelectionChange: Seleção alterada - Questão ${questionId}, Palavra: "${selectedWord}", Tipo: ${isMost ? 'MAIS' : 'MENOS'}`);

    // --- Lógica para desmarcar seleção conflitante ---
    const otherTypeClass = isMost ? '.least-option' : '.most-option';
    // Encontra o radio do OUTRO tipo (menos ou mais) que tenha a MESMA palavra (value)
    const conflictingRadio = optionsList.querySelector(`${otherTypeClass}[value="${CSS.escape(selectedWord)}"]`);

    if (conflictingRadio && conflictingRadio.checked) {
        console.log(`handleSelectionChange: Desmarcando seleção conflitante: ${isMost ? 'MENOS' : 'MAIS'} para a palavra "${selectedWord}"`);
        conflictingRadio.checked = false;
    }
    // ------------------------------------------------

    saveCurrentResponse(); // Salva a resposta atual (pode estar incompleta)
    checkAndAdvance();     // Verifica se ambos (MAIS e MENOS) foram marcados para avançar
}


function saveCurrentResponse() {
     if (!questions || currentQuestionIndex < 0 || currentQuestionIndex >= questions.length) {
         console.error("saveCurrentResponse: Índice de questão inválido ou questões não carregadas.");
         return;
     }
     const questionId = questions[currentQuestionIndex].id;
     if(!optionsList) return;

     // Busca os radios marcados para a questão atual
     const mostChecked = optionsList.querySelector(`input.most-option[name="most_${questionId}"]:checked`);
     const leastChecked = optionsList.querySelector(`input.least-option[name="least_${questionId}"]:checked`);

     // Salva a resposta (agora com as palavras) se ambas estiverem selecionadas
     if (mostChecked && leastChecked) {
          const response = {
              questionId: questionId,
              mais: mostChecked.value, // Salva a palavra
              menos: leastChecked.value // Salva a palavra
          };
          userResponses[questionId] = response;
          console.log(`saveCurrentResponse: Resposta COMPLETA salva para questão ${questionId}:`, response);
     } else {
          // Se a resposta estiver incompleta, remove do objeto (ou mantém parcial, dependendo da lógica desejada)
          // Remover garante que apenas respostas completas sejam enviadas.
          if (userResponses[questionId]) {
              delete userResponses[questionId];
              console.log(`saveCurrentResponse: Resposta para questão ${questionId} removida (INCOMPLETA).`);
          }
     }
}


function startCountdown() {
    if (!countdownSpan || !timerContainer) return;
    let timeLeft = 15; // Segundos por questão
    countdownSpan.textContent = timeLeft;
    countdownSpan.style.color = ''; // Reseta cor
    timerContainer.style.backgroundColor = ''; // Reseta fundo

    clearInterval(countdownTimer); // Limpa timer anterior
    console.log("startCountdown: Timer iniciado para questão:", currentQuestionIndex + 1);

    countdownTimer = setInterval(() => {
        timeLeft--;
        const currentCountdownSpan = document.getElementById('countdown'); // Re-seleciona caso o DOM mude? (Não deve mudar)
        if (currentCountdownSpan) {
             currentCountdownSpan.textContent = timeLeft;
             // Muda cor perto do fim
             if (timeLeft <= 5 && timeLeft > 0) {
                 timerContainer.style.backgroundColor = '#ffe0e0'; // Vermelho claro
                 currentCountdownSpan.style.color = '#d9534f'; // Vermelho Bootstrap 'danger'
             } else if (timeLeft <=0 ) {
                 timerContainer.style.backgroundColor = '#f8d7da'; // Fundo de alerta vermelho
                 currentCountdownSpan.style.color = '#721c24'; // Texto de alerta vermelho
             } else {
                  timerContainer.style.backgroundColor = ''; // Normal
                  currentCountdownSpan.style.color = ''; // Normal
             }
        } else {
             console.warn("startCountdown: Elemento countdown não encontrado no intervalo. Limpando timer.");
             clearInterval(countdownTimer);
             return;
        }

        // Tempo esgotado
        if (timeLeft <= 0) {
            clearInterval(countdownTimer);
            console.log("startCountdown: Tempo esgotado para questão:", currentQuestionIndex + 1);
            // Verifica se é a última questão
            if (currentQuestionIndex >= totalQuestions - 1) {
                 console.log("startCountdown: Tempo esgotado NA ÚLTIMA questão. Mostrando tela de conclusão.");
                 showCompletionScreen();
            } else {
                 console.log("startCountdown: Tempo esgotado (não última). Avançando para próxima questão.");
                 advanceQuestion(true); // Força avanço
            }
        }
    }, 1000);
}

function checkAndAdvance() {
     console.log("checkAndAdvance: Verificando se pode avançar...");
     if (isTransitioning) {
         console.log("checkAndAdvance: Transição em andamento, aguardando.");
         return; // Não faz nada se já estiver transicionando
     }
     // Verifica se temos uma questão válida carregada
     if (!questions || currentQuestionIndex < 0 || currentQuestionIndex >= questions.length) {
          console.warn("checkAndAdvance: Tentando verificar avanço sem questão válida.");
          return;
     };

     const questionId = questions[currentQuestionIndex].id;
     // Verifica se a resposta para a questão atual está no objeto de respostas (ou seja, foi salva)
     const currentResponseComplete = userResponses.hasOwnProperty(questionId);

     if (currentResponseComplete) {
         console.log(`checkAndAdvance: Resposta completa para questão ${currentQuestionIndex + 1}.`);
         // É a última questão?
         if (currentQuestionIndex >= totalQuestions - 1) {
             console.log("checkAndAdvance: É a última questão. Mostrando tela de conclusão.");
             showCompletionScreen();
         } else {
             console.log("checkAndAdvance: Não é a última. Avançando para a próxima.");
             advanceQuestion(false); // Avança normalmente (sem forçar)
         }
     } else {
         console.log("checkAndAdvance: Resposta ainda incompleta. Aguardando...");
     }
}


function advanceQuestion(forceNext = false) {
    console.log(`advanceQuestion: Iniciando. forceNext=${forceNext}, isTransitioning=${isTransitioning}`);
    if (isTransitioning) {
        console.log("advanceQuestion: Já em transição, retornando.");
        return;
    }

    // Salva a resposta atual (mesmo que incompleta, caso forceNext seja true)
    // A lógica de saveCurrentResponse já garante que só salva se for completa,
    // mas chamamos aqui para garantir o estado mais recente antes da transição.
    saveCurrentResponse();

    clearInterval(countdownTimer); // Para o timer da questão atual
    isTransitioning = true; // Define que a transição começou
    console.log("advanceQuestion: isTransitioning definida como TRUE. Iniciando fade-out...");
    questionContentWrapper.classList.add('fading-out');

    const transitionDuration = 400; // ms - Deve ser igual à duração da animação CSS
    console.log(`advanceQuestion: Agendando próxima ação em ${transitionDuration}ms.`);

    // Espera a animação de fade-out terminar para carregar a próxima questão
    setTimeout(() => {
        console.log("advanceQuestion: Dentro do setTimeout (após fade-out).");
        const nextIndex = currentQuestionIndex + 1;
        console.log(`advanceQuestion: Próximo índice a carregar: ${nextIndex}`);

        // Verifica se ainda há questões para carregar
        if (nextIndex < totalQuestions) {
            loadQuestion(nextIndex); // Carrega a próxima questão
             // A flag isTransitioning será resetada DENTRO de loadQuestion
        } else {
            // Isso pode acontecer se advanceQuestion for chamado na última questão
            // (ex: pelo timeout do timer). Deve ir para a tela de conclusão.
            console.log("advanceQuestion: Não há mais questões (nextIndex >= totalQuestions). Indo para conclusão.");
            showCompletionScreen(); // Garante que vá para a tela final
        }
        // A flag isTransitioning é resetada no início de loadQuestion ou showCompletionScreen agora
    }, transitionDuration);
}


function showCompletionScreen() {
    console.log("showCompletionScreen: Preparando para mostrar tela de conclusão...");
    if (isTransitioning && !questionContentWrapper.classList.contains('fading-out')) {
        // Evita chamar múltiplas vezes se já estiver indo para a conclusão
        console.log("showCompletionScreen: Já em transição para conclusão, retornando.");
        return;
    }

    isTransitioning = true; // Garante que está em transição
    console.log("showCompletionScreen: isTransitioning definida como TRUE.");

    // Garante que a última resposta seja salva
    saveCurrentResponse();
    clearInterval(countdownTimer);
    console.log("showCompletionScreen: Timer parado.");

    // Esconde elementos do quiz com animação
    if(quizHeader) quizHeader.classList.add('hidden');
    if(timerContainer) timerContainer.classList.add('hidden');
    if(questionContentWrapper) questionContentWrapper.classList.add('fading-out');
    console.log("showCompletionScreen: Elementos do quiz escondidos/fading out.");

    const fadeOutDuration = 400; // ms
    setTimeout(() => {
        console.log("showCompletionScreen: Dentro do setTimeout (após fade-out).");
        // Esconde permanentemente o wrapper das questões
        if(questionContentWrapper) questionContentWrapper.style.display = 'none';
        // Mostra a seção de conclusão
        if(quizCompletionSection) {
            quizCompletionSection.style.display = 'block';
             // Força reflow e fade-in (opcional, mas pode ficar legal)
            quizCompletionSection.style.opacity = '0';
            void quizCompletionSection.offsetWidth;
            quizCompletionSection.style.transition = 'opacity 0.5s ease-in-out';
            quizCompletionSection.style.opacity = '1';
        }
        console.log("showCompletionScreen: Seção de conclusão exibida.");

        if (viewResultsBtn) {
            viewResultsBtn.disabled = false; // Habilita o botão
            // Garante que só há um listener
            viewResultsBtn.removeEventListener('click', handleViewResultsClick);
            viewResultsBtn.addEventListener('click', handleViewResultsClick);
            console.log("showCompletionScreen: Listener adicionado/atualizado no botão 'Ver Resultado'.");
        } else {
            console.error("showCompletionScreen: Botão 'Ver Resultado' (view-results-btn) não encontrado no DOM!");
        }
        // Fim da transição aqui
         isTransitioning = false;
         console.log("showCompletionScreen: isTransitioning definida como FALSE.");
    }, fadeOutDuration);
}


function handleViewResultsClick() {
    console.log("handleViewResultsClick: Botão 'Ver Resultado' clicado.");
    if(viewResultsBtn) {
        viewResultsBtn.disabled = true; // Desabilita para evitar cliques múltiplos
        viewResultsBtn.textContent = "Processando..."; // Feedback visual
        console.log("handleViewResultsClick: Botão desabilitado e texto alterado.");
    }
    finishAssessment(); // Chama a função que envia os dados
}


function finishAssessment() {
     console.log("finishAssessment: Finalizando avaliação e preparando envio.");

     // Pega as respostas do objeto (já devem estar no formato {questionId, mais: palavra, menos: palavra})
     const answersArray = Object.values(userResponses);

     // --- Overlay de Carregamento ---
     let overlay = document.getElementById('loading-overlay');
     if (!overlay) {
         // Cria o overlay se não existir
         document.body.insertAdjacentHTML('beforeend', `
             <div id="loading-overlay" style="position: fixed; inset: 0; background: rgba(255,255,255,0.85); z-index: 9999; display: flex; justify-content: center; align-items: center; flex-direction: column; gap: 15px; opacity: 0; transition: opacity 0.3s;">
                 <div class="spinner-border text-primary" role="status" style="width: 3rem; height: 3rem;">
                     <span class="visually-hidden">Carregando...</span>
                 </div>
                 <p style="font-size: 1.2em; color: #333;">Calculando seus resultados...</p>
             </div>
         `);
         overlay = document.getElementById('loading-overlay');
         // Força reflow para animar a opacidade
         void overlay.offsetWidth;
         overlay.style.opacity = '1';
         console.log("finishAssessment: Overlay de carregamento criado e exibido.");
     } else {
         // Reutiliza e mostra o overlay existente
         overlay.style.display = 'flex';
         overlay.style.opacity = '1';
         console.log("finishAssessment: Overlay de carregamento reutilizado.");
     }
     // -----------------------------

     // Verifica se todas as respostas foram dadas (opcional, mas bom para avisar)
     if (answersArray.length < totalQuestions) {
          console.warn(`finishAssessment: Avaliação finalizada com ${answersArray.length} de ${totalQuestions} respostas completas.`);
          // Poderia mostrar um aviso, mas prossegue mesmo assim
     } else {
          console.log("finishAssessment: Todas as questões respondidas.");
     }

     console.log("finishAssessment: Enviando respostas para /api/calculate:", JSON.stringify(answersArray));

     // Só envia se houver alguma resposta
     if (answersArray.length > 0) {
         sendAnswersAndRedirect(answersArray);
     } else {
         console.warn("finishAssessment: Nenhuma resposta completa registrada para enviar.");
         const currentOverlay = document.getElementById('loading-overlay');
         if (currentOverlay) {
            currentOverlay.style.opacity = '0';
            setTimeout(() => currentOverlay.style.display = 'none', 300); // Esconde após fade-out
         }
         alert("Nenhuma resposta foi registrada. Por favor, tente refazer a avaliação.");
         // Reabilita o botão se houve falha antes do envio
         if(viewResultsBtn) {
            viewResultsBtn.disabled = false;
            viewResultsBtn.textContent = "Ver Meus Resultados";
         }
     }
}

// Função assíncrona para enviar os dados e tratar a resposta
async function sendAnswersAndRedirect(answers) {
    const overlay = document.getElementById('loading-overlay');
    console.log("sendAnswersAndRedirect: Tentando POST para /api/calculate");
    try {
        const response = await fetch('/api/calculate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                // Adicionar CSRF token se implementado no backend
            },
            body: JSON.stringify({ answers: answers }) // Envia no corpo como esperado pela API Flask
        });

        console.log(`sendAnswersAndRedirect: Resposta recebida do servidor, status: ${response.status}`);

        if (!response.ok) {
            // Tenta ler a mensagem de erro do corpo da resposta, se houver
            let errorBody = "Nenhum detalhe adicional.";
            try {
                errorBody = await response.text(); // Tenta ler como texto primeiro
            } catch (e) { /* Ignora se não conseguir ler o corpo */ }
            console.error(`sendAnswersAndRedirect: Erro HTTP ${response.status}. Corpo: ${errorBody}`);
            throw new Error(`Erro do Servidor: ${response.status} ${response.statusText}. Detalhes: ${errorBody}`);
        }

        // Processa a resposta JSON
        const result = await response.json();
        console.log("sendAnswersAndRedirect: Resposta JSON recebida:", result);

        if (result.success) {
            console.log("sendAnswersAndRedirect: Sucesso retornado pelo backend. Redirecionando para /results...");
            // Redireciona para a página de resultados
            window.location.href = '/results';
            // O overlay desaparecerá com o carregamento da nova página
        } else {
             // O backend indicou uma falha, mas a requisição HTTP foi OK (status 200)
             console.error("sendAnswersAndRedirect: Backend retornou success=false. Erro:", result.error || "Erro não especificado pelo servidor.");
            throw new Error(result.error || 'Ocorreu um erro no processamento do lado do servidor.');
        }

    } catch (error) {
        // Captura erros de rede ou erros lançados acima
        console.error('sendAnswersAndRedirect: Falha ao enviar ou processar respostas:', error);

        // Esconde o overlay em caso de erro
        if (overlay) {
            overlay.style.opacity = '0';
            setTimeout(() => overlay.style.display = 'none', 300);
        }
        // Mostra mensagem de erro para o usuário
        alert(`Houve um problema ao enviar ou processar suas respostas:\n\n${error.message}\n\nPor favor, verifique sua conexão e tente novamente.`);

        // Reabilita o botão para permitir nova tentativa
        if(viewResultsBtn) {
            viewResultsBtn.disabled = false;
            viewResultsBtn.textContent = "Ver Meus Resultados";
        }
    }
}

// --- Event Listener Inicial ---
document.addEventListener('DOMContentLoaded', async () => {
    console.log("DOMContentLoaded: Evento disparado - v1.1.0");

    // Tenta buscar as questões assim que o DOM estiver pronto
    const questionsLoaded = await fetchQuestions();

    if (questionsLoaded) {
        // Se as questões carregaram, verifica se estamos na página do quiz para iniciá-lo
        if (assessmentSection) {
            console.log("DOMContentLoaded: Questões carregadas e seção de avaliação encontrada. Iniciando o quiz...");
            startAssessment();
        } else if (document.getElementById('results')) {
             console.log("DOMContentLoaded: Página de resultados carregada.");
             // Lógica específica para a página de resultados (se houver) pode ir aqui
             // Ex: buscar dados do gráfico se não vierem do template
        } else {
             console.log("DOMContentLoaded: Questões carregadas, mas não está na página do quiz ou resultados.");
        }
    } else {
        // Se as questões não carregaram, uma mensagem de erro já foi exibida por fetchQuestions
        console.error("DOMContentLoaded: Falha ao carregar questões. O quiz não pode iniciar.");
        // Poderia desabilitar botões ou mostrar um erro mais proeminente
    }

    // Listener para o botão de nova avaliação (na página de resultados)
    const newAssessmentBtn = document.getElementById('new-assessment');
    if (newAssessmentBtn) {
         newAssessmentBtn.addEventListener('click', () => {
             console.log("Botão 'Nova Avaliação' clicado. Redirecionando para /quiz");
             window.location.href = '/quiz'; // Redireciona para iniciar um novo quiz
         });
    }

    console.log("DOMContentLoaded: Setup inicial concluído.");
});