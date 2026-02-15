package handlers

import (
	"net/http"
	"github.com/cneluhena/StockPulse/internal/config"
	"github.com/gin-gonic/gin"
)

type Handler struct {
	cfg *config.Config
}

func New(cfg *config.Config) *Handler {
	return &Handler{cfg: cfg}
}

func (h *Handler) Ping(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{"status": "StockPulse API is live"})
}

func (h *Handler) GetConfig(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{
		"monitored_symbols": h.cfg.Symbols,
		"kafka_broker":      h.cfg.KafkaBroker,
	})
}