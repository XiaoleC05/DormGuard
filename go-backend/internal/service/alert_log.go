package service

import (
	"database/sql"
	"time"

	"github.com/XiaoleC05/dormguard-go/internal/model"
)

type AlertLogService struct {
	db *sql.DB
}

func NewAlertLogService(db *sql.DB) *AlertLogService {
	return &AlertLogService{db: db}
}

func (s *AlertLogService) GetLogs(dormNumber *string, limit int) ([]model.AlertLog, error) {
	var rows *sql.Rows
	var err error

	if dormNumber != nil && *dormNumber != "" {
		rows, err = s.db.Query(
			`SELECT id, dorm_number, alert_type, alert_category, balance, threshold, alert_message, alert_status, created_at
			 FROM alert_logs WHERE dorm_number = ? ORDER BY created_at DESC LIMIT ?`,
			*dormNumber, limit,
		)
	} else {
		rows, err = s.db.Query(
			`SELECT id, dorm_number, alert_type, alert_category, balance, threshold, alert_message, alert_status, created_at
			 FROM alert_logs ORDER BY created_at DESC LIMIT ?`,
			limit,
		)
	}
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var logs []model.AlertLog
	for rows.Next() {
		var l model.AlertLog
		if err := rows.Scan(
			&l.ID, &l.DormNumber, &l.AlertType, &l.AlertCategory,
			&l.Balance, &l.Threshold, &l.AlertMessage, &l.AlertStatus,
			&l.CreatedAt,
		); err != nil {
			return nil, err
		}
		logs = append(logs, l)
	}
	return logs, nil
}

func (s *AlertLogService) CreateLog(log model.AlertLog) error {
	log.CreatedAt = time.Now()
	_, err := s.db.Exec(
		`INSERT INTO alert_logs (dorm_number, alert_type, alert_category, balance, threshold, alert_message, alert_status, created_at)
		 VALUES (?, ?, ?, ?, ?, ?, ?, ?)`,
		log.DormNumber, log.AlertType, log.AlertCategory,
		log.Balance, log.Threshold, log.AlertMessage, log.AlertStatus, log.CreatedAt,
	)
	return err
}

func (s *AlertLogService) GetLastSuccessLog(dormNumber, category, alertType string) (*model.AlertLog, error) {
	row := s.db.QueryRow(
		`SELECT id, dorm_number, alert_type, alert_category, balance, threshold, alert_message, alert_status, created_at
		 FROM alert_logs
		 WHERE dorm_number = ? AND alert_category = ? AND alert_type = ? AND alert_status = 'success'
		 ORDER BY created_at DESC LIMIT 1`,
		dormNumber, category, alertType,
	)

	var l model.AlertLog
	err := row.Scan(
		&l.ID, &l.DormNumber, &l.AlertType, &l.AlertCategory,
		&l.Balance, &l.Threshold, &l.AlertMessage, &l.AlertStatus,
		&l.CreatedAt,
	)
	if err != nil {
		return nil, err
	}
	return &l, nil
}
