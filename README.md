# Sistema de Avaliação DISC Online

Um sistema completo para realização de avaliações comportamentais utilizando a metodologia DISC de William Moulton Marston.

## Visão Geral

O Sistema de Avaliação DISC Online permite que usuários realizem a avaliação DISC, que identifica tendências comportamentais em quatro áreas:

- **D - Dominância**: Relacionado à forma como lidamos com problemas e desafios.
- **I - Influência**: Relacionado à forma como lidamos com pessoas e influenciamos os outros.
- **S - Estabilidade**: Relacionado ao nosso ritmo de trabalho e consistência.
- **C - Conformidade**: Relacionado à forma como lidamos com procedimentos e restrições.

O sistema oferece uma interface intuitiva, questionário interativo, cálculo preciso de pontuação e relatórios detalhados.

## Funcionalidades

- Questionário DISC interativo com 24 perguntas
- Sistema de temporizador para cada questão (15 segundos)
- Algoritmo de pontuação preciso conforme metodologia DISC
- Visualização gráfica dos resultados
- Interpretação detalhada do perfil DISC
- Exportação de resultados em PDF
- Dashboard para visualizar estatísticas
- Sistema de autenticação seguro

## Requisitos Técnicos

- Python 3.12 ou superior
- Flask (backend)
- React (frontend, opcional)
- Banco de dados SQLite (produção pode usar PostgreSQL/MySQL)
- Bibliotecas Python conforme `requirements.txt`

## Estrutura do Projeto

```
sdisc/
│
├── .github/               # Configurações do GitHub
│   └── workflows/         # Workflows de CI/CD
│
├── app/                   # Aplicação principal
│   └── templates/         # Templates específicos da aplicação
│
├── backend/               # Backend Flask
│   ├── config/            # Configurações do backend
│   ├── data/              # Dados e assets
│   ├── models/            # Modelos de dados
│   ├── static/            # Arquivos estáticos (CSS, JS)
│   └── templates/         # Templates HTML
│
├── frontend/              # Frontend React (opcional)
│   ├── public/            # Assets públicos
│   └── src/               # Código fonte React
│
├── models/                # Modelos de dados compartilhados
│
├── scripts/               # Scripts de utilidade
│
├── static/                # Arquivos estáticos globais
│
├── templates/             # Templates HTML globais
│
├── tests/                 # Testes automatizados
│
├── venv/                  # Ambiente virtual Python
│
├── .gitignore             # Configuração Git
├── deploy.bat             # Script de deploy
├── README.md              # Este arquivo
├── requirements.txt       # Dependências Python
└── prod_config.py         # Configurações de produção
```

## Instalação e Execução

### Configuração Inicial

1. Clone o repositório:
   ```
   git clone https://github.com/seu-usuario/sdisc.git
   cd sdisc
   ```

2. Execute o script de deploy para configurar automaticamente:
   ```
   deploy.bat
   ```

3. Alternativamente, configure manualmente:
   ```
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

### Executar em Desenvolvimento

```
python -m backend.app
```

O sistema estará disponível em: http://127.0.0.1:5000

### Executar em Produção

1. Configure o arquivo `prod_config.py` com suas configurações de produção
2. Execute:
   ```
   python -m backend.app --prod
   ```

## Testes

Execute todos os testes:
```
python -m pytest
```

Ou testes específicos:
```
python -m pytest tests/test_app.py
python -m pytest tests/test_disc_scoring.py
python -m pytest tests/security_test.py
python -m pytest tests/integration_tests.py
```

## Segurança

O sistema implementa várias medidas de segurança:
- Proteção contra CSRF
- Sanitização de inputs
- Cabeçalhos de segurança
- Controle de sessão seguro
- Proteção contra ataques comuns (XSS, CSRF, SQL Injection)
- Dependabot para monitoramento de vulnerabilidades

## Contribuição

1. Faça um fork do projeto
2. Crie sua branch de feature (`git checkout -b feature/nome-da-feature`)
3. Commit suas alterações (`git commit -m 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nome-da-feature`)
5. Abra um Pull Request

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo LICENSE para detalhes.

## Agradecimentos

- William Moulton Marston pelo desenvolvimento da metodologia DISC
- Todos os colaboradores que contribuíram para este projeto
