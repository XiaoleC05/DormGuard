package config

import (
	"fmt"
	"log"
	"os"
	"strconv"
	"time"

	"github.com/joho/godotenv"
)

type Config struct {
	DBHost     string
	DBPort     int
	DBUser     string
	DBPassword string
	DBName     string

	CrawlerBaseURL    string
	CrawlerAPIBaseURL string
	CrawlerDormNumber string
	CrawlerOpenID     string
	CrawlerJSessionID string
	CrawlerRoomID     string
	CrawlerAreaID     string
	CrawlerYQID       string
	CrawlerBuildingID string
	CrawlerFloorID    string
	CrawlerFactoryCode string
	CrawlerSign       string
	CrawlerOrgID      string

	SchedulerIntervalHours     int
	AlertCooldownHours         int
	CrawlerAlertThreshold      float64
	QQAlertPauseUntil          string

	QQBotEnabled  bool
	QQBotAPIURL   string
	QQBotAPIToken string
	QQBotID       string
	QQBotGroupID  string

	AppDebug bool

	DefaultAlertThreshold float64

	AdminUsername        string
	AdminPassword        string
	AdminJWTSecret       string
	AdminTokenExpireHours int

	OxeliaGatewayMode   bool
	OxeliaGatewaySecret string

	ServerPort string
}

var Cfg *Config

func Load() *Config {
	_ = godotenv.Load()

	Cfg = &Config{
		DBHost:     getEnv("DB_HOST", "localhost"),
		DBPort:     getEnvInt("DB_PORT", 3306),
		DBUser:     getEnv("DB_USER", "root"),
		DBPassword: getEnv("DB_PASSWORD", ""),
		DBName:     getEnv("DB_NAME", "dorm_guard"),

		CrawlerBaseURL:     getEnv("CRAWLER_BASE_URL", "https://ecard.xhu.edu.cn"),
		CrawlerAPIBaseURL:  getEnv("CRAWLER_API_BASE_URL", "https://ecard.xhu.edu.cn/api"),
		CrawlerDormNumber:  getEnv("CRAWLER_DORM_NUMBER", ""),
		CrawlerOpenID:      getEnv("CRAWLER_OPENID", ""),
		CrawlerJSessionID:  getEnv("CRAWLER_JSESSIONID", ""),
		CrawlerRoomID:      getEnv("CRAWLER_ROOM_ID", ""),
		CrawlerAreaID:      getEnv("CRAWLER_AREA_ID", "1"),
		CrawlerYQID:        getEnv("CRAWLER_YQ_ID", "3"),
		CrawlerBuildingID:  getEnv("CRAWLER_BUILDING_ID", "40-1"),
		CrawlerFloorID:     getEnv("CRAWLER_FLOOR_ID", "3"),
		CrawlerFactoryCode: getEnv("CRAWLER_FACTORY_CODE", "E014"),
		CrawlerSign:        getEnv("CRAWLER_SIGN", "qt"),
		CrawlerOrgID:       getEnv("CRAWLER_ORG_ID", "2"),

		SchedulerIntervalHours:    getEnvInt("SCHEDULER_INTERVAL_HOURS", 2),
		AlertCooldownHours:        getEnvInt("ALERT_COOLDOWN_HOURS", 2),
		CrawlerAlertThreshold:     getEnvFloat("CRAWLER_ALERT_THRESHOLD", 20.0),
		QQAlertPauseUntil:         getEnv("QQ_ALERT_PAUSE_UNTIL", ""),

		QQBotEnabled:  getEnvBool("QQ_BOT_ENABLED", false),
		QQBotAPIURL:   getEnv("QQ_BOT_API_URL", ""),
		QQBotAPIToken: getEnv("QQ_BOT_API_TOKEN", ""),
		QQBotID:       getEnv("QQ_BOT_ID", "1270667498"),
		QQBotGroupID:  getEnv("QQ_BOT_GROUP_ID", "6011223303"),

		AppDebug: getEnvBool("APP_DEBUG", false),

		DefaultAlertThreshold: getEnvFloat("DEFAULT_ALERT_THRESHOLD", 20.0),

		AdminUsername:        getEnv("ADMIN_USERNAME", "root"),
		AdminPassword:        getEnv("ADMIN_PASSWORD", ""),
		AdminJWTSecret:       getEnv("ADMIN_JWT_SECRET", ""),
		AdminTokenExpireHours: getEnvInt("ADMIN_TOKEN_EXPIRE_HOURS", 168),

		OxeliaGatewayMode:   getEnvBool("OXELIA_GATEWAY_MODE", false),
		OxeliaGatewaySecret: getEnv("OXELIA_GATEWAY_SECRET", ""),

		ServerPort: getEnv("SERVER_PORT", "8000"),
	}

	if !Cfg.AppDebug {
		if len(Cfg.AdminPassword) < 12 {
			log.Fatal("生产环境须在 .env 设置 ADMIN_PASSWORD（至少 12 位）")
		}
		if len(Cfg.AdminJWTSecret) < 32 {
			log.Fatal("生产环境须在 .env 设置 ADMIN_JWT_SECRET（至少 32 位）")
		}
	}

	return Cfg
}

func (c *Config) DSN() string {
	return fmt.Sprintf("%s:%s@tcp(%s:%d)/%s?charset=utf8mb4&parseTime=true&loc=Local",
		c.DBUser, c.DBPassword, c.DBHost, c.DBPort, c.DBName)
}

func (c *Config) AlertCooldownDuration() time.Duration {
	return time.Duration(c.AlertCooldownHours) * time.Hour
}

func getEnv(key, fallback string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return fallback
}

func getEnvBool(key string, fallback bool) bool {
	v := os.Getenv(key)
	if v == "" {
		return fallback
	}
	b, err := strconv.ParseBool(v)
	if err != nil {
		return fallback
	}
	return b
}

func getEnvInt(key string, fallback int) int {
	v := os.Getenv(key)
	if v == "" {
		return fallback
	}
	n, err := strconv.Atoi(v)
	if err != nil {
		return fallback
	}
	return n
}

func getEnvFloat(key string, fallback float64) float64 {
	v := os.Getenv(key)
	if v == "" || v == "None" {
		return fallback
	}
	f, err := strconv.ParseFloat(v, 64)
	if err != nil {
		return fallback
	}
	return f
}
