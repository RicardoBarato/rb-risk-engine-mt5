# Robo Scalper MT5

Projeto para transformar historicos reais de scalping em regras objetivas para um Expert Advisor no MetaTrader 5.

O foco inicial nao e "copiar todos os trades". O foco e separar:

- tecnica: momentos em que o metodo acelera a conta com boa assimetria;
- caos: momentos em que a mesma agressividade gera drawdown ruim;
- travas: regras que impedem o robo de continuar operando quando o regime ficou hostil.

## Estrutura

- `tools/analyze_mt5_reports.py`: le relatorios `.xlsx` exportados pelo MT5/Tickmill sem depender de pandas.
- `docs/analise_relatorios.md`: saida gerada com metricas, sessoes boas/ruins e hipoteses.
- `docs/tecnica_vs_caos.md`: leitura operacional do metodo.
- `docs/especificacao_robo_mt5.md`: especificacao inicial do EA.
- `docs/automatizacao_mt5.md`: ciclo automatizado de compilacao/backtest no MT5.
- `MQL5/Experts/RoboScalper/RoboScalper.mq5`: Expert Advisor com gatilho M1, modo runner e travas anti-caos.
- `tools/mt5_compile.ps1`: copia e compila o EA no MetaEditor.
- `tools/mt5_backtest.ps1`: dispara backtest via `terminal64.exe`.
- `config/RoboScalper.set`: parametros usados pelo Strategy Tester.

## Uso

```powershell
python tools/analyze_mt5_reports.py --output docs/analise_relatorios.md
```

```powershell
powershell -ExecutionPolicy Bypass -File tools\mt5_compile.ps1
```

```powershell
powershell -ExecutionPolicy Bypass -File tools\mt5_backtest.ps1 -CompileFirst
```

O EA continua seguro para uso manual: `InpEnableLiveOrders=false` por padrao. No Strategy Tester, o preset atual usa XAUUSD M1, compra apenas, TP/SL assimetrico, confluencia frouxa em M5/M15/H1 e trava a sessao quando uma perda fecha em ate 120 segundos.
