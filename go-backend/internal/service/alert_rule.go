package service

import (
	"database/sql"
	"time"

	"github.com/XiaoleC05/dormguard-go/internal/model"
)

type AlertRuleService struct {
	db *sql.DB
}

func NewAlertRuleService(db *sql.DB) *AlertRuleService {
	return &AlertRuleService{db: db}
}

func (s *AlertRuleService) GetEnabledRules() ([]model.AlertRule, error) {
	rows, err := s.db.Query(
		`SELECT id, dorm_number, room_id, kthreshold, zthreshold, enabled, qq_enabled, last_alert_time, created_at, updated_at
		 FROM alert_rules WHERE enabled = 1`,
	)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var rules []model.AlertRule
	for rows.Next() {
		var rule model.AlertRule
		if err := rows.Scan(
			&rule.ID, &rule.DormNumber, &rule.RoomID,
			&rule.KThreshold, &rule.ZThreshold,
			&rule.Enabled, &rule.QQEnabled,
			&rule.LastAlertTime, &rule.CreatedAt, &rule.UpdatedAt,
		); err != nil {
			return nil, err
		}
		rules = append(rules, rule)
	}
	return rules, nil
}

func (s *AlertRuleService) GetAllRules() ([]model.AlertRule, error) {
	rows, err := s.db.Query(
		`SELECT id, dorm_number, room_id, kthreshold, zthreshold, enabled, qq_enabled, last_alert_time, created_at, updated_at
		 FROM alert_rules`,
	)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var rules []model.AlertRule
	for rows.Next() {
		var rule model.AlertRule
		if err := rows.Scan(
			&rule.ID, &rule.DormNumber, &rule.RoomID,
			&rule.KThreshold, &rule.ZThreshold,
			&rule.Enabled, &rule.QQEnabled,
			&rule.LastAlertTime, &rule.CreatedAt, &rule.UpdatedAt,
		); err != nil {
			return nil, err
		}
		rules = append(rules, rule)
	}
	return rules, nil
}

func (s *AlertRuleService) GetRule(dormNumber string) (*model.AlertRule, error) {
	row := s.db.QueryRow(
		`SELECT id, dorm_number, room_id, kthreshold, zthreshold, enabled, qq_enabled, last_alert_time, created_at, updated_at
		 FROM alert_rules WHERE dorm_number = ?`,
		dormNumber,
	)

	var rule model.AlertRule
	err := row.Scan(
		&rule.ID, &rule.DormNumber, &rule.RoomID,
		&rule.KThreshold, &rule.ZThreshold,
		&rule.Enabled, &rule.QQEnabled,
		&rule.LastAlertTime, &rule.CreatedAt, &rule.UpdatedAt,
	)
	if err != nil {
		return nil, err
	}
	return &rule, nil
}

func (s *AlertRuleService) CreateRule(req model.AlertRuleCreate) (*model.AlertRule, error) {
	now := time.Now()
	enabled := true
	if req.Enabled != nil {
		enabled = *req.Enabled
	}
	qqEnabled := false
	if req.QQEnabled != nil {
		qqEnabled = *req.QQEnabled
	}

	rule := &model.AlertRule{
		DormNumber: req.DormNumber,
		RoomID:     req.RoomID,
		KThreshold: req.KThreshold,
		ZThreshold: req.ZThreshold,
		Enabled:    enabled,
		QQEnabled:  qqEnabled,
		CreatedAt:  now,
		UpdatedAt:  now,
	}

	result, err := s.db.Exec(
		`INSERT INTO alert_rules (dorm_number, room_id, kthreshold, zthreshold, enabled, qq_enabled, created_at, updated_at)
		 VALUES (?, ?, ?, ?, ?, ?, ?, ?)`,
		rule.DormNumber, rule.RoomID, rule.KThreshold, rule.ZThreshold,
		rule.Enabled, rule.QQEnabled, rule.CreatedAt, rule.UpdatedAt,
	)
	if err != nil {
		return nil, err
	}

	id, _ := result.LastInsertId()
	rule.ID = id
	return rule, nil
}

func (s *AlertRuleService) UpdateRule(dormNumber string, req model.AlertRuleUpdate) (*model.AlertRule, error) {
	existing, err := s.GetRule(dormNumber)
	if err != nil {
		return nil, err
	}

	sets := ""
	args := []interface{}{}
	sep := ""

	if req.RoomID != nil {
		sets += sep + "room_id = ?"
		args = append(args, *req.RoomID)
		sep = ", "
	}
	if req.KThreshold != nil {
		sets += sep + "kthreshold = ?"
		args = append(args, *req.KThreshold)
		sep = ", "
	}
	if req.ZThreshold != nil {
		sets += sep + "zthreshold = ?"
		args = append(args, *req.ZThreshold)
		sep = ", "
	}
	if req.Enabled != nil {
		sets += sep + "enabled = ?"
		args = append(args, *req.Enabled)
		sep = ", "
	}
	if req.QQEnabled != nil {
		sets += sep + "qq_enabled = ?"
		args = append(args, *req.QQEnabled)
		sep = ", "
	}

	if sets == "" {
		return existing, nil
	}

	sets += ", updated_at = ?"
	args = append(args, time.Now())
	args = append(args, existing.ID)

	_, err = s.db.Exec("UPDATE alert_rules SET "+sets+" WHERE id = ?", args...)
	if err != nil {
		return nil, err
	}

	return s.GetRule(dormNumber)
}

func (s *AlertRuleService) DeleteRule(dormNumber string) (bool, error) {
	result, err := s.db.Exec(
		`DELETE FROM alert_rules WHERE dorm_number = ?`,
		dormNumber,
	)
	if err != nil {
		return false, err
	}
	affected, _ := result.RowsAffected()
	return affected > 0, nil
}
