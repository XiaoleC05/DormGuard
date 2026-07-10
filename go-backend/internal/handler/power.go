package handler

import (
	"database/sql"
	"net/http"
	"strconv"

	"github.com/XiaoleC05/dormguard-go/internal/model"
	"github.com/XiaoleC05/dormguard-go/internal/service"
	"github.com/gin-gonic/gin"
)

type PowerHandler struct {
	powerSvc *service.PowerRecordService
}

func NewPowerHandler(db *sql.DB) *PowerHandler {
	return &PowerHandler{
		powerSvc: service.NewPowerRecordService(db),
	}
}

func (h *PowerHandler) GetLatest(c *gin.Context) {
	dormNumber := c.Param("dorm_number")

	record, err := h.powerSvc.GetLatestRecord(dormNumber)
	if err != nil {
		if err == sql.ErrNoRows {
			c.JSON(http.StatusNotFound, gin.H{"error": "暂无记录"})
			return
		}
		c.JSON(http.StatusInternalServerError, gin.H{"error": "查询失败"})
		return
	}

	c.JSON(http.StatusOK, record)
}

func (h *PowerHandler) GetRecords(c *gin.Context) {
	dormNumber := c.Param("dorm_number")

	limit, _ := strconv.Atoi(c.DefaultQuery("limit", "100"))
	offset, _ := strconv.Atoi(c.DefaultQuery("offset", "0"))

	records, err := h.powerSvc.GetRecords(dormNumber, limit, offset)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "查询失败"})
		return
	}

	total, err := h.powerSvc.CountRecords(dormNumber)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "统计失败"})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"items": records,
		"total": total,
	})
}

func (h *PowerHandler) Create(c *gin.Context) {
	var req model.PowerRecordCreate
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "请求格式错误"})
		return
	}

	created, err := h.powerSvc.CreateRecord(req)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "创建失败"})
		return
	}

	c.JSON(http.StatusCreated, created)
}
