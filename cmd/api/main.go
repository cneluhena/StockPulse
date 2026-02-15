package main

import (
	"log"
	"github.com/cneluhena/StockPulse/internal/config"
	"github.com/cneluhena/StockPulse/internal/handlers"
	"github.com/gin-gonic/gin"
)

func main() {
	cfg := config.Load()
	
	r := gin.Default()
	h := handlers.New(cfg)

	v1 := r.Group("/api/v1")
	{
		v1.GET("/ping", h.Ping)
		v1.GET("/status", h.GetConfig)
	}

	log.Fatal(r.Run(":8080"))
}