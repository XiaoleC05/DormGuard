package main

import (
	"log"
	"os"
	"strings"
	"time"

	"github.com/XiaoleC05/dormguard-go/internal/config"
	"github.com/XiaoleC05/dormguard-go/internal/database"
	"github.com/XiaoleC05/dormguard-go/internal/handler"
	"github.com/XiaoleC05/dormguard-go/internal/scheduler"
	"github.com/XiaoleC05/dormguard-go/internal/service"
	"github.com/gin-contrib/cors"
	"github.com/gin-gonic/gin"
)

func corsOrigins() []string {
	if v := os.Getenv("CORS_ALLOWED_ORIGINS"); v != "" {
		return strings.Split(v, ",")
	}
	return []string{"http://localhost:5173"}
}

func main() {
	cfg := config.Load()

	if cfg.OxeliaGatewayMode && cfg.OxeliaGatewaySecret == "" {
		log.Fatalf("缃戝叧妯″紡瑕佹眰閰嶇疆 OXELIA_GATEWAY_SECRET")
	}

	db, err := database.Connect(cfg.DSN())
	if err != nil {
		log.Fatalf("鏁版嵁搴撹繛鎺ュけ璐? %v", err)
	}
	defer db.Close()

	if err := database.InitTables(db); err != nil {
		log.Fatalf("鏁版嵁搴撳缓琛ㄥけ璐? %v", err)
	}

	if !cfg.AppDebug {
		gin.SetMode(gin.ReleaseMode)
	}
	r := gin.Default()

	r.Use(cors.New(cors.Config{
		AllowOrigins:     corsOrigins(),
		AllowMethods:     []string{"GET", "POST", "PUT", "DELETE", "OPTIONS"},
		AllowHeaders:     []string{"Origin", "Content-Type", "Authorization"},
		ExposeHeaders:    []string{"Content-Length"},
		AllowCredentials: true,
		MaxAge:           12 * time.Hour,
	}))

	authHandler := handler.NewAuthHandler()
	powerHandler := handler.NewPowerHandler(db)
	alertHandler := handler.NewAlertHandler(db)
	adminHandler := handler.NewAdminHandler()
	systemHandler := handler.NewSystemHandler(db)

	r.GET("/health", handler.Health)

	api := r.Group("/api")
	{
		auth := api.Group("/auth")
		{
			auth.POST("/login", authHandler.Login)
		}

		// === 鏅€氱敤鎴峰彲璁块棶锛堥渶瑕佽璇侊級 ===
		userProtected := api.Group("")
		userProtected.Use(handler.AuthMiddleware())
		{
			userProtected.GET("/power/records/:dorm_number/latest", powerHandler.GetLatest)
			userProtected.GET("/power/records/:dorm_number", powerHandler.GetRecords)
			userProtected.GET("/alert/rules/:dorm_number", alertHandler.GetRule)
			userProtected.GET("/alert/logs", alertHandler.GetLogs)
			userProtected.GET("/alert/config", alertHandler.GetConfig)
		}

		// === 浠呯鐞嗗憳鍙闂紙闇€瑕佽璇?+ admin 瑙掕壊锛?===
		adminProtected := api.Group("")
		adminProtected.Use(handler.AuthMiddleware())
		adminProtected.Use(handler.AdminOnly())
		{
			// 鐢甸噺璁板綍鍐欏叆
			adminProtected.POST("/power/records", powerHandler.Create)

			// 鍛婅瑙勫垯绠＄悊
			adminProtected.POST("/alert/rules", alertHandler.CreateRule)
			adminProtected.PUT("/alert/rules/:dorm_number", alertHandler.UpdateRule)
			adminProtected.DELETE("/alert/rules/:dorm_number", alertHandler.DeleteRule)

			// 绠＄悊鍛樿缃?
			adminProtected.GET("/admin/settings", adminHandler.GetSettings)
			adminProtected.PUT("/admin/settings", adminHandler.UpdateSettings)
			adminProtected.GET("/admin/qq-config", adminHandler.GetQQConfig)

			// 绯荤粺鎿嶄綔
			adminProtected.POST("/system/crawl", systemHandler.ManualCrawl)
			adminProtected.POST("/system/report", systemHandler.SendReport)
			adminProtected.GET("/system/qq-status", systemHandler.QQStatus)
		}
	}

	crawlerSvc := service.NewCrawlerService(db)
	sched := scheduler.New(crawlerSvc)
	sched.Start()
	defer sched.Stop()

	go func() {
		time.Sleep(3 * time.Second)
		log.Println("鍚姩鏃舵墽琛岄娆℃姄鍙?..")
		crawlerSvc.CrawlAndSave(false, false)
	}()

	addr := ":" + cfg.ServerPort
	log.Printf("DormGuard Go 鏈嶅姟鍚姩鍦?%s", addr)
	if err := r.Run(addr); err != nil {
		log.Fatalf("鏈嶅姟鍣ㄥ惎鍔ㄥけ璐? %v", err)
	}
}