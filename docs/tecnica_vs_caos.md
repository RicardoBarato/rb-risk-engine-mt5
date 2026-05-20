# Tecnica vs Caos

Este documento resume a primeira leitura dos relatorios de performance. A ideia e transformar comportamento manual em regras para um robo MT5.

## Hipotese central

O metodo tem capacidade de multiplicar a conta quando o mercado entra em regime favoravel, principalmente em XAUUSD. O problema nao parece ser falta de edge em todos os momentos. O problema parece ser continuar em modo agressivo quando o regime deixa de favorecer a leitura.

Assim, o robo deve ter dois motores:

- motor de tecnica: identifica quando pode operar e acelerar;
- motor anti-caos: reduz, pausa ou bloqueia quando o padrao vira drawdown.

## O que apareceu no recorte vencedor

Arquivo `dddd.xlsx`:

- Ativo unico: XAUUSD.
- Operacoes muito curtas: mediana perto de 1 minuto.
- Maioria fechada em ate 5 minutos.
- Forte concentracao em blocos de operacao.
- Vies comprador dominante, com vendas bem mais seletivas.
- Horarios com desempenho muito diferente.
- Lucro alto veio de poucos blocos, nao de distribuicao uniforme ao longo do dia.

## O que apareceu no historico maior

Arquivo `ReportHistory-55749699.xlsx`:

- Muitos ativos e horarios misturados.
- Existem blocos excelentes, mas tambem blocos destrutivos.
- O resultado agregado piora quando o metodo fica disperso.
- O drawdown cresce quando a agressividade permanece ativa depois que o mercado muda.
- Sessoes ruins tem muitas entradas agrupadas e perdas grandes em sequencia.

## Regras candidatas para excluir caos

1. Operar inicialmente apenas XAUUSD.
2. Permitir trades apenas em janelas de horario estatisticamente favoraveis.
3. Encerrar a sessao quando o drawdown do bloco atingir limite fixo ou percentual.
4. Encerrar a sessao depois de uma sequencia curta de perdas.
5. Reduzir lote apos perda relevante.
6. Bloquear aumento de lote quando a conta acabou de fazer novo pico.
7. Fechar operacao que passar do tempo maximo esperado para scalping.
8. Parar depois de meta de ganho de sessao e preservar lucro.
9. Bloquear entradas quando spread/volatilidade estiverem fora do padrao.
10. Nao permitir muitos trades no mesmo lado se o preco nao confirmou deslocamento.
11. Bloquear o restante da sessao quando um stop acontece rapido demais.

## Descoberta atual

O filtro mais promissor isolado nao foi o H1 estrito. O H1 ajudou nos estresses, mas tambem cortou trades bons demais.

A melhor leitura de caos apareceu na duracao da perda: quando o stop vem em poucos segundos, o mercado provavelmente esta em serrote/sweep contra a tecnica. O robo agora pode bloquear novas entradas ate o proximo dia quando uma perda fecha em ate 120 segundos.

Nos testes atuais, essa trava preservou o periodo bom de 2026.02.18-2026.02.20 em 1620.00, preservou outubro em 1649.40 e melhorou o stress de 2026.02.02-2026.02.05 de 925.50 para 1089.60.

A leitura manual de convergencia entre M1, M5, M15 e H1 virou um filtro MTF frouxo: o robo aceita pelo menos um tempo maior alinhado, mas bloqueia quando dois tempos maiores estao claramente contra. Esse formato preservou o periodo bom em 1619.80, melhorou fevereiro para 1139.80 e outubro para 1699.50.

O retorno do XAU apos rompimento tambem foi testado como entrada por reteste. Funcionou muito bem no periodo campeao, chegando a 1670.10, mas piorou outubro para 1457.30. Por enquanto fica como ferramenta opcional, nao como preset principal.

## Regime favoravel a procurar no grafico

Os melhores blocos sugerem uma leitura de fluxo/expansao:

- preco deslocando rapido;
- entrada repetida no mesmo sentido;
- perdas pequenas quando a leitura erra;
- ganhos maiores quando o movimento continua;
- saidas rapidas;
- possibilidade de piramidar ou reentrar enquanto o fluxo segue.

## Regime perigoso

Os piores blocos sugerem:

- insistencia no mesmo sentido em mercado que ja virou;
- muitas entradas proximas;
- perda grande isolada ou sequencia curta de perdas;
- tentativa de recuperar em ambiente de serrote;
- operacao aberta tempo demais para um scalp.

## Proxima validacao

Para descobrir o gatilho real da entrada, cruzar os horarios dos melhores e piores blocos com candles/ticks de XAUUSD. A planilha mostra o comportamento. O grafico mostra o motivo.
