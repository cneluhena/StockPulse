package main

import (
	"context"
	"log"
	"time"

	"github.com/cneluhena/StockPulse/internal/config"
	"github.com/gorilla/websocket"
	"github.com/segmentio/kafka-go"
)

func main() {

	cfg := config.Load()

	log.Println(cfg.KafkaTopic)
	
	writer := &kafka.Writer{
		Addr:  kafka.TCP(cfg.KafkaBroker),
		Topic: cfg.KafkaTopic,
		Async: true,
		BatchSize:    1,         
    	BatchTimeout: 10 * time.Millisecond,
		Logger: kafka.LoggerFunc(log.Printf),
		AllowAutoTopicCreation: true,
	}

	defer writer.Close()

	wsURL := "wss://ws.finnhub.io?token=" + cfg.FinnhubToken
	conn, _, err := websocket.DefaultDialer.Dial(wsURL, nil)

	if err != nil {
		log.Fatal("WebSocket Dial Error:", err)
	}

	for _, s := range cfg.Symbols {
		conn.WriteJSON(map[string]string{"type": "subscribe", "symbol": s})
	}
	
	log.Println("Streaming ticks to Kafka...")

	for {
		_, message, err := conn.ReadMessage()

		if err != nil {
			log.Println("Read error:", err)
			break
		}
		
		//log.Print(string(message))
		writer.WriteMessages(context.Background(), kafka.Message{Value: message})
	}
}