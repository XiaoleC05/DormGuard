package model

import (
	"time"
)

type PowerRecord struct {
	ID                int64      `json:"id" db:"id"`
	DormNumber        string     `json:"dorm_number" db:"dorm_number"`
	Balance           float64    `json:"balance" db:"balance"`
	KBalance          *float64   `json:"kbalance,omitempty" db:"kbalance"`
	ZBalance          *float64   `json:"zbalance,omitempty" db:"zbalance"`
	KPowerConsumption *float64   `json:"kpower_consumption,omitempty" db:"kpower_consumption"`
	ZPowerConsumption *float64   `json:"zpower_consumption,omitempty" db:"zpower_consumption"`
	PowerConsumption  *float64   `json:"power_consumption,omitempty" db:"power_consumption"`
	RecordTime        time.Time  `json:"record_time" db:"record_time"`
	CreatedAt         time.Time  `json:"created_at" db:"created_at"`
}

type AlertRule struct {
	ID            int64      `json:"id" db:"id"`
	DormNumber    string     `json:"dorm_number" db:"dorm_number"`
	RoomID        *string    `json:"room_id,omitempty" db:"room_id"`
	KThreshold    *float64   `json:"kthreshold,omitempty" db:"kthreshold"`
	ZThreshold    *float64   `json:"zthreshold,omitempty" db:"zthreshold"`
	Enabled       bool       `json:"enabled" db:"enabled"`
	QQEnabled     bool       `json:"qq_enabled" db:"qq_enabled"`
	LastAlertTime *time.Time `json:"last_alert_time,omitempty" db:"last_alert_time"`
	CreatedAt     time.Time  `json:"created_at" db:"created_at"`
	UpdatedAt     time.Time  `json:"updated_at" db:"updated_at"`
}

type AlertLog struct {
	ID            int64     `json:"id" db:"id"`
	DormNumber    string    `json:"dorm_number" db:"dorm_number"`
	AlertCategory *string   `json:"alert_category,omitempty" db:"alert_category"`
	Balance       float64   `json:"balance" db:"balance"`
	Threshold     float64   `json:"threshold" db:"threshold"`
	AlertType     string    `json:"alert_type" db:"alert_type"`
	AlertStatus   string    `json:"alert_status" db:"alert_status"`
	AlertMessage  *string   `json:"alert_message,omitempty" db:"alert_message"`
	CreatedAt     time.Time `json:"created_at" db:"created_at"`
}

// Request/Response DTOs
type PowerRecordCreate struct {
	DormNumber string   `json:"dorm_number" binding:"required"`
	Balance    float64  `json:"balance"`
	KBalance   *float64 `json:"kbalance,omitempty"`
	ZBalance   *float64 `json:"zbalance,omitempty"`
}

type PowerRecordListResponse struct {
	Items []PowerRecord `json:"items"`
	Total int           `json:"total"`
}

type AlertRuleCreate struct {
	DormNumber string   `json:"dorm_number" binding:"required"`
	RoomID     *string  `json:"room_id,omitempty"`
	KThreshold *float64 `json:"kthreshold,omitempty"`
	ZThreshold *float64 `json:"zthreshold,omitempty"`
	Enabled    *bool    `json:"enabled,omitempty"`
	QQEnabled  *bool    `json:"qq_enabled,omitempty"`
}

type AlertRuleUpdate struct {
	RoomID     *string  `json:"room_id,omitempty"`
	KThreshold *float64 `json:"kthreshold,omitempty"`
	ZThreshold *float64 `json:"zthreshold,omitempty"`
	Enabled    *bool    `json:"enabled,omitempty"`
	QQEnabled  *bool    `json:"qq_enabled,omitempty"`
}

type LoginRequest struct {
	Username string `json:"username" binding:"required"`
	Password string `json:"password" binding:"required"`
}

type LoginResponse struct {
	AccessToken string `json:"access_token"`
	TokenType   string `json:"token_type"`
	Username    string `json:"username"`
}

type SettingsResponse struct {
	Settings        map[string]string `json:"settings"`
	RestartRequired bool              `json:"restart_required"`
}

type SettingsUpdateRequest struct {
	Settings map[string]string `json:"settings"`
}
