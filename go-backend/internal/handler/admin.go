package handler

import (
	"net/http"

	"github.com/XiaoleC05/dormguard-go/internal/config"
	"github.com/gin-gonic/gin"
)

type AdminHandler struct{}

func NewAdminHandler() *AdminHandler {
	return &AdminHandler{}
}

func (h *AdminHandler) GetSettings(c *gin.Context) {
	settings := config.ReadEnvValues()
	masked := config.MaskEnvValues(settings)

	c.JSON(http.StatusOK, gin.H{
		"settings":         masked,
		"restart_required": false,
	})
}

func (h *AdminHandler) UpdateSettings(c *gin.Context) {
	var req struct {
		Settings map[string]string `json:"settings" binding:"required"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "请求格式错误"})
		return
	}

	if err := config.WriteEnvValues(req.Settings); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "写入失败"})
		return
	}

	config.Load()

	settings := config.ReadEnvValues()
	masked := config.MaskEnvValues(settings)

	c.JSON(http.StatusOK, gin.H{
		"settings":         masked,
		"restart_required": true,
	})
}

func (h *AdminHandler) GetQQConfig(c *gin.Context) {
	cfg := config.Cfg

	c.JSON(http.StatusOK, gin.H{
		"enabled":  cfg.QQBotEnabled,
		"group_id": cfg.QQBotGroupID,
		"bot_id":   cfg.QQBotID,
	})
}
