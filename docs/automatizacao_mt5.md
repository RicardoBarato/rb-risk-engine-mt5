# Automacao do Ciclo MT5

Objetivo: reduzir o ciclo manual para poucos comandos.

## Ciclo desejado

1. Editar o EA no repositorio.
2. Copiar o EA para a pasta de dados correta do MT5.
3. Compilar com o MetaEditor.
4. Rodar backtest pelo terminal com um arquivo `.ini`.
5. Guardar relatorio em `runs/`.
6. Comparar o resultado com os relatorios anteriores.

## Caminhos detectados neste computador

Instalacao escolhida por padrao:

```text
C:\Program Files\Tickmill MT5 Terminal - Scalper
```

Pasta de dados correspondente:

```text
%APPDATA%\MetaQuotes\Terminal\A2DC375E49C302D35C48D5B640ECC12B
```

Se quiser fixar manualmente, copie:

```powershell
Copy-Item config\mt5.local.example.ps1 config\mt5.local.ps1
```

Depois ajuste `config\mt5.local.ps1` se necessario. Esse arquivo fica fora do GitHub.

## Compilar o robo

```powershell
powershell -ExecutionPolicy Bypass -File tools\mt5_compile.ps1
```

O script copia:

```text
MQL5\Experts\RoboScalper\RoboScalper.mq5
```

para a pasta `MQL5\Experts\RoboScalper` do terminal escolhido e compila via `MetaEditor64.exe`.

## Rodar backtest

```powershell
powershell -ExecutionPolicy Bypass -File tools\mt5_backtest.ps1 -CompileFirst
```

Parametros uteis:

```powershell
powershell -ExecutionPolicy Bypass -File tools\mt5_backtest.ps1 `
  -Symbol XAUUSD `
  -Period M1 `
  -FromDate 2026.02.18 `
  -ToDate 2026.02.20 `
  -Deposit 1000 `
  -Leverage 1:500 `
  -CompileFirst
```

Os arquivos da rodada ficam em `runs/`.

Se o terminal nao estiver logado em uma conta valida, o backtest pode nao sincronizar simbolos/historico. O caminho mais seguro e abrir o `Tickmill MT5 Terminal - Scalper` uma vez, fazer login na conta correta e fechar o terminal.

Tambem da para passar login pelo comando, mas evite colocar senha em arquivo versionado:

```powershell
powershell -ExecutionPolicy Bypass -File tools\mt5_backtest.ps1 `
  -Login 123456 `
  -Password "SENHA_AQUI" `
  -Server "Tickmill-Live" `
  -CompileFirst
```

## Observacao importante

O robo ja tem gatilho tecnico ativo e o fluxo automatizado esta medindo resultado real a cada iteracao. As rodadas ficam em `runs/`, com `.set`, `tester.ini`, logs do tester/agente/terminal e `summary.txt` para auditoria rapida.
