# indicators/keltner_channel.py
import pandas as pd
import numpy as np
from typing import Dict, Any, List
from stock_indicators import indicators
from stock_indicators.indicators.common import Quote
from .base_indicator import BaseIndicator

class KeltnerChannel(BaseIndicator):
    def __init__(self, ema_period: int = 20, atr_period: int = 10, atr_multiplier: float = 2.0,
                 breakout_tolerance: float = 0.001, confirmation_candles: int = 1, 
                 verbose: bool = False, fill_missing: bool = False):
        self.ema_period = ema_period
        self.atr_period = atr_period
        self.atr_multiplier = atr_multiplier
        self.breakout_tolerance = breakout_tolerance
        self.confirmation_candles = confirmation_candles
        self.verbose = verbose
        self.fill_missing = fill_missing

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # Initialisation des colonnes de sortie
        kc_columns = ['kc_middle', 'kc_upper', 'kc_lower', 'kc_atr', 'kc_position', 'kc_width_pct']
        for col in kc_columns:
            df[col] = np.nan

        # Clean data
        required_cols = ["open", "high", "low", "close"]
        df = df.dropna(subset=required_cols)

        min_period = max(self.ema_period, self.atr_period)
        if len(df) < min_period:
            if self.verbose:
                print("⚠️ Données insuffisantes pour le calcul Keltner Channel")
            return df

        # Préparation des quotes
        original_dates = []
        quotes = []

        for i, row in df.iterrows():
            date_val = i if pd.api.types.is_datetime64_any_dtype(df.index) else row.get('date', i)
            original_dates.append(date_val)
            quotes.append(Quote(
                date=date_val,
                open=float(row['open']),
                high=float(row['high']),
                low=float(row['low']),
                close=float(row['close']),
                volume=float(row.get('volume', 0))
            ))

        # Calcul ATR / EMA
        try:
            atr_results = indicators.get_atr(quotes, self.atr_period)
            ema_results = indicators.get_ema(quotes, self.ema_period)
        except AttributeError:
            atr_results = indicators.atr(quotes, self.atr_period)
            ema_results = indicators.ema(quotes, self.ema_period)

        # Alignement robuste
        df = self._align_results_by_date(df, original_dates, atr_results, ema_results)
        return df

    def _align_results_by_date(
        self,
        df: pd.DataFrame,
        original_dates: List,
        atr_results: List,
        ema_results: List
    ) -> pd.DataFrame:
        # Extraction ATR / EMA
        atr_data = [{"date": atr.date, "kc_atr": atr.atr} for atr in atr_results if atr and hasattr(atr, "atr")]
        ema_data = [{"date": ema.date, "kc_middle": ema.ema} for ema in ema_results if ema and hasattr(ema, "ema")]

        # Si aucune donnée valide
        if not atr_data or not ema_data:
            if self.verbose:
                print("⚠️ Pas de données ATR ou EMA valides, retour DataFrame original avec colonnes NaN")
            for col in ["kc_middle", "kc_atr", "kc_upper", "kc_lower", "kc_position", "kc_width_pct"]:
                if col not in df.columns:
                    df[col] = np.nan
            return df

        atr_df = pd.DataFrame(atr_data)
        ema_df = pd.DataFrame(ema_data)
        merged_indicators = pd.merge(atr_df, ema_df, on="date", how="outer").sort_values("date")

        df_reset = df.reset_index()
        if "date" not in df_reset.columns:
            df_reset["date"] = df_reset.get("index", df_reset.index)
        df_reset["date"] = pd.to_datetime(df_reset["date"])

        df_merged = pd.merge(df_reset, merged_indicators, on="date", how="left")

        # Création forcée des colonnes avant fill
        for col in ["kc_middle", "kc_atr", "kc_upper", "kc_lower", "kc_position", "kc_width_pct"]:
            if col not in df_merged.columns:
                df_merged[col] = np.nan

        # Calcul des bandes Keltner
        df_merged["kc_upper"] = df_merged["kc_middle"] + (self.atr_multiplier * df_merged["kc_atr"])
        df_merged["kc_lower"] = df_merged["kc_middle"] - (self.atr_multiplier * df_merged["kc_atr"])
        width = df_merged["kc_upper"] - df_merged["kc_lower"]
        df_merged["kc_position"] = np.clip(
            np.where(width != 0, (df_merged["close"] - df_merged["kc_lower"]) / width, 0.5),
            0, 1
        )
        df_merged["kc_width_pct"] = np.where(
            df_merged["kc_middle"] != 0, width / df_merged["kc_middle"] * 100, np.nan
        )

        # Gestion des données manquantes
        initial_count = len(df_merged)
        if self.fill_missing:
            kc_value_cols = ["kc_middle", "kc_atr", "kc_upper", "kc_lower"]
            df_merged[kc_value_cols] = df_merged[kc_value_cols].ffill()
            width_ff = df_merged["kc_upper"] - df_merged["kc_lower"]
            df_merged["kc_position"] = np.clip(
                np.where(width_ff != 0, (df_merged["close"] - df_merged["kc_lower"]) / width_ff, 0.5),
                0, 1
            )
            df_merged["kc_width_pct"] = np.where(
                df_merged["kc_middle"] != 0, width_ff / df_merged["kc_middle"] * 100, np.nan
            )
        else:
            df_merged = df_merged.dropna(subset=["kc_middle", "kc_atr"])

        if self.verbose and len(df_merged) < initial_count:
            removed = initial_count - len(df_merged)
            method = "forward fill" if self.fill_missing else "drop"
            print(f"📊 Keltner Channel: {removed} lignes traitées ({method})")

        df_merged = df_merged.set_index("date")
        return df_merged

    def get_signal(self, df: pd.DataFrame, current_index: int) -> int:
        current_index = int(current_index)
        if current_index < max(self.ema_period, self.atr_period):
            return 0

        cur = df.iloc[current_index]
        prev = df.iloc[current_index - 1]

        upper_tolerance = cur['kc_upper'] * (1 + self.breakout_tolerance)
        lower_tolerance = cur['kc_lower'] * (1 + self.breakout_tolerance)

        if (cur['close'] > cur['kc_upper']) and (prev['close'] < upper_tolerance):
            if self._confirm_breakout(df, current_index, is_bullish=True):
                return 1
        if (cur['close'] < cur['kc_lower']) and (prev['close'] > lower_tolerance):
            if self._confirm_breakout(df, current_index, is_bullish=False):
                return -1

        return 0

    def get_detailed_signal(self, df: pd.DataFrame, current_index: int) -> Dict[str, Any]:
        current_index = int(current_index)
        base_signal = self.get_signal(df, current_index)

        if current_index < max(self.ema_period, self.atr_period):
            return {"signal": 0, "confidence": 0.0, "position": 0.5, "atr": 0.0, "width_pct": 0.0, "strength": 0.0}

        cur = df.iloc[current_index]
        confidence = abs(cur['kc_position'] - 0.5) * 2

        if base_signal == 1:
            strength = (cur['close'] - cur['kc_upper']) / cur['kc_atr']
        elif base_signal == -1:
            strength = (cur['kc_lower'] - cur['close']) / cur['kc_atr']
        else:
            strength = 0.0

        return {
            "signal": base_signal,
            "confidence": round(confidence, 3),
            "position": round(cur['kc_position'], 3),
            "atr": round(cur.get('kc_atr', 0), 5),
            "width_pct": round(cur.get('kc_width_pct', 0), 4),
            "strength": round(strength, 3)
        }

    def _confirm_breakout(self, df: pd.DataFrame, current_index: int, is_bullish: bool) -> bool:
        if self.confirmation_candles == 0:
            return True

        end_idx = min(current_index + self.confirmation_candles, len(df))
        for i in range(current_index + 1, end_idx):
            candle = df.iloc[i]
            ref_candle = df.iloc[current_index]

            if pd.isna(candle['close']) or pd.isna(ref_candle['kc_upper']) or pd.isna(ref_candle['kc_lower']):
                return False

            if is_bullish and candle['close'] < ref_candle['kc_upper']:
                return False
            if not is_bullish and candle['close'] > ref_candle['kc_lower']:
                return False

        return True

    def get_name(self) -> str:
        return f"KeltnerChannel_{self.ema_period}_{self.atr_period}_{self.atr_multiplier}"
