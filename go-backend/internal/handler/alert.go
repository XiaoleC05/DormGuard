package handler

import (
	"database/sql"
	"net/http"
	"strconv"

	"github.com/XiaoleC05/dormguard-go/internal/config"
	"github.com/XiaoleC05/dormguard-go/internal/model"
	"github.com/XiaoleC05/dormguard-go/internal/service"
	"github.com/gin-gonic/gin"
)

type AlertHandler struct {
	ruleSvc *service.AlertRuleService
	logSvc  *service.AlertLogService
}

func NewAlertHandler(db *sql.DB) *AlertHandler {
	return &AlertHandler{
		ruleSvc: service.NewAlertRuleService(db),
		logSvc:  service.NewAlertLogService(db),
	}
}

func (h *AlertHandler) GetRule(c *gin.Context) {
	dormNumber := c.Param("dorm_number")

	rule, err := h.ruleSvc.GetRule(dormNumber)
	if err != nil {
		if err == sql.ErrNoRows {
			c.JSON(http.StatusNotFound, gin.H{"error": "规则不存在"})
			return
		}
		c.JSON(http.StatusInternalServerError, gin.H{"error": "查询失败"})
		return
	}

	// 非管理员隐藏阈值字段
	if GetRole(c) != "admin" {
		rule.KThreshold = nil
		rule.ZThreshold = nil
	}

	c.JSON(http.StatusOK, rule)
}

func (h *AlertHandler) CreateRule(c *gin.Context) {
	var req model.AlertRuleCreate
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "请求格式错误"})
		return
	}

	rule, err := h.ruleSvc.CreateRule(req)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusCreated, rule)
}

func (h *AlertHandler) UpdateRule(c *gin.Context) {
	dormNumber := c.Param("dorm_number")

	var req model.AlertRuleUpdate
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "请求格式错误"})
		return
	}

	rule, err := h.ruleSvc.UpdateRule(dormNumber, req)
	if err != nil {
		if err == sql.ErrNoRows {
			c.JSON(http.StatusNotFound, gin.H{"error": "规则不存在"})
			return
		}
		c.JSON(http.StatusInternalServerError, gin.H{"error": "更新失败"})
		return
	}

	c.JSON(http.StatusOK, rule)
}

func (h *AlertHandler) DeleteRule(c *gin.Context) {
	dormNumber := c.Param("dorm_number")

	success, err := h.ruleSvc.DeleteRule(dormNumber)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "删除失败"})
		return
	}
	if !success {
		c.JSON(http.StatusNotFound, gin.H{"error": "规则不存在"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "删除成功"})
}

func (h *AlertHandler) GetLogs(c *gin.Context) {
	dormNumber := c.Query("dorm_number")
	limit, _ := strconv.Atoi(c.DefaultQuery("limit", "50"))

	var dormPtr *string
	if dormNumber != "" {
		dormPtr = &dormNumber
	}

	logs, err := h.logSvc.GetLogs(dormPtr, limit)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "查询失败"})
		return
	}

	// 非管理员隐藏阈值字段
	if GetRole(c) != "admin" {
		for i := range logs {
			logs[i].Threshold = 0
		}
	}

	c.JSON(http.StatusOK, logs)
}

func (h *AlertHandler) GetConfig(c *gin.Context) {
	cfg := config.Cfg
	c.JSON(http.StatusOK, gin.H{
		"dorm_number": cfg.CrawlerDormNumber,
	})
}
