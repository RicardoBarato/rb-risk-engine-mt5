//+------------------------------------------------------------------+
//|                                          RBRiskEngine_Public.mq5  |
//| Educational MT5 Expert Advisor scaffold for risk-managed testing. |
//| This public file intentionally omits private strategy logic.      |
//+------------------------------------------------------------------+
#property strict
#property version "1.00"

#include <Trade/Trade.mqh>

CTrade trade;

input string InpAllowedSymbol = "XAUUSD";
input bool   InpEnableLiveOrders = false;
input bool   InpEnableTesterOrders = true;
input int    InpMagicNumber = 100001;
input double InpRiskPercent = 0.25;
input int    InpMaxSpreadPoints = 50;
input int    InpDeviationPoints = 20;

input bool   InpUseSessionFilter = true;
input int    InpSessionStartHour = 8;
input int    InpSessionEndHour = 16;

input int    InpFastEmaPeriod = 20;
input int    InpSlowEmaPeriod = 50;
input int    InpAtrPeriod = 14;
input double InpAtrStopMult = 1.5;
input double InpTakeProfitR = 2.0;
input bool   InpTradeOnNewBarOnly = true;

int fast_ema_handle = INVALID_HANDLE;
int slow_ema_handle = INVALID_HANDLE;
int atr_handle = INVALID_HANDLE;
datetime last_bar_time = 0;

bool IsTester()
{
   return (bool)MQLInfoInteger(MQL_TESTER);
}

bool IsAllowedEnvironment()
{
   if(_Symbol != InpAllowedSymbol)
      return false;

   if(IsTester())
      return InpEnableTesterOrders;

   return InpEnableLiveOrders;
}

bool IsSessionAllowed()
{
   if(!InpUseSessionFilter)
      return true;

   MqlDateTime now;
   TimeToStruct(TimeCurrent(), now);

   if(InpSessionStartHour <= InpSessionEndHour)
      return now.hour >= InpSessionStartHour && now.hour < InpSessionEndHour;

   return now.hour >= InpSessionStartHour || now.hour < InpSessionEndHour;
}

bool IsSpreadAllowed()
{
   long spread = SymbolInfoInteger(_Symbol, SYMBOL_SPREAD);
   return spread > 0 && spread <= InpMaxSpreadPoints;
}

bool HasOpenPosition()
{
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      ulong ticket = PositionGetTicket(i);
      if(ticket == 0)
         continue;

      if(PositionGetString(POSITION_SYMBOL) == _Symbol &&
         (int)PositionGetInteger(POSITION_MAGIC) == InpMagicNumber)
         return true;
   }

   return false;
}

double NormalizeVolume(double volume)
{
   double min_volume = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
   double max_volume = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
   double step = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);

   if(step <= 0.0)
      return 0.0;

   volume = MathMax(min_volume, MathMin(max_volume, volume));
   volume = MathFloor(volume / step) * step;
   return NormalizeDouble(volume, 2);
}

double CalculateRiskVolume(double stop_distance)
{
   double equity = AccountInfoDouble(ACCOUNT_EQUITY);
   double risk_money = equity * InpRiskPercent / 100.0;
   double tick_size = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
   double tick_value = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);

   if(risk_money <= 0.0 || stop_distance <= 0.0 || tick_size <= 0.0 || tick_value <= 0.0)
      return 0.0;

   double risk_per_lot = (stop_distance / tick_size) * tick_value;
   if(risk_per_lot <= 0.0)
      return 0.0;

   return NormalizeVolume(risk_money / risk_per_lot);
}

bool LoadIndicators(double &fast_current, double &fast_previous,
                    double &slow_current, double &slow_previous,
                    double &atr_value)
{
   double fast_buffer[];
   double slow_buffer[];
   double atr_buffer[];

   ArrayResize(fast_buffer, 2);
   ArrayResize(slow_buffer, 2);
   ArrayResize(atr_buffer, 1);

   ArraySetAsSeries(fast_buffer, true);
   ArraySetAsSeries(slow_buffer, true);
   ArraySetAsSeries(atr_buffer, true);

   if(CopyBuffer(fast_ema_handle, 0, 1, 2, fast_buffer) != 2)
      return false;
   if(CopyBuffer(slow_ema_handle, 0, 1, 2, slow_buffer) != 2)
      return false;
   if(CopyBuffer(atr_handle, 0, 1, 1, atr_buffer) != 1)
      return false;

   fast_current = fast_buffer[0];
   fast_previous = fast_buffer[1];
   slow_current = slow_buffer[0];
   slow_previous = slow_buffer[1];
   atr_value = atr_buffer[0];
   return true;
}

void TryOpenPosition()
{
   if(!IsAllowedEnvironment() || !IsSessionAllowed() || !IsSpreadAllowed() || HasOpenPosition())
      return;

   double fast_current, fast_previous, slow_current, slow_previous, atr_value;
   if(!LoadIndicators(fast_current, fast_previous, slow_current, slow_previous, atr_value))
      return;

   bool buy_signal = fast_previous <= slow_previous && fast_current > slow_current;
   bool sell_signal = fast_previous >= slow_previous && fast_current < slow_current;

   if(!buy_signal && !sell_signal)
      return;

   double stop_distance = atr_value * InpAtrStopMult;
   double volume = CalculateRiskVolume(stop_distance);
   if(volume <= 0.0)
      return;

   int digits = (int)SymbolInfoInteger(_Symbol, SYMBOL_DIGITS);
   trade.SetExpertMagicNumber(InpMagicNumber);
   trade.SetDeviationInPoints(InpDeviationPoints);

   if(buy_signal)
   {
      double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
      double sl = NormalizeDouble(ask - stop_distance, digits);
      double tp = NormalizeDouble(ask + stop_distance * InpTakeProfitR, digits);
      trade.Buy(volume, _Symbol, ask, sl, tp, "public-risk-engine-demo");
      return;
   }

   if(sell_signal)
   {
      double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
      double sl = NormalizeDouble(bid + stop_distance, digits);
      double tp = NormalizeDouble(bid - stop_distance * InpTakeProfitR, digits);
      trade.Sell(volume, _Symbol, bid, sl, tp, "public-risk-engine-demo");
   }
}

int OnInit()
{
   fast_ema_handle = iMA(_Symbol, PERIOD_CURRENT, InpFastEmaPeriod, 0, MODE_EMA, PRICE_CLOSE);
   slow_ema_handle = iMA(_Symbol, PERIOD_CURRENT, InpSlowEmaPeriod, 0, MODE_EMA, PRICE_CLOSE);
   atr_handle = iATR(_Symbol, PERIOD_CURRENT, InpAtrPeriod);

   if(fast_ema_handle == INVALID_HANDLE || slow_ema_handle == INVALID_HANDLE || atr_handle == INVALID_HANDLE)
      return INIT_FAILED;

   return INIT_SUCCEEDED;
}

void OnDeinit(const int reason)
{
   if(fast_ema_handle != INVALID_HANDLE)
      IndicatorRelease(fast_ema_handle);
   if(slow_ema_handle != INVALID_HANDLE)
      IndicatorRelease(slow_ema_handle);
   if(atr_handle != INVALID_HANDLE)
      IndicatorRelease(atr_handle);
}

void OnTick()
{
   if(InpTradeOnNewBarOnly)
   {
      datetime bar_time = iTime(_Symbol, PERIOD_CURRENT, 0);
      if(bar_time == last_bar_time)
         return;
      last_bar_time = bar_time;
   }

   TryOpenPosition();
}
