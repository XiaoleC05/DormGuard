package service

import (
	"database/sql"
	"time"

	"github.com/XiaoleC05/dormguard-go/internal/model"
)

type PowerRecordService struct {
	db *sql.DB
}

func NewPowerRecordService(db *sql.DB) *PowerRecordService {
	return &PowerRecordService{db: db}
}

func (s *PowerRecordService) CreateRecord(req model.PowerRecordCreate) (*model.PowerRecord, error) {
	last, _ := s.GetLatestRecord(req.DormNumber)

	var kConsumption, zConsumption *float64
	if last != nil {
		if req.KBalance != nil && last.KBalance != nil {
			diff := *req.KBalance - *last.KBalance
			kConsumption = &diff
		}
		if req.ZBalance != nil && last.ZBalance != nil {
			diff := *req.ZBalance - *last.ZBalance
			zConsumption = &diff
		}
	}

	now := time.Now()
	record := &model.PowerRecord{
		DormNumber:        req.DormNumber,
		Balance:           req.Balance,
		KBalance:          req.KBalance,
		ZBalance:          req.ZBalance,
		KPowerConsumption: kConsumption,
		ZPowerConsumption: zConsumption,
		RecordTime:        now,
		CreatedAt:         now,
	}

	_, err := s.db.Exec(
		`INSERT INTO power_records (dorm_number, balance, kbalance, zbalance, kpower_consumption, zpower_consumption, record_time, created_at)
		 VALUES (?, ?, ?, ?, ?, ?, ?, ?)`,
		record.DormNumber, record.Balance, record.KBalance, record.ZBalance,
		record.KPowerConsumption, record.ZPowerConsumption, record.RecordTime, record.CreatedAt,
	)
	if err != nil {
		return nil, err
	}

	return record, nil
}

func (s *PowerRecordService) GetLatestRecord(dormNumber string) (*model.PowerRecord, error) {
	row := s.db.QueryRow(
		`SELECT id, dorm_number, balance, kbalance, zbalance, kpower_consumption, zpower_consumption, record_time, created_at
		 FROM power_records WHERE dorm_number = ? ORDER BY record_time DESC LIMIT 1`,
		dormNumber,
	)

	var r model.PowerRecord
	err := row.Scan(
		&r.ID, &r.DormNumber, &r.Balance,
		&r.KBalance, &r.ZBalance,
		&r.KPowerConsumption, &r.ZPowerConsumption,
		&r.RecordTime, &r.CreatedAt,
	)
	if err != nil {
		return nil, err
	}
	return &r, nil
}

func (s *PowerRecordService) GetRecords(dormNumber string, limit, offset int) ([]model.PowerRecord, error) {
	rows, err := s.db.Query(
		`SELECT id, dorm_number, balance, kbalance, zbalance, kpower_consumption, zpower_consumption, record_time, created_at
		 FROM power_records WHERE dorm_number = ? ORDER BY record_time DESC LIMIT ? OFFSET ?`,
		dormNumber, limit, offset,
	)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var records []model.PowerRecord
	for rows.Next() {
		var r model.PowerRecord
		if err := rows.Scan(
			&r.ID, &r.DormNumber, &r.Balance,
			&r.KBalance, &r.ZBalance,
			&r.KPowerConsumption, &r.ZPowerConsumption,
			&r.RecordTime, &r.CreatedAt,
		); err != nil {
			return nil, err
		}
		records = append(records, r)
	}
	return records, nil
}

func (s *PowerRecordService) CountRecords(dormNumber string) (int, error) {
	var count int
	err := s.db.QueryRow(
		`SELECT COUNT(*) FROM power_records WHERE dorm_number = ?`,
		dormNumber,
	).Scan(&count)
	return count, err
}
