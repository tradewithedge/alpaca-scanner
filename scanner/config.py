from dataclasses import dataclass

@dataclass(frozen=True)
class ScannerConfig:
    min_price: float = 5.0
    min_prev_dollar_volume: float = 20_000_000.0
    min_avg_dollar_volume_20d: float = 20_000_000.0
    min_avg_volume_20d: float = 500_000.0
    min_atr_pct: float = 1.5
    max_atr_pct: float = 10.0
    min_history_bars: int = 200
    min_rs_percentile: float = 60.0
    require_above_ma50: bool = False
    require_ma50_above_ma200: bool = False
    max_deep_scan_symbols: int = 2000
    history_days: int = 280
    bar_batch_size: int = 40
    snapshot_batch_size: int = 100
    min_quality_actionable: float = 75.0
    min_entry_actionable: float = 72.0
    min_quality_wait: float = 80.0
    min_quality_developing: float = 65.0
    max_ext_ema8_pct: float = 5.0
    max_ext_ema20_pct: float = 8.0
    max_ext_atr: float = 2.0
    strict_event_gate: bool = True

MARKET_SYMBOLS = ["SPY", "QQQ", "IWM"]

SECTOR_ETFS = {
    "XLK": "Technology", "XLF": "Financials", "XLI": "Industrials",
    "XLY": "Consumer Discretionary", "XLC": "Communication Services",
    "XLV": "Health Care", "XLP": "Consumer Staples", "XLE": "Energy",
    "XLU": "Utilities", "XLRE": "Real Estate", "XLB": "Materials",
    "SMH": "Semiconductors", "XBI": "Biotechnology",
}

QUALITY_PRESETS = {
    "BALANCED": dict(min_avg_dollar_volume_20d=20_000_000, min_avg_volume_20d=500_000,
                     min_atr_pct=1.5, max_atr_pct=10.0, min_rs_percentile=60.0),
    "STRICT": dict(min_avg_dollar_volume_20d=30_000_000, min_avg_volume_20d=750_000,
                   min_atr_pct=1.5, max_atr_pct=8.0, min_rs_percentile=70.0),
    "ELITE": dict(min_avg_dollar_volume_20d=50_000_000, min_avg_volume_20d=1_000_000,
                  min_atr_pct=1.5, max_atr_pct=7.0, min_rs_percentile=80.0),
}
