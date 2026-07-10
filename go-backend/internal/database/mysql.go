package database

import (
	"database/sql"
	"fmt"
	"log"

	_ "github.com/go-sql-driver/mysql"
)

var DB *sql.DB

func Connect(dsn string) (*sql.DB, error) {
	db, err := sql.Open("mysql", dsn)
	if err != nil {
		return nil, fmt.Errorf("数据库连接失败: %w", err)
	}

	db.SetMaxOpenConns(10)
	db.SetMaxIdleConns(5)
	db.SetConnMaxLifetime(3600e9) // 1 hour

	if err := db.Ping(); err != nil {
		return nil, fmt.Errorf("数据库 ping 失败: %w", err)
	}

	DB = db
	log.Println("MySQL 连接成功")
	return db, nil
}

func InitTables(db *sql.DB) error {
	stmts := []string{
		`CREATE TABLE IF NOT EXISTS power_records (
			id BIGINT AUTO_INCREMENT PRIMARY KEY,
			dorm_number VARCHAR(50) NOT NULL,
			balance DOUBLE NOT NULL,
			kbalance DOUBLE DEFAULT NULL,
			zbalance DOUBLE DEFAULT NULL,
			kpower_consumption DOUBLE DEFAULT NULL,
			zpower_consumption DOUBLE DEFAULT NULL,
			power_consumption DOUBLE DEFAULT NULL,
			record_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
			created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
			INDEX idx_dorm_number (dorm_number),
			INDEX idx_record_time (record_time)
		) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4`,
		`CREATE TABLE IF NOT EXISTS alert_rules (
			id BIGINT AUTO_INCREMENT PRIMARY KEY,
			dorm_number VARCHAR(50) NOT NULL UNIQUE,
			room_id VARCHAR(50) DEFAULT NULL,
			kthreshold DOUBLE DEFAULT NULL,
			zthreshold DOUBLE DEFAULT NULL,
			enabled TINYINT(1) NOT NULL DEFAULT 1,
			qq_enabled TINYINT(1) NOT NULL DEFAULT 0,
			last_alert_time DATETIME DEFAULT NULL,
			created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
			updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
			INDEX idx_enabled (enabled)
		) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4`,
		`CREATE TABLE IF NOT EXISTS alert_logs (
			id BIGINT AUTO_INCREMENT PRIMARY KEY,
			dorm_number VARCHAR(50) NOT NULL,
			alert_category VARCHAR(20) DEFAULT NULL,
			balance DOUBLE NOT NULL,
			threshold DOUBLE NOT NULL,
			alert_type VARCHAR(20) NOT NULL,
			alert_status VARCHAR(20) NOT NULL,
			alert_message TEXT DEFAULT NULL,
			created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
			INDEX idx_dorm_number (dorm_number),
			INDEX idx_created_at (created_at)
		) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4`,
	}

	for _, stmt := range stmts {
		if _, err := db.Exec(stmt); err != nil {
			return fmt.Errorf("建表失败: %w", err)
		}
	}
	log.Println("数据库表初始化完成")
	return nil
}
