package config

import (
	"log"
	"os"
	"strings"
	"github.com/joho/godotenv"
)

type Config struct {
	KafkaBroker  string
	KafkaTopic   string
	FinnhubToken string
	Symbols      []string
}

func Load() *Config {

	if err := godotenv.Load(); err != nil {
		log.Println("No .env file found, using system env")
	}

	return &Config{
		KafkaBroker:  getEnv("KAFKA_BROKER", ""),
		KafkaTopic:   getEnv("KAFKA_TOPIC", ""),
		FinnhubToken: getEnv("FINNHUB_TOKEN", ""),
		Symbols:      strings.Split(getEnv("SYMBOL_LIST", "BINANCE:ETHUSDT,BINANCE:BTCUSDT"), ","),
	}
	
}

func getEnv(key, fallback string) string {
	if value, ok := os.LookupEnv(key); ok {
		return value
	}
	return fallback
}