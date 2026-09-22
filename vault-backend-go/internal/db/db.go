package db

import (
	"context"
	"errors"
	"fmt"
	"os"
	"time"

	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgxpool"
)

type Database struct {
	Pool *pgxpool.Pool
}

func NewConnection() (*Database, error) {
	user := os.Getenv("DB_USER")
	password := os.Getenv("DB_PASSWORD")
	host := os.Getenv("DB_HOST")
	port := os.Getenv("DB_PORT")
	dbname := os.Getenv("DB_NAME")

	if host == "" {
		host = "localhost"
	}
	if port == "" {
		port = "5439"
	}

	connStr := fmt.Sprintf("postgres://%s:%s@%s:%s/%s?sslmode=disable",
		user, password, host, port, dbname)

	config, err := pgxpool.ParseConfig(connStr)
	if err != nil {
		return nil, fmt.Errorf("unable to parse connection string: %v", err)
	}

	ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
	defer cancel()

	pool, err := pgxpool.NewWithConfig(ctx, config)
	if err != nil {
		fmt.Printf("Postgres connection failed, falling back to local storage: %v\n", err)
		return nil, nil // Indicate fallback needed
	}

	// Ping to verify
	if err := pool.Ping(ctx); err != nil {
		fmt.Printf("Postgres ping failed, falling back to local storage: %v\n", err)
		return nil, nil
	}

	return &Database{Pool: pool}, nil
}

func (db *Database) InitSchema(ctx context.Context) error {
	queries := []string{
		`CREATE TABLE IF NOT EXISTS devices (
			id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
			public_key TEXT UNIQUE NOT NULL,
			name TEXT NOT NULL,
			os TEXT NOT NULL,
			status TEXT NOT NULL DEFAULT 'secure',
			last_active TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
			last_root_blob_id TEXT
		)`,
		`ALTER TABLE devices ADD COLUMN IF NOT EXISTS last_root_blob_id TEXT`,
		`CREATE TABLE IF NOT EXISTS activity_logs (
			id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
			device_public_key TEXT NOT NULL,
			event_type TEXT NOT NULL,
			title TEXT NOT NULL,
			description TEXT NOT NULL,
			risk_level TEXT NOT NULL DEFAULT 'low',
			timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
		)`,
		`CREATE TABLE IF NOT EXISTS blobs (
			blob_id TEXT PRIMARY KEY,
			owner_public_key TEXT NOT NULL,
			size_bytes BIGINT NOT NULL,
			created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
		)`,
		`CREATE TABLE IF NOT EXISTS company_licenses (
			id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
			company_name TEXT NOT NULL,
			tier TEXT NOT NULL,
			tier_display TEXT NOT NULL,
			setup_fee_gbp NUMERIC(10, 2) NOT NULL,
			per_user_monthly_gbp NUMERIC(10, 2) NOT NULL,
			max_seats INT NOT NULL,
			admin_key TEXT UNIQUE NOT NULL,
			user_key TEXT UNIQUE NOT NULL,
			status TEXT NOT NULL DEFAULT 'active',
			created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
		)`,
		`CREATE TABLE IF NOT EXISTS license_seats (
			id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
			license_id UUID REFERENCES company_licenses(id) ON DELETE CASCADE,
			role TEXT NOT NULL,
			name TEXT NOT NULL,
			email TEXT NOT NULL,
			device_id TEXT NOT NULL,
			device_os TEXT NOT NULL DEFAULT 'Windows',
			status TEXT NOT NULL DEFAULT 'active',
			storage_used_bytes BIGINT NOT NULL DEFAULT 0,
			created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
			last_active TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
			UNIQUE(license_id, email, device_id)
		)`,
	}

	for _, q := range queries {
		if _, err := db.Pool.Exec(ctx, q); err != nil {
			return fmt.Errorf("failed to execute schema query: %v", err)
		}
	}

	// Seed default enterprise licenses if none exist
	var count int
	_ = db.Pool.QueryRow(ctx, "SELECT COUNT(*) FROM company_licenses").Scan(&count)
	if count == 0 {
		seedQuery := `INSERT INTO company_licenses 
			(company_name, tier, tier_display, setup_fee_gbp, per_user_monthly_gbp, max_seats, admin_key, user_key)
			VALUES 
			('Acme Health Corp', 'enterprise_1_5', 'Enterprise 1–5 seats (£6,000 one-time + £9/user/mo)', 6000.00, 9.00, 5, 'SV-ADM-ACME-5527', 'SV-USR-ACME-5527'),
			('NHS Trust Alliance', 'enterprise_6_50', 'Enterprise 6–50 seats (£9,000 one-time + £9/user/mo)', 9000.00, 9.00, 25, 'SV-ADM-NHS-7738', 'SV-USR-NHS-7738'),
			('Solo Practice', 'individual', 'Individual (£2,000 one-time + £12/mo)', 2000.00, 12.00, 1, 'SV-ADM-SOLO-1029', 'SV-USR-SOLO-1029')`
		_, _ = db.Pool.Exec(ctx, seedQuery)
	}

	return nil
}

func (db *Database) RegisterOrUpdateDevice(ctx context.Context, pk, name, os string) error {
	q := `INSERT INTO devices (public_key, name, os, last_active) 
		  VALUES ($1, $2, $3, CURRENT_TIMESTAMP)
		  ON CONFLICT (public_key) DO UPDATE SET last_active = CURRENT_TIMESTAMP, name = $2, os = $3`
	_, err := db.Pool.Exec(ctx, q, pk, name, os)
	return err
}

func (db *Database) GetDevices(ctx context.Context) ([]map[string]interface{}, error) {
	rows, err := db.Pool.Query(ctx, "SELECT name, os, status, last_active, public_key FROM devices ORDER BY last_active DESC")
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var devices []map[string]interface{}
	for rows.Next() {
		var name, os, status, pk string
		var lastActive time.Time
		if err := rows.Scan(&name, &os, &status, &lastActive, &pk); err != nil {
			return nil, err
		}
		devices = append(devices, map[string]interface{}{
			"name":        name,
			"os":          os,
			"status":      status,
			"last_active": lastActive.Format(time.RFC3339),
			"public_key":  pk,
		})
	}
	return devices, nil
}

func (db *Database) DeleteDevice(ctx context.Context, pk string) error {
	_, err := db.Pool.Exec(ctx, "DELETE FROM devices WHERE public_key = $1", pk)
	return err
}

func (db *Database) DeleteDevicesByNameAndOS(ctx context.Context, name, os string) error {
	_, err := db.Pool.Exec(ctx, "DELETE FROM devices WHERE name = $1 AND os = $2", name, os)
	return err
}

func (db *Database) LogActivity(ctx context.Context, pk, eventType, title, desc, risk string) error {
	q := `INSERT INTO activity_logs (device_public_key, event_type, title, description, risk_level) 
		  VALUES ($1, $2, $3, $4, $5)`
	_, err := db.Pool.Exec(ctx, q, pk, eventType, title, desc, risk)
	return err
}

func (db *Database) GetActivityLogs(ctx context.Context) ([]map[string]interface{}, error) {
	rows, err := db.Pool.Query(ctx, "SELECT device_public_key, event_type, title, description, risk_level, timestamp FROM activity_logs ORDER BY timestamp DESC LIMIT 50")
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var logs []map[string]interface{}
	for rows.Next() {
		var dpk, et, title, desc, risk string
		var ts time.Time
		if err := rows.Scan(&dpk, &et, &title, &desc, &risk, &ts); err != nil {
			return nil, err
		}
		logs = append(logs, map[string]interface{}{
			"device_public_key": dpk,
			"type":              et,
			"title":             title,
			"description":       desc,
			"risk":              risk,
			"time":              ts.Format(time.RFC3339),
		})
	}
	return logs, nil
}

func (db *Database) RecordBlobOwnership(ctx context.Context, blobID, pk string, size int64) error {
	q := `INSERT INTO blobs (blob_id, owner_public_key, size_bytes) VALUES ($1, $2, $3)
		  ON CONFLICT (blob_id) DO UPDATE SET size_bytes = $3`
	_, err := db.Pool.Exec(ctx, q, blobID, pk, size)
	return err
}

func (db *Database) GetUserStorageStats(ctx context.Context, pk string) (int, int64, error) {
	var count int
	var size int64
	q := `SELECT COUNT(*), COALESCE(SUM(size_bytes), 0) FROM blobs WHERE owner_public_key = $1`
	err := db.Pool.QueryRow(ctx, q, pk).Scan(&count, &size)
	return count, size, err
}

func (db *Database) GetBlobOwner(ctx context.Context, blobID string) (string, error) {
	var owner string
	err := db.Pool.QueryRow(ctx, "SELECT owner_public_key FROM blobs WHERE blob_id = $1", blobID).Scan(&owner)
	return owner, err
}

func (db *Database) DeleteBlobOwnership(ctx context.Context, blobID string) error {
	_, err := db.Pool.Exec(ctx, "DELETE FROM blobs WHERE blob_id = $1", blobID)
	return err
}

func (db *Database) SetRootBlob(ctx context.Context, pk, blobID string) error {
	_, err := db.Pool.Exec(ctx, "UPDATE devices SET last_root_blob_id = $1 WHERE public_key = $2", blobID, pk)
	return err
}

func (db *Database) GetRootBlob(ctx context.Context, pk string) (string, error) {
	var id string
	err := db.Pool.QueryRow(ctx, "SELECT COALESCE(last_root_blob_id, '') FROM devices WHERE public_key = $1", pk).Scan(&id)
	if err != nil {
		if errors.Is(err, pgx.ErrNoRows) {
			return "", nil
		}
		return "", err
	}
	return id, nil
}

func (db *Database) Close() {
	db.Pool.Close()
}

func (db *Database) Ping(ctx context.Context) error {
	return db.Pool.Ping(ctx)
}

// --- Enterprise License Management ---

type SeatActivationResult struct {
	Valid             bool    `json:"valid"`
	Message           string  `json:"message"`
	LicenseID         string  `json:"license_id"`
	Role              string  `json:"role"` // "admin" | "user"
	CompanyName       string  `json:"company_name"`
	Tier              string  `json:"tier"`
	TierDisplay       string  `json:"tier_display"`
	SetupFeeGBP       float64 `json:"setup_fee_gbp"`
	PerUserMonthlyGBP float64 `json:"per_user_monthly_gbp"`
	MaxSeats          int     `json:"max_seats"`
	ActiveSeats       int     `json:"active_seats"`
	AdminCount        int     `json:"admin_count"`
	UserCount         int     `json:"user_count"`
	SeatID            string  `json:"seat_id"`
}

type AdminDashboardSeat struct {
	ID             string `json:"id"`
	Role           string `json:"role"`
	Name           string `json:"name"`
	Email          string `json:"email"`
	DeviceID       string `json:"device_id"`
	DeviceOS       string `json:"device_os"`
	Status         string `json:"status"`
	StorageUsedStr string `json:"storage_used_str"`
	StorageBytes   int64  `json:"storage_bytes"`
	LastActive     string `json:"last_active"`
	CreatedAt      string `json:"created_at"`
}

type AdminDashboardView struct {
	CompanyName       string               `json:"company_name"`
	Tier              string               `json:"tier"`
	TierDisplay       string               `json:"tier_display"`
	SetupFeeGBP       float64              `json:"setup_fee_gbp"`
	PerUserMonthlyGBP float64              `json:"per_user_monthly_gbp"`
	MonthlyRunRateGBP float64              `json:"monthly_run_rate_gbp"`
	MaxSeats          int                  `json:"max_seats"`
	TotalActiveSeats  int                  `json:"total_active_seats"`
	AdminCount        int                  `json:"admin_count"`
	UserCount         int                  `json:"user_count"`
	RemainingSeats    int                  `json:"remaining_seats"`
	Seats             []AdminDashboardSeat `json:"seats"`
}

func formatBytes(b int64) string {
	const unit = 1024
	if b < unit {
		return fmt.Sprintf("%d B", b)
	}
	div, exp := int64(unit), 0
	for n := b / unit; n >= unit; n /= unit {
		div *= unit
		exp++
	}
	return fmt.Sprintf("%.1f %cB", float64(b)/float64(div), "KMGTPE"[exp])
}

func (db *Database) VerifyAndActivateSeat(ctx context.Context, key, name, email, deviceID, deviceOS string) (*SeatActivationResult, error) {
	var licenseID, companyName, tier, tierDisplay, adminKey, userKey, status string
	var setupFee, perUserFee float64
	var maxSeats int

	err := db.Pool.QueryRow(ctx, `SELECT id, company_name, tier, tier_display, setup_fee_gbp, per_user_monthly_gbp, max_seats, admin_key, user_key, status
		FROM company_licenses 
		WHERE (admin_key = $1 OR user_key = $1)`, key).Scan(
		&licenseID, &companyName, &tier, &tierDisplay, &setupFee, &perUserFee, &maxSeats, &adminKey, &userKey, &status,
	)
	if err != nil {
		if errors.Is(err, pgx.ErrNoRows) {
			return &SeatActivationResult{Valid: false, Message: "The license key provided is invalid. Please enter a valid license key."}, nil
		}
		return nil, err
	}

	if status != "active" {
		return &SeatActivationResult{Valid: false, Message: "This company license is suspended or expired. Please contact your administrator."}, nil
	}

	role := "user"
	if key == adminKey {
		role = "admin"
	}

	// Check if this user/device already has an allocated seat
	var seatID, existingStatus string
	err = db.Pool.QueryRow(ctx, `SELECT id, status FROM license_seats WHERE license_id = $1 AND email = $2 AND device_id = $3`,
		licenseID, email, deviceID).Scan(&seatID, &existingStatus)

	if err == nil {
		if existingStatus == "revoked" {
			return &SeatActivationResult{Valid: false, Message: "Your seat access has been revoked by your company administrator."}, nil
		}
		// Refresh active timestamp, name, role and OS
		_, _ = db.Pool.Exec(ctx, `UPDATE license_seats SET last_active = CURRENT_TIMESTAMP, name = $1, device_os = $2, role = $3 WHERE id = $4`,
			name, deviceOS, role, seatID)
	} else if errors.Is(err, pgx.ErrNoRows) {
		// New seat request: Check current seat quota across Admins and Users
		var activeSeats, adminCount, userCount int
		err = db.Pool.QueryRow(ctx, `SELECT 
			COUNT(*),
			COUNT(*) FILTER (WHERE role = 'admin'),
			COUNT(*) FILTER (WHERE role = 'user')
			FROM license_seats 
			WHERE license_id = $1 AND status = 'active'`, licenseID).Scan(&activeSeats, &adminCount, &userCount)
		if err != nil {
			return nil, err
		}

		if activeSeats >= maxSeats {
			return &SeatActivationResult{
				Valid:   false,
				Message: fmt.Sprintf("All %d seats for %s have been allocated (%d Admins, %d Users). Contact your administrator to expand your license.", maxSeats, companyName, adminCount, userCount),
			}, nil
		}

		// Insert new seat
		err = db.Pool.QueryRow(ctx, `INSERT INTO license_seats (license_id, role, name, email, device_id, device_os, status)
			VALUES ($1, $2, $3, $4, $5, $6, 'active')
			RETURNING id`, licenseID, role, name, email, deviceID, deviceOS).Scan(&seatID)
		if err != nil {
			return nil, err
		}
	} else {
		return nil, err
	}

	// Fetch current counts
	var activeSeats, adminCount, userCount int
	_ = db.Pool.QueryRow(ctx, `SELECT 
		COUNT(*),
		COUNT(*) FILTER (WHERE role = 'admin'),
		COUNT(*) FILTER (WHERE role = 'user')
		FROM license_seats 
		WHERE license_id = $1 AND status = 'active'`, licenseID).Scan(&activeSeats, &adminCount, &userCount)

	return &SeatActivationResult{
		Valid:             true,
		Message:           "License verified and activated successfully.",
		LicenseID:         licenseID,
		Role:              role,
		CompanyName:       companyName,
		Tier:              tier,
		TierDisplay:       tierDisplay,
		SetupFeeGBP:       setupFee,
		PerUserMonthlyGBP: perUserFee,
		MaxSeats:          maxSeats,
		ActiveSeats:       activeSeats,
		AdminCount:        adminCount,
		UserCount:         userCount,
		SeatID:            seatID,
	}, nil
}

func (db *Database) CheckSeatStatus(ctx context.Context, licenseID, email, deviceID string) (bool, error) {
	var status string
	err := db.Pool.QueryRow(ctx, `SELECT status FROM license_seats WHERE license_id = $1 AND email = $2 AND device_id = $3`,
		licenseID, email, deviceID).Scan(&status)
	if err != nil {
		if errors.Is(err, pgx.ErrNoRows) {
			return false, nil
		}
		return false, err
	}
	return status == "active", nil
}

func (db *Database) GetAdminDashboardData(ctx context.Context, adminKey string) (*AdminDashboardView, error) {
	var licenseID, companyName, tier, tierDisplay string
	var setupFee, perUserFee float64
	var maxSeats int

	err := db.Pool.QueryRow(ctx, `SELECT id, company_name, tier, tier_display, setup_fee_gbp, per_user_monthly_gbp, max_seats 
		FROM company_licenses 
		WHERE admin_key = $1 AND status = 'active'`, adminKey).Scan(
		&licenseID, &companyName, &tier, &tierDisplay, &setupFee, &perUserFee, &maxSeats,
	)
	if err != nil {
		return nil, errors.New("unauthorized: invalid admin license key")
	}

	var activeSeats, adminCount, userCount int
	_ = db.Pool.QueryRow(ctx, `SELECT 
		COUNT(*),
		COUNT(*) FILTER (WHERE role = 'admin'),
		COUNT(*) FILTER (WHERE role = 'user')
		FROM license_seats 
		WHERE license_id = $1 AND status = 'active'`, licenseID).Scan(&activeSeats, &adminCount, &userCount)

	rows, err := db.Pool.Query(ctx, `SELECT id, role, name, email, device_id, device_os, status, storage_used_bytes, last_active, created_at
		FROM license_seats 
		WHERE license_id = $1 
		ORDER BY status ASC, role ASC, created_at ASC`, licenseID)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var seats []AdminDashboardSeat
	for rows.Next() {
		var s AdminDashboardSeat
		var lastActive, createdAt time.Time
		if err := rows.Scan(&s.ID, &s.Role, &s.Name, &s.Email, &s.DeviceID, &s.DeviceOS, &s.Status, &s.StorageBytes, &lastActive, &createdAt); err != nil {
			return nil, err
		}
		s.LastActive = lastActive.Format(time.RFC339)
		s.CreatedAt = createdAt.Format("2006-01-02")
		s.StorageUsedStr = formatBytes(s.StorageBytes)
		seats = append(seats, s)
	}

	monthlyRate := perUserFee * float64(activeSeats)
	remaining := maxSeats - activeSeats
	if remaining < 0 {
		remaining = 0
	}

	return &AdminDashboardView{
		CompanyName:       companyName,
		Tier:              tier,
		TierDisplay:       tierDisplay,
		SetupFeeGBP:       setupFee,
		PerUserMonthlyGBP: perUserFee,
		MonthlyRunRateGBP: monthlyRate,
		MaxSeats:          maxSeats,
		TotalActiveSeats:  activeSeats,
		AdminCount:        adminCount,
		UserCount:         userCount,
		RemainingSeats:    remaining,
		Seats:             seats,
	}, nil
}

func (db *Database) RevokeSeat(ctx context.Context, adminKey, seatID string) error {
	var licenseID string
	err := db.Pool.QueryRow(ctx, `SELECT id FROM company_licenses WHERE admin_key = $1 AND status = 'active'`, adminKey).Scan(&licenseID)
	if err != nil {
		return errors.New("unauthorized: invalid admin license key")
	}

	tag, err := db.Pool.Exec(ctx, `UPDATE license_seats SET status = 'revoked' WHERE id = $1 AND license_id = $2`, seatID, licenseID)
	if err != nil {
		return err
	}
	if tag.RowsAffected() == 0 {
		return errors.New("seat not found or not belonging to this license")
	}
	return nil
}

