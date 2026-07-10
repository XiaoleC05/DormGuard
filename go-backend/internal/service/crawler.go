package service

import (
	"database/sql"
	"log"
	"time"

	"github.com/XiaoleC05/dormguard-go/internal/alert"
	"github.com/XiaoleC05/dormguard-go/internal/config"
	"github.com/XiaoleC05/dormguard-go/internal/crawler"
	"github.com/XiaoleC05/dormguard-go/internal/model"
)

type CrawlerService struct {
	db           *sql.DB
	powerSvc     *PowerRecordService
	ruleSvc      *AlertRuleService
	logSvc       *AlertLogService
	alertManager *alert.Manager
}

func NewCrawlerService(db *sql.DB) *CrawlerService {
	return &CrawlerService{
		db:           db,
		powerSvc:     NewPowerRecordService(db),
		ruleSvc:      NewAlertRuleService(db),
		logSvc:       NewAlertLogService(db),
		alertManager: alert.NewManager(),
	}
}

func (s *CrawlerService) CrawlAndSave(forceAlert, skipAlert bool) bool {
	rules, err := s.ruleSvc.GetEnabledRules()
	if err != nil {
		log.Printf("获取启用规则失败: %v", err)
		return false
	}

	if len(rules) == 0 {
		log.Println("没有启用的告警规则，跳过爬虫任务")
		return false
	}

	c := crawler.NewPowerCrawler()
	successCount := 0

	for _, rule := range rules {
		if rule.RoomID == nil || *rule.RoomID == "" {
			log.Printf("宿舍 %s 未配置room_id，跳过", rule.DormNumber)
			continue
		}

		data, err := c.FetchPowerData(rule.DormNumber, *rule.RoomID)
		if err != nil {
			log.Printf("获取宿舍 %s 的电费数据失败: %v", rule.DormNumber, err)
			continue
		}

		createReq := model.PowerRecordCreate{
			DormNumber: data.DormNumber,
			Balance:    data.Balance,
			KBalance:   &data.KBalance,
			ZBalance:   &data.ZBalance,
		}

		if _, err := s.powerSvc.CreateRecord(createReq); err != nil {
			log.Printf("保存记录失败: %v", err)
			continue
		}

		log.Printf("成功抓取: %s, 空调 %.2f 度, 照明 %.2f 度",
			data.DormNumber, data.KBalance, data.ZBalance)

		if !skipAlert {
			s.checkAndAlert(rule.DormNumber, &data.KBalance, &data.ZBalance, forceAlert)
		}

		successCount++
	}

	return successCount > 0
}

func (s *CrawlerService) checkAndAlert(dormNumber string, kbalance, zbalance *float64, forceAlert bool) {
	rule, err := s.ruleSvc.GetRule(dormNumber)
	if err != nil || rule == nil {
		return
	}
	if !rule.Enabled {
		return
	}

	cfg := config.Cfg
	kthreshold := cfg.DefaultAlertThreshold
	zthreshold := cfg.DefaultAlertThreshold
	if rule.KThreshold != nil {
		kthreshold = *rule.KThreshold
	}
	if rule.ZThreshold != nil {
		zthreshold = *rule.ZThreshold
	}

	if kbalance != nil && *kbalance < kthreshold {
		s.sendAlert(rule, dormNumber, *kbalance, kthreshold, "ac", "空调", forceAlert)
	}
	if zbalance != nil && *zbalance < zthreshold {
		s.sendAlert(rule, dormNumber, *zbalance, zthreshold, "light", "照明", forceAlert)
	}
}

func (s *CrawlerService) sendAlert(rule *model.AlertRule, dormNumber string, balance, threshold float64,
	category, categoryName string, forceAlert bool) {

	if !rule.QQEnabled {
		return
	}

	if !forceAlert && !s.shouldSendAlert(dormNumber, category) {
		return
	}

	latest, _ := s.powerSvc.GetLatestRecord(dormNumber)
	var kbalance, zbalance *float64
	if latest != nil {
		kbalance = latest.KBalance
		zbalance = latest.ZBalance
	}

	result := s.alertManager.SendAlert(dormNumber, categoryName, balance, threshold,
		true, kbalance, zbalance)

	var msg *string
	status := "success"
	if !result.QQ {
		status = "failed"
		errMsg := result.QQError
		msg = &errMsg
	}

	s.logSvc.CreateLog(model.AlertLog{
		DormNumber:    dormNumber,
		AlertType:     "qq",
		AlertCategory: &category,
		Balance:       balance,
		Threshold:     threshold,
		AlertMessage:  msg,
		AlertStatus:   status,
	})
}

func (s *CrawlerService) shouldSendAlert(dormNumber, category string) bool {
	cfg := config.Cfg

	if cfg.QQAlertPauseUntil != "" {
		resumeDate, err := time.Parse("2006-01-02", cfg.QQAlertPauseUntil)
		if err == nil && time.Now().Before(resumeDate) {
			return false
		}
	}

	lastLog, err := s.logSvc.GetLastSuccessLog(dormNumber, category, "qq")
	if err != nil {
		return true
	}

	cooldown := cfg.AlertCooldownDuration()
	if time.Since(lastLog.CreatedAt) < cooldown {
		return false
	}

	return true
}
