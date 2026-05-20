# Experimentos

Resumo das primeiras iteracoes automatizadas no Strategy Tester.

Periodo testado:

- XAUUSD, M1
- 2026.02.18 a 2026.02.20
- Deposito inicial: 1000 USD

## Rodadas principais

| Rodada | Ideia | Resultado |
| --- | --- | --- |
| 20260520-115909 | Primeiro gatilho M1, horario amplo, TP 350, SL 250 | 867.90 |
| 20260520-120006 | Compra apenas, cooldown em vez de trava diaria, TP 350, SL 250 | 939.20 |
| 20260520-120159 | Parametros via `.set`, horario 03-06, TP 350, SL 250 | 1050.30 |
| 20260520-120259 | Mesmo filtro, TP 600, SL 250 | 1144.80 |
| 20260520-120353 | Mesmo filtro, TP 900, SL 250 | 1174.10 |
| 20260520-120446 | Mesmo filtro, TP 1200, SL 250 | 1253.90 |
| 20260520-120549 | Mesmo filtro, TP 1500, SL 250 | 1224.30 |
| 20260520-120702 | Modo runner, TP 2400, SL 500 | 1620.00 |
| 20260520-120842 | Modo runner validado, TP 2400, SL 500 | 1620.00 |
| 20260520-123758 | Stress 2026.02.02-2026.02.05, TP 2400, SL 500 | 925.50 |
| 20260520-123903 | Stress 2025.10.10-2025.10.17, TP 2400, SL 500 | 1649.40 |

## Filtros anti-caos testados

| Rodada | Ideia | Periodo | Resultado | Leitura |
| --- | --- | --- | --- | --- |
| 20260520-130852 | Filtro H1 estrito | 2026.02.18-2026.02.20 | 1190.30 | Ficou conservador demais e cortou trades bons. |
| 20260520-130931 | Filtro H1 estrito | 2026.02.02-2026.02.05 | 1128.50 | Melhorou o periodo ruim. |
| 20260520-130958 | Filtro H1 estrito | 2025.10.10-2025.10.17 | 1799.50 | Melhorou o stress de outubro. |
| 20260520-131259 | H1 bloqueando apenas contra-tendencia | 2025.10.10-2025.10.17 | 1699.40 | Melhor que base, mas ainda cortou o periodo bom. |
| 20260520-131524 | Cooldown longo apos 2 perdas | 2026.02.02-2026.02.05 | 826.50 | Piorou: o cooldown empurrou entradas para novos sinais ruins. |
| 20260520-131735 | Encerrar novas entradas as 05h | 2026.02.18-2026.02.20 | 1670.30 | Melhorou o periodo bom ao remover uma perda tardia. |
| 20260520-131825 | Encerrar novas entradas as 05h | 2025.10.10-2025.10.17 | 1509.20 | Ainda positivo, mas pior que manter a janela ate 06h. |
| 20260520-132217 | Trava apos perda rapida de ate 120s | 2026.02.02-2026.02.05 | 1089.60 | Virou o periodo ruim para positivo com apenas 4 trades. |
| 20260520-132328 | Trava apos perda rapida de ate 120s | 2025.10.10-2025.10.17 | 1649.40 | Preservou o resultado base de outubro. |
| 20260520-132506 | Validacao final do preset atual | 2026.02.18-2026.02.20 | 1620.00 | Preservou o periodo bom. |

## Convergencia de tempos e leitura do XAU

Hipotese manual adicionada: olhar M1, M5, M15 e H1 juntos. Um W no M1 pode ser a primeira perna do M5. O XAU tambem costuma romper e voltar bastante, entao a entrada no rompimento puro pode ficar dificil.

| Rodada | Ideia | Periodo | Resultado | Leitura |
| --- | --- | --- | --- | --- |
| 20260520-120646 | MTF M5/M15/H1 exigindo 2 tempos alinhados | 2026.02.18-2026.02.20 | 1379.90 | Cortou lucro demais. |
| 20260520-120715 | MTF M5/M15/H1 exigindo 2 tempos alinhados | 2026.02.02-2026.02.05 | 1139.80 | Filtrou bem o periodo ruim. |
| 20260520-121313 | MTF frouxo: basta 1 alinhado e bloqueia 2 contra | 2026.02.18-2026.02.20 | 1619.80 | Preservou o periodo bom. |
| 20260520-120825 | MTF frouxo: basta 1 alinhado e bloqueia 2 contra | 2026.02.02-2026.02.05 | 1139.80 | Melhorou o filtro de perda rapida. |
| 20260520-120852 | MTF frouxo: basta 1 alinhado e bloqueia 2 contra | 2025.10.10-2025.10.17 | 1699.50 | Melhorou outubro sem matar frequencia. |
| 20260520-120933 | Reteste apos rompimento + MTF frouxo | 2026.02.18-2026.02.20 | 1670.10 | Excelente no periodo bom. |
| 20260520-121004 | Reteste apos rompimento + MTF frouxo | 2026.02.02-2026.02.05 | 1089.20 | Pior que MTF frouxo sem reteste. |
| 20260520-121030 | Reteste apos rompimento + MTF frouxo | 2025.10.10-2025.10.17 | 1457.30 | Perdeu entradas de continuacao. |
| 20260520-121224 | W/M1 complementar + MTF frouxo | 2025.10.10-2025.10.17 | 1649.00 | Ficou abaixo do MTF frouxo puro. |

## Leitura

O resultado melhorou quando o robo parou de cortar o ganho cedo. Isso combina com a leitura dos relatorios manuais: a tecnica aceita alguns stops pequenos/medios para capturar poucos movimentos grandes.

O teste em 2026.02.02-2026.02.05 mostrou que ainda existe regime ruim: 13 trades, 2 ganhos, 11 perdas, saldo 925.50. Ja o teste em 2025.10.10-2025.10.17 ficou positivo, com 16 trades, 5 ganhos, 11 perdas, saldo 1649.40.

O melhor conjunto ate aqui e: modo runner, trava por perda rapida e MTF frouxo. A regra MTF nao exige que todos os tempos estejam perfeitos; ela aceita pelo menos um tempo alinhado e bloqueia quando dois tempos maiores estao claramente contra.

O reteste do rompimento capturou melhor o periodo campeao, mas piorou outubro. Isso sugere que o XAU realmente volta bastante, mas nem todo movimento bom permite esperar o reteste.

O proximo foco nao deve ser aumentar frequencia. Deve ser:

1. preservar o modo runner;
2. validar MTF frouxo + perda rapida em mais tardes;
3. testar o mesmo setup em mais periodos;
4. estudar quando usar reteste e quando aceitar continuacao direta.
