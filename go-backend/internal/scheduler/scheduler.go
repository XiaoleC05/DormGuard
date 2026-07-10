package scheduler

import (
	"log"
	"strconv"
	"time"

	"github.com/XiaoleC05/dormguard-go/internal/config"
	"github.com/XiaoleC05/dormguard-go/internal/service"
	"github.com/robfig/cron/v3"
)

type Scheduler struct {
	c              *cron.Cron
	crawlerService *service.CrawlerService
}

func New(crawlerSvc *service.CrawlerService) *Scheduler {
	return &Scheduler{
		c:              cron.New(),
		crawlerService: crawlerSvc,
	}
}

func (s *Scheduler) Start() {
	cfg := config.Cfg
	interval := cfg.SchedulerIntervalHours

	spec := "@every " + strconv.Itoa(interval) + "h"
	_, err := s.c.AddFunc(spec, func() {
		log.Println("定时任务: 开始抓取电费数据")
		s.crawlerService.CrawlAndSave(false, false)
		log.Println("定时任务: 抓取完成")
	})

	if err != nil {
		log.Printf("添加定时任务失败: %v", err)
		return
	}

	s.c.Start()
	log.Printf("定时任务已启动: 每 %d 小时执行一次", interval)

	// 启动后延迟 3 秒执行一次
	go func() {
		time.Sleep(3 * time.Second)
		log.Println("启动时执行首次抓取...")
		s.crawlerService.CrawlAndSave(false, false)
	}()
}

func (s *Scheduler) Stop() {
	s.c.Stop()
	log.Println("定时任务已停止")
}
