package handler

import (
	"database/sql"
	"fmt"
	"net/http"
	"strconv"
	"time"

	"github.com/XiaoleC05/dormguard-go/internal/bot"
	"github.com/XiaoleC05/dormguard-go/internal/config"
	"github.com/XiaoleC05/dormguard-go/internal/service"
	"github.com/gin-gonic/gin"
)

type SystemHandler struct {
	crawlerService *service.CrawlerService
	powerService   *service.PowerRecordService
	botClient      *bot.Client
}

func NewSystemHandler(db *sql.DB) *SystemHandler {
	return &SystemHandler{
		crawlerService: service.NewCrawlerService(db),
		powerService:   service.NewPowerRecordService(db),
		botClient:      bot.NewClient(),
	}
}

// ManualCrawl 手动触发抓取
// POST /api/system/crawl
func (h *SystemHandler) ManualCrawl(c *gin.Context) {
	success := h.crawlerService.CrawlAndSave(false, false)

	if success {
		c.JSON(http.StatusOK, gin.H{
			"success": true,
			"message": "抓取完成",
		})
	} else {
		c.JSON(http.StatusOK, gin.H{
			"success": false,
			"message": "抓取失败或无启用的规则",
		})
	}
}

// SendReport 发送报告到 QQ 群
// POST /api/system/report
func (h *SystemHandler) SendReport(c *gin.Context) {
	cfg := config.Cfg

	if !cfg.QQBotEnabled {
		c.JSON(http.StatusOK, gin.H{
			"success": false,
			"message": "QQ 机器人未启用",
		})
		return
	}

	if cfg.QQBotGroupID == "" {
		c.JSON(http.StatusOK, gin.H{
			"success": false,
			"message": "未配置 QQ 群号",
		})
		return
	}

	groupID, err := strconv.Atoi(cfg.QQBotGroupID)
	if err != nil {
		c.JSON(http.StatusOK, gin.H{
			"success": false,
			"message": "QQ 群号格式错误",
		})
		return
	}

	// 获取最新记录
	record, err := h.powerService.GetLatestRecord(cfg.CrawlerDormNumber)
	if err != nil {
		c.JSON(http.StatusOK, gin.H{
			"success": false,
			"message": "无可用数据",
		})
		return
	}

	// 构建报告
	msg := fmt.Sprintf("【电费报告】\n宿舍: %s\n空调: %.2f 度\n照明: %.2f 度\n时间: %s",
		record.DormNumber,
		*record.KBalance,
		*record.ZBalance,
		record.CreatedAt.Format("2006-01-02 15:04:05"),
	)

	success, errMsg := h.botClient.SendGroupMsg(groupID, msg)
	if !success {
		c.JSON(http.StatusOK, gin.H{
			"success": false,
			"message": errMsg,
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"success": true,
		"message": "报告已发送",
	})
}

// QQStatus 检查 QQ 机器人状态
// GET /api/system/qq-status
func (h *SystemHandler) QQStatus(c *gin.Context) {
	cfg := config.Cfg

	if !cfg.QQBotEnabled {
		c.JSON(http.StatusOK, gin.H{
			"success":          false,
			"message":          "QQ 机器人未启用",
			"nonebot_running":  false,
			"napcat_connected": false,
		})
		return
	}

	nonebotRunning, napcatConnected, botID, errMsg := h.botClient.GetStatus()

	if !nonebotRunning {
		c.JSON(http.StatusOK, gin.H{
			"success":          false,
			"message":          errMsg,
			"nonebot_running":  false,
			"napcat_connected": false,
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"success":          true,
		"message":          "连接正常",
		"nonebot_running":  true,
		"napcat_connected": napcatConnected,
		"bot_id":           botID,
	})
}

// Health 健康检查
// GET /health
func Health(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{
		"status": "ok",
		"time":   time.Now().Format(time.RFC3339),
	})
}
