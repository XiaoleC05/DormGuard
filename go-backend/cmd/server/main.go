package main

import (
	"log"
	"time"

	"github.com/XiaoleC05/dormguard-go/internal/config"
	"github.com/XiaoleC05/dormguard-go/internal/database"
	"github.com/XiaoleC05/dormguard-go/internal/handler"
	"github.com/XiaoleC05/dormguard-go/internal/scheduler"
	"github.com/XiaoleC05/dormguard-go/internal/service"
	"github.com/gin-contrib/cors"
	"github.com/gin-gonic/gin"
)

func main() {
	cfg := config.Load()

	db, err := database.Connect(cfg.DSN())
	if err != nil {
		log.Fatalf("数据库连接失败: %v", err)
	}
	defer db.Close()

	if err := database.InitTables(db); err != nil {
		log.Fatalf("数据库建表失败: %v", err)
	}

	if !cfg.AppDebug {
		gin.SetMode(gin.ReleaseMode)
	}
	r := gin.Default()

	r.Use(cors.New(cors.Config{
		AllowOrigins:     []string{"*"},
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

		// === 普通用户可访问（需要认证） ===
		userProtected := api.Group("")
		userProtected.Use(handler.AuthMiddleware())
		{
			userProtected.GET("/power/records/:dorm_number/latest", powerHandler.GetLatest)
			userProtected.GET("/power/records/:dorm_number", powerHandler.GetRecords)
			userProtected.GET("/alert/rules/:dorm_number", alertHandler.GetRule)
			userProtected.GET("/alert/logs", alertHandler.GetLogs)
			userProtected.GET("/alert/config", alertHandler.GetConfig)
		}

		// === 仅管理员可访问（需要认证 + admin 角色） ===
		adminProtected := api.Group("")
		adminProtected.Use(handler.AuthMiddleware())
		adminProtected.Use(handler.AdminOnly())
		{
			// 电量记录写入
			adminProtected.POST("/power/records", powerHandler.Create)

			// 告警规则管理
			adminProtected.POST("/alert/rules", alertHandler.CreateRule)
			adminProtected.PUT("/alert/rules/:dorm_number", alertHandler.UpdateRule)
			adminProtected.DELETE("/alert/rules/:dorm_number", alertHandler.DeleteRule)

			// 管理员设置
			adminProtected.GET("/admin/settings", adminHandler.GetSettings)
			adminProtected.PUT("/admin/settings", adminHandler.UpdateSettings)
			adminProtected.GET("/admin/qq-config", adminHandler.GetQQConfig)

			// 系统操作
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
		log.Println("启动时执行首次抓取...")
		crawlerSvc.CrawlAndSave(false, false)
	}()

	addr := ":" + cfg.ServerPort
	log.Printf("DormGuard Go 服务启动在 %s", addr)
	if err := r.Run(addr); err != nil {
		log.Fatalf("服务器启动失败: %v", err)
	}
}
