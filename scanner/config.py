from dataclasses import dataclass

@dataclass(frozen=True)
class ScannerConfig:
    min_price: float = 5.0
    min_prev_dollar_volume: float = 20_000_000.0
    max_deep_scan_symbols: int = 1200
    history_days: int = 120
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
