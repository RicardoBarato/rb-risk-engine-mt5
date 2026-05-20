# Especificacao Inicial do Robo MT5

## Objetivo

Criar um Expert Advisor para MT5 que replique a parte disciplinada do metodo de scalping e bloqueie a parte caotica.

## Escopo da versao inicial

Esta versao deve priorizar preservacao e coleta de dados:

- operar somente XAUUSD por padrao;
- ter janelas de horario configuraveis;
- controlar drawdown por sessao;
- controlar perda diaria;
- limitar quantidade de trades por bloco;
- permitir modo runner sem tempo maximo de posicao;
- travar lucro apos meta;
- registrar eventos de bloqueio;
- manter o gatilho de entrada separado do motor de risco.

## Estados do robo

- `IDLE`: fora de horario ou aguardando sinal.
- `TECHNIQUE_READY`: mercado dentro dos filtros basicos.
- `IN_POSITION`: existe posicao aberta pelo robo.
- `COOLDOWN`: pausa apos perda, sequencia ruim ou fechamento recente.
- `LOCKED`: sessao encerrada por meta, perda maxima ou regra de caos.

## Filtros obrigatorios

1. Simbolo permitido.
2. Horario permitido.
3. Spread maximo.
4. Lote dentro do limite.
5. Drawdown de sessao abaixo do limite.
6. Drawdown diario abaixo do limite.
7. Sequencia de perdas abaixo do limite.
8. Numero de trades por sessao abaixo do limite.
9. Tempo desde ultima entrada acima do minimo.

## Motor anti-caos

O robo deve bloquear novas entradas quando qualquer condicao ocorrer:

- perda de sessao maior que limite;
- perda diaria maior que limite;
- lucro de sessao devolvido alem do limite;
- muitas perdas consecutivas;
- stop rapido demais, indicando serrote/sweep contra a tecnica;
- muitas entradas em pouco tempo sem progresso;
- spread acima do permitido;
- posicao excedeu tempo maximo de scalp.

## Motor de tecnica

O gatilho atual combina:

- rompimento com corpo forte;
- continuacao no mesmo sentido com filtro de tendencia no M1;
- confluencia frouxa de M5, M15 e H1;
- bloqueio quando dois tempos maiores estao claramente contra;
- opcoes desligadas no preset: reteste do rompimento e W/M no M1.

## Preset atual testado

- ativo: `XAUUSD`;
- timeframe: `M1`;
- janela de entrada: 03h ate 06h no horario do servidor;
- lado: compra apenas;
- stop: 500 pontos;
- alvo: 2400 pontos;
- tempo maximo em posicao: 0, ou seja, runner sem corte por tempo;
- maximo de trades por sessao: 40;
- pausa apos perda: 180 segundos;
- maximo de perdas consecutivas: 3;
- cooldown longo apos sequencia: 900 segundos;
- trava apos perda rapida: ativa, com limite de 120 segundos;
- confluencia MTF: ativa;
- minimo MTF alinhado: 1;
- reteste do rompimento: disponivel, mas desligado no preset atual;
- W/M no M1: disponivel, mas desligado no preset atual;
- filtro H1 estrito: disponivel, mas desligado no preset atual.

Esses valores devem ser calibrados no Strategy Tester, nao fixados como verdade.
