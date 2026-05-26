# Security Audit Report

## Status geral

Atencao: historico publico limpo preparado localmente; `force push` ainda pendente de aprovacao final.

O estado publico sanitizado foi preservado em uma branch orfa local. O objetivo e substituir o historico publico antigo por uma base limpa contendo apenas os arquivos educacionais atuais.

## Metodo selecionado

Metodo usado: criacao de historico limpo com branch orfa.

Ferramentas nao usadas nesta etapa:

- `git-filter-repo`
- BFG Repo-Cleaner

Motivo: para este caso, a opcao mais defensavel e manter apenas o estado publico atual como novo ponto inicial do repositorio. Isso evita tentar preservar partes seletivas de commits antigos que continham pesquisa privada.

## Backup antes da limpeza

Backup local/offline criado antes da reescrita local:

- `rb-risk-engine-mt5-backups/pre-history-clean-20260525-215346/rb-risk-engine-mt5-pre-clean-all.bundle`

Metadados preservados no mesmo diretorio:

- `status-before-clean.txt`
- `log-before-clean.txt`
- `remote-refs-before-clean.txt`
- `tracked-files-before-clean.txt`
- `ignored-files-before-clean.txt`

## Escopo analisado

- Arquivos rastreados atuais.
- Arquivos ignorados locais.
- Historico Git antigo.
- Branches locais e remotas.
- Tags.
- Pull requests.
- Arquivos de configuracao.
- Presets MT5.
- Relatorios e documentos de backtest.
- Pastas de runtime.

## Ferramentas usadas

- `git status --short --branch`
- `git remote -v`
- `git branch -a`
- `git tag --list`
- `git log --all --decorate --oneline --graph`
- `git ls-files`
- `git log --all --name-status`
- `git grep` over all revisions
- `rg` over current files and ignored files
- `gh pr list`
- `gh pr view`
- `gh issue list`
- `git ls-remote --heads --tags origin`

Ferramentas nao instaladas ou nao disponiveis no PATH:

- `gitleaks`
- `trufflehog`
- `git-secrets`

## Artefatos privados encontrados no historico antigo

### 1. Presets reais de MT5

- Tipo: parametros estrategicos / arquivos `.set`.
- Arquivo: `config/*.set`.
- Esta no estado publico atual? Nao, exceto exemplo ficticio em `examples/`.
- Esta no historico antigo? Sim.
- Risco: alto para confidencialidade estrategica.
- Acao: remover do historico publico por substituicao de historico limpo.

### 2. Relatorios privados de pesquisa e backtest

- Tipo: resultados de backtest, robustez, alavancagem, presets e pesquisa.
- Arquivo: documentos antigos em `docs/`.
- Esta no estado publico atual? Nao.
- Esta no historico antigo? Sim.
- Risco: medio a alto para confidencialidade de pesquisa.
- Acao: manter apenas documentacao publica educacional.

### 3. Codigo antigo de estrategia privada

- Tipo: codigo MQL5 com logica estrategica anterior.
- Arquivo: caminhos legados de Expert Advisor.
- Esta no estado publico atual? Nao.
- Esta no historico antigo? Sim.
- Risco: alto para propriedade intelectual.
- Acao: preservar apenas `MQL5/Experts/RBRiskEngine/RBRiskEngine_Public.mq5`.

### 4. Referencias locais e de ambiente

- Tipo: caminhos locais, nomes de terminal/corretora e referencias operacionais.
- Esta no estado publico atual? Sanitizado.
- Esta no historico antigo? Sim.
- Risco: baixo a medio.
- Acao: substituir por exemplos genericos.

### 5. Exports e arquivos locais ignorados

- Tipo: planilhas, relatorios locais e pastas de execucao.
- Esta no estado publico atual? Nao rastreado e ignorado.
- Esta no historico antigo? As planilhas locais inspecionadas nao estavam rastreadas no historico Git analisado.
- Risco: alto se forem publicados por acidente.
- Acao: manter fora do Git e mover para armazenamento privado quando necessario.

## Credenciais

Nao houve indicacao de senha, token, API key, chave privada ou credencial de broker no estado publico rastreado.

Mesmo assim, o historico antigo continha artefatos sensiveis de estrategia e pesquisa. A limpeza e motivada por confidencialidade tecnica e propriedade intelectual, nao por emergencia de credencial.

## Arquivos preservados na historia publica limpa

- `.gitignore`
- `AGENTS.md`
- `CHANGELOG.md`
- `README.md`
- `SECURITY.md`
- `SECURITY_AUDIT_REPORT.md`
- `config/example-config.md`
- `config/mt5.local.example.ps1`
- `docs/`
- `examples/`
- `MQL5/Experts/RBRiskEngine/RBRiskEngine_Public.mq5`
- `tools/` publicos seguros

## Arquivos e categorias removidos do historico publico

- Presets reais `.set` fora de `examples/`.
- Relatorios reais ou privados de backtest.
- Documentos antigos com resultados, parametros e evolucao estrategica sensivel.
- Codigo antigo de estrategia privada.
- Exports e artefatos operacionais de corretora.
- Referencias locais antigas que nao sao necessarias para o portfolio publico.

## Validacao antes da reescrita local

- Working tree em `main`: limpo antes da operacao.
- Backup local/offline: criado.
- Compilacao MQL5: `0 errors, 0 warnings`.
- `py_compile` dos scripts Python publicos: aprovado.
- Nenhuma licenca foi adicionada.
- Nenhuma release foi criada.

## Validacao da historia limpa local

- Branch local: `public-clean-history`.
- Historico da branch: um commit raiz limpo.
- Arvore rastreada: apenas arquivos publicos educacionais.
- Busca por nomes antigos de presets, relatorios, planilhas, EA privado e termos operacionais: sem achados na arvore rastreada.
- Arquivos privados locais continuam ignorados e nao rastreados.
- `force push` remoto ainda pendente de aprovacao final.

## Force push

Nao executado ainda.

Comando planejado, caso aprovado:

```powershell
git push --force-with-lease origin public-clean-history:main
```

## Riscos remanescentes

- Reescrever o historico do repositorio principal nao apaga forks, clones, caches externos ou copias ja feitas por terceiros.
- Arquivos privados ignorados ainda podem existir localmente na maquina e devem continuar fora do Git.
- O `force push` altera a base historica do repositorio publico; colaboradores precisarao reclonar ou realinhar seus clones locais.

## Recomendacao final

Usar a branch orfa limpa como novo `main` publico apos aprovacao final do `force push`.

Depois do envio, repetir a busca sensivel no estado remoto e confirmar que o GitHub mostra apenas a versao publica limpa.
