const discQuestions = [
    {
        id: 1,
        options: [
            { id: "A", text: "DETERMINADO" },
            { id: "B", text: "CONFIANTE" },
            { id: "C", text: "CONSISTENTE" },
            { id: "D", text: "PRECISO" }
        ]
    },
    {
        id: 2,
        options: [
            { id: "A", text: "APRESSADO" },
            { id: "B", text: "PERSUASIVO" },
            { id: "C", text: "METÓDICO" },
            { id: "D", text: "CUIDADOSO" }
        ]
    },
    {
        id: 3,
        options: [
            { id: "A", text: "COMPETITIVO" },
            { id: "B", text: "POLÍTICO" },
            { id: "C", text: "COOPERATIVO" },
            { id: "D", text: "DIPLOMATA" }
        ]
    },
    {
        id: 4,
        options: [
            { id: "A", text: "OBJETIVO" },
            { id: "B", text: "EXAGERADO" },
            { id: "C", text: "ESTÁVEL" },
            { id: "D", text: "EXATO" }
        ]
    } // Removidas as questões 5 a 25
];

// Mapeamento de letras para fatores DISC (Mantido)
const discMapping = {
    'A': 'D', // Dominância
    'B': 'I', // Influência
    'C': 'S', // Estabilidade
    'D': 'C'  // Conformidade
};

// Exportar os dados para uso em outros arquivos (Mantido)
// Esta linha garante que 'disc_quiz.js' (ou outro script) possa importar estas questões.
// O método de exportação pode variar dependendo se você está usando módulos ES6 ou CommonJS.
// Se o seu 'disc_quiz.js' simplesmente assume que 'discQuestions' é uma variável global,
// esta parte pode não ser estritamente necessária nesse contexto, mas é boa prática.
if (typeof module !== 'undefined' && typeof module.exports !== 'undefined') {
    // Para ambientes Node.js/CommonJS (menos provável no JS do navegador diretamente)
    module.exports = { discQuestions, discMapping };
} else {
    // Deixa 'discQuestions' e 'discMapping' como variáveis globais se não estiver usando módulos
    // (Comum em scripts simples incluídos diretamente no HTML)
}