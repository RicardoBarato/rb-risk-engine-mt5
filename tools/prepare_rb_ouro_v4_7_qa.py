from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "MQL5" / "Experts" / "RoboScalper" / "RB_Ouro_v4_4_Port.mq5"
DST = ROOT / "MQL5" / "Experts" / "RoboScalper" / "RB_Ouro_v4_7_QA.mq5"


def replace_once(text: str, old: str, new: str) -> str:
    if old not in text:
        raise RuntimeError(f"Pattern not found:\n{old[:500]}")
    return text.replace(old, new, 1)


def replace_all_checked(text: str, old: str, new: str, min_count: int = 1) -> str:
    count = text.count(old)
    if count < min_count:
        raise RuntimeError(f"Pattern found {count} times, expected at least {min_count}:\n{old[:500]}")
    return text.replace(old, new)


def main() -> None:
    text = SRC.read_text(encoding="utf-8-sig")

    text = text.replace("RB_Ouro_v4_4.mq5", "RB_Ouro_v4_7_QA.mq5")
    text = text.replace("v4.6: Quality/Trend Mode com regime macro e risco por equity", "v4.7 QA: filtros anti-repaint, magic guard e correcoes de SL")
    text = text.replace('#property version "4.60"', '#property version "4.70"')

    text = replace_once(
        text,
        'input int    InpMagicNumber = 55749699;\n',
        'input int    InpMagicNumber = 55749699;\n'
        'input bool   InpUseClosedBarSignals = false; // true = usa candle fechado nos sinais; false = comportamento original intrabar\n'
        'input double InpMarginSafetyFactor = 1.05;   // margem livre minima = margem requerida * fator\n',
    )

    text = replace_once(
        text,
        'double CalcLots(double sl_points, double risk_pct)\n{\n   if(sl_points<=0.0) return 0.0;\n   double equity=AccountInfoDouble(ACCOUNT_EQUITY);\n   double risk_money=equity*risk_pct;\n   double vpp=GetValuePerPoint();\n   if(vpp<=0.0) return 0.0;\n   return NormalizeLots(risk_money/(sl_points*vpp));\n}\n',
        'double CalcLots(double sl_points, double risk_pct)\n{\n   if(sl_points<=0.0) return 0.0;\n   double equity=AccountInfoDouble(ACCOUNT_EQUITY);\n   double risk_money=equity*risk_pct;\n   double vpp=GetValuePerPoint();\n   if(vpp<=0.0) return 0.0;\n   return NormalizeLots(risk_money/(sl_points*vpp));\n}\n\n'
        'int SignalShift()\n{\n   return InpUseClosedBarSignals ? 1 : 0;\n}\n\n'
        'double BarHigh(ENUM_TIMEFRAMES tf)\n{\n   return iHigh(_Symbol, tf, SignalShift());\n}\n\n'
        'double BarLow(ENUM_TIMEFRAMES tf)\n{\n   return iLow(_Symbol, tf, SignalShift());\n}\n\n'
        'double BarClose(ENUM_TIMEFRAMES tf)\n{\n   return iClose(_Symbol, tf, SignalShift());\n}\n\n'
        'bool MarginOK(ENUM_ORDER_TYPE order_type,double lots,double price)\n{\n   if(lots<=0.0) return false;\n\n   double margin_required=0.0;\n   if(!OrderCalcMargin(order_type,_Symbol,lots,price,margin_required))\n      return false;\n\n   double margin_free=AccountInfoDouble(ACCOUNT_MARGIN_FREE);\n   return (margin_free >= margin_required*InpMarginSafetyFactor);\n}\n'
    )

    text = replace_all_checked(text, 'CopyBuffer(ema_fast_handle,0,0,1,f)', 'CopyBuffer(ema_fast_handle,0,SignalShift(),1,f)', 1)
    text = replace_all_checked(text, 'CopyBuffer(ema_slow_handle,0,0,1,s)', 'CopyBuffer(ema_slow_handle,0,SignalShift(),1,s)', 1)
    text = replace_all_checked(text, 'CopyBuffer(ema_confirm_fast_1_handle,0,0,1,f1)', 'CopyBuffer(ema_confirm_fast_1_handle,0,SignalShift(),1,f1)', 1)
    text = replace_all_checked(text, 'CopyBuffer(ema_confirm_slow_1_handle,0,0,1,s1)', 'CopyBuffer(ema_confirm_slow_1_handle,0,SignalShift(),1,s1)', 1)
    text = replace_all_checked(text, 'CopyBuffer(ema_confirm_fast_2_handle,0,0,1,f2)', 'CopyBuffer(ema_confirm_fast_2_handle,0,SignalShift(),1,f2)', 1)
    text = replace_all_checked(text, 'CopyBuffer(ema_confirm_slow_2_handle,0,0,1,s2)', 'CopyBuffer(ema_confirm_slow_2_handle,0,SignalShift(),1,s2)', 1)
    text = replace_all_checked(text, 'CopyBuffer(adx_m15_handle,0,0,1,buf)', 'CopyBuffer(adx_m15_handle,0,SignalShift(),1,buf)', 1)

    text = replace_all_checked(text, 'double high0=iHigh(_Symbol, PERIOD_M1, 0);\n   double low0 =iLow(_Symbol,  PERIOD_M1, 0);', 'double high0=BarHigh(PERIOD_M1);\n   double low0 =BarLow(PERIOD_M1);', 2)
    text = replace_all_checked(text, 'double close0=iClose(_Symbol, PERIOD_M1, 0);', 'double close0=BarClose(PERIOD_M1);', 1)

    text = replace_once(
        text,
        '      if(lots<=0.0) return true;\n\n      double tp_price=ask + (TP_R*sl_points)*_Point;\n      if(CanSendOrders())',
        '      if(lots<=0.0) return true;\n\n      double tp_price=ask + (TP_R*sl_points)*_Point;\n      if(!MarginOK(ORDER_TYPE_BUY,lots,ask)) return true;\n      if(CanSendOrders())',
    )
    text = replace_once(
        text,
        '   if(lots<=0.0) return true;\n\n   double tp_price=bid - (TP_R*sl_points)*_Point;\n   if(CanSendOrders())',
        '   if(lots<=0.0) return true;\n\n   double tp_price=bid - (TP_R*sl_points)*_Point;\n   if(!MarginOK(ORDER_TYPE_SELL,lots,bid)) return true;\n   if(CanSendOrders())',
    )

    text = replace_once(
        text,
        '      double sl_price = LL15 - buffer_points*_Point;\n      double sl_points = (ask - sl_price)/_Point;\n      if(sl_points < MinSL_points) sl_points = MinSL_points;\n\n      double lots=CalcLots(sl_points, risk_pct);\n      if(lots<=0.0) return;\n\n      double tp_price = ask + (TP_R*sl_points)*_Point;\n\n      if(CanSendOrders())',
        '      double sl_price = LL15 - buffer_points*_Point;\n      double sl_points = (ask - sl_price)/_Point;\n      if(sl_points < MinSL_points)\n      {\n         sl_points = MinSL_points;\n         sl_price = ask - sl_points*_Point;\n      }\n\n      double lots=CalcLots(sl_points, risk_pct);\n      if(lots<=0.0) return;\n\n      double tp_price = ask + (TP_R*sl_points)*_Point;\n      if(!MarginOK(ORDER_TYPE_BUY,lots,ask)) return;\n\n      if(CanSendOrders())',
    )
    text = replace_once(
        text,
        '      double sl_price = HH15 + buffer_points*_Point;\n      double sl_points = (sl_price - bid)/_Point;\n      if(sl_points < MinSL_points) sl_points = MinSL_points;\n\n      double lots=CalcLots(sl_points, risk_pct);\n      if(lots<=0.0) return;\n\n      double tp_price = bid - (TP_R*sl_points)*_Point;\n\n      if(CanSendOrders())',
        '      double sl_price = HH15 + buffer_points*_Point;\n      double sl_points = (sl_price - bid)/_Point;\n      if(sl_points < MinSL_points)\n      {\n         sl_points = MinSL_points;\n         sl_price = bid + sl_points*_Point;\n      }\n\n      double lots=CalcLots(sl_points, risk_pct);\n      if(lots<=0.0) return;\n\n      double tp_price = bid - (TP_R*sl_points)*_Point;\n      if(!MarginOK(ORDER_TYPE_SELL,lots,bid)) return;\n\n      if(CanSendOrders())',
    )

    text = replace_once(
        text,
        '//==================== ONTICK ====================//\nvoid OnTick()',
        'void OnDeinit(const int reason)\n{\n   if(atr_m1_handle!=INVALID_HANDLE) IndicatorRelease(atr_m1_handle);\n   if(adx_m1_handle!=INVALID_HANDLE) IndicatorRelease(adx_m1_handle);\n   if(ema_fast_handle!=INVALID_HANDLE) IndicatorRelease(ema_fast_handle);\n   if(ema_slow_handle!=INVALID_HANDLE) IndicatorRelease(ema_slow_handle);\n   if(atr_vol_handle!=INVALID_HANDLE) IndicatorRelease(atr_vol_handle);\n   if(bb_handle!=INVALID_HANDLE) IndicatorRelease(bb_handle);\n   if(kc_ema_handle!=INVALID_HANDLE) IndicatorRelease(kc_ema_handle);\n   if(kc_atr_handle!=INVALID_HANDLE) IndicatorRelease(kc_atr_handle);\n   if(adx_m15_handle!=INVALID_HANDLE) IndicatorRelease(adx_m15_handle);\n   if(ema_confirm_fast_1_handle!=INVALID_HANDLE) IndicatorRelease(ema_confirm_fast_1_handle);\n   if(ema_confirm_slow_1_handle!=INVALID_HANDLE) IndicatorRelease(ema_confirm_slow_1_handle);\n   if(ema_confirm_fast_2_handle!=INVALID_HANDLE) IndicatorRelease(ema_confirm_fast_2_handle);\n   if(ema_confirm_slow_2_handle!=INVALID_HANDLE) IndicatorRelease(ema_confirm_slow_2_handle);\n   if(ema_macro_fast_handle!=INVALID_HANDLE) IndicatorRelease(ema_macro_fast_handle);\n   if(ema_macro_slow_handle!=INVALID_HANDLE) IndicatorRelease(ema_macro_slow_handle);\n   if(atr_macro_handle!=INVALID_HANDLE) IndicatorRelease(atr_macro_handle);\n}\n\n//==================== ONTICK ====================//\nvoid OnTick()'
    )

    text = replace_once(
        text,
        '   long reason=(long)HistoryDealGetInteger(trans.deal, DEAL_REASON);\n   double deal_pnl=HistoryDealGetDouble(trans.deal, DEAL_PROFIT) +',
        '   string deal_symbol=HistoryDealGetString(trans.deal, DEAL_SYMBOL);\n   long deal_magic=(long)HistoryDealGetInteger(trans.deal, DEAL_MAGIC);\n   long deal_entry=(long)HistoryDealGetInteger(trans.deal, DEAL_ENTRY);\n   if(deal_symbol!=_Symbol || deal_magic!=InpMagicNumber || deal_entry!=DEAL_ENTRY_OUT) return;\n\n   long reason=(long)HistoryDealGetInteger(trans.deal, DEAL_REASON);\n   double deal_pnl=HistoryDealGetDouble(trans.deal, DEAL_PROFIT) +'
    )

    DST.write_text(text, encoding="utf-8")
    print(f"Generated {DST.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
