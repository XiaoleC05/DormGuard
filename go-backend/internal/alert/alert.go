package alert

import (
	"fmt"
	"log"
	"strconv"
	"strings"

	"github.com/XiaoleC05/dormguard-go/internal/bot"
	"github.com/XiaoleC05/dormguard-go/internal/config"
)

type QQBotAlert struct {
	client  *bot.Client
	enabled bool
	botID   string
	groupID string
}

func NewQQBotAlert() *QQBotAlert {
	cfg := config.Cfg
	return &QQBotAlert{
		client:  bot.NewClient(),
		enabled: cfg.QQBotEnabled,
		botID:   cfg.QQBotID,
		groupID: cfg.QQBotGroupID,
	}
}

func (a *QQBotAlert) Send(dormNumber, categoryName string, balance, threshold float64, kbalance, zbalance *float64) (bool, string) {
	if !a.enabled {
		return false, "QQ告警未启用"
	}
	if a.groupID == "" {
		return false, "未配置告警群号"
	}

	groupNum, err := strconv.Atoi(strings.TrimSpace(a.groupID))
	if err != nil {
		return false, "告警群号配置无效"
	}

	msg := a.buildMessage(dormNumber, categoryName, balance, threshold, kbalance, zbalance)
	return a.client.SendGroupMsg(groupNum, msg)
}

func (a *QQBotAlert) buildMessage(dormNumber, categoryName string, balance, threshold float64, kbalance, zbalance *float64) string {
	var b strings.Builder
	b.WriteString("【宿舍电费告警】\n")
	b.WriteString("━━━━━━━━━━━━━━━━━━\n")
	fmt.Fprintf(&b, "宿舍号：%s\n", dormNumber)
	fmt.Fprintf(&b, "告警类型：%s余量不足\n", categoryName)
	fmt.Fprintf(&b, "当前余量：%.2f 度\n", balance)
	fmt.Fprintf(&b, "告警阈值：%.2f 度\n", threshold)

	if kbalance != nil || zbalance != nil {
		b.WriteString("\n📊 详细余量：\n")
		if kbalance != nil {
			fmt.Fprintf(&b, "  空调余量：%.2f 度", *kbalance)
			if *kbalance < threshold {
				b.WriteString(" ⚠️")
			}
			b.WriteString("\n")
		}
		if zbalance != nil {
			fmt.Fprintf(&b, "  照明余量：%.2f 度", *zbalance)
			if *zbalance < threshold {
				b.WriteString(" ⚠️")
			}
			b.WriteString("\n")
		}
	}

	b.WriteString("\n⚠️ 请及时充值，避免停电影响正常生活！\n")
	b.WriteString("━━━━━━━━━━━━━━━━━━\n")
	b.WriteString("数据来源：西华大学一卡通宿舍用电小程序\n")
	fmt.Fprintf(&b, "机器人QQ：%s · 告警群：%s", a.botID, a.groupID)
	return b.String()
}

type Manager struct {
	qqAlert *QQBotAlert
}

func NewManager() *Manager {
	return &Manager{
		qqAlert: NewQQBotAlert(),
	}
}

type AlertResult struct {
	QQ       bool
	QQError  string
}

func (m *Manager) SendAlert(dormNumber, categoryName string, balance, threshold float64, qqEnabled bool, kbalance, zbalance *float64) AlertResult {
	result := AlertResult{}
	if !qqEnabled {
		return result
	}

	ok, errMsg := m.qqAlert.Send(dormNumber, categoryName, balance, threshold, kbalance, zbalance)
	result.QQ = ok
	if !ok {
		result.QQError = errMsg
	}

	log.Printf("QQ告警: dorm=%s, category=%s, balance=%.2f, success=%v, error=%s",
		dormNumber, categoryName, balance, ok, errMsg)
	return result
}
