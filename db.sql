CREATE TABLE ohlc_candles (
    symbol VARCHAR(20),
    window_start TIMESTAMP,
    window_end TIMESTAMP,
    open_price DOUBLE PRECISION,
    high_price DOUBLE PRECISION,
    low_price DOUBLE PRECISION,
    close_price DOUBLE PRECISION,
    PRIMARY KEY (symbol, window_start)
);