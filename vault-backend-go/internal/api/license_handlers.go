package api

import (
	"encoding/json"
	"net/http"
	"strings"
)

type VerifyLicenseRequest struct {
	LicenseKey string `json:"license_key"`
	Name       string `json:"name"`
	Email      string `json:"email"`
	DeviceID   string `json:"device_id"`
	DeviceOS   string `json:"device_os"`
}

type CheckSeatStatusRequest struct {
	LicenseID string `json:"license_id"`
	Email     string `json:"email"`
	DeviceID  string `json:"device_id"`
}

type RevokeSeatRequest struct {
	AdminKey string `json:"admin_key"`
	SeatID   string `json:"seat_id"`
}

func (h *Handler) VerifyAndActivateLicense(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var req VerifyLicenseRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid JSON payload", http.StatusBadRequest)
		return
	}

	req.LicenseKey = strings.TrimSpace(req.LicenseKey)
	req.Name = strings.TrimSpace(req.Name)
	req.Email = strings.TrimSpace(strings.ToLower(req.Email))
	req.DeviceID = strings.TrimSpace(req.DeviceID)
	if req.DeviceOS == "" {
		req.DeviceOS = "Windows"
	}

	if req.LicenseKey == "" || req.Name == "" || req.Email == "" || req.DeviceID == "" {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusBadRequest)
		_ = json.NewEncoder(w).Encode(map[string]interface{}{
			"valid":   false,
			"message": "Full Name, Work Email, and License Key are all required.",
		})
		return
	}

	result, err := h.db.VerifyAndActivateSeat(r.Context(), req.LicenseKey, req.Name, req.Email, req.DeviceID, req.DeviceOS)
	if err != nil {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusInternalServerError)
		_ = json.NewEncoder(w).Encode(map[string]interface{}{
			"valid":   false,
			"message": "Database verification error: " + err.Error(),
		})
		return
	}

	w.Header().Set("Content-Type", "application/json")
	if !result.Valid {
		w.WriteHeader(http.StatusForbidden)
	} else {
		w.WriteHeader(http.StatusOK)
	}
	_ = json.NewEncoder(w).Encode(result)
}

func (h *Handler) CheckLicenseSeatStatus(w http.ResponseWriter, r *http.Request) {
	var req CheckSeatStatusRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid request body", http.StatusBadRequest)
		return
	}

	active, err := h.db.CheckSeatStatus(r.Context(), req.LicenseID, req.Email, req.DeviceID)
	if err != nil {
		http.Error(w, "Database error", http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	_ = json.NewEncoder(w).Encode(map[string]bool{"active": active})
}

func (h *Handler) GetAdminDashboardOverview(w http.ResponseWriter, r *http.Request) {
	adminKey := strings.TrimSpace(r.Header.Get("X-Admin-License-Key"))
	if adminKey == "" {
		adminKey = strings.TrimSpace(r.URL.Query().Get("admin_key"))
	}

	if adminKey == "" {
		http.Error(w, "X-Admin-License-Key header required", http.StatusUnauthorized)
		return
	}

	view, err := h.db.GetAdminDashboardData(r.Context(), adminKey)
	if err != nil {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusUnauthorized)
		_ = json.NewEncoder(w).Encode(map[string]string{"error": err.Error()})
		return
	}

	w.Header().Set("Content-Type", "application/json")
	_ = json.NewEncoder(w).Encode(view)
}

func (h *Handler) RevokeAdminSeat(w http.ResponseWriter, r *http.Request) {
	adminKey := strings.TrimSpace(r.Header.Get("X-Admin-License-Key"))
	var req RevokeSeatRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid request payload", http.StatusBadRequest)
		return
	}

	if adminKey == "" {
		adminKey = req.AdminKey
	}

	if adminKey == "" || req.SeatID == "" {
		http.Error(w, "admin_key and seat_id required", http.StatusBadRequest)
		return
	}

	err := h.db.RevokeSeat(r.Context(), adminKey, req.SeatID)
	if err != nil {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusBadRequest)
		_ = json.NewEncoder(w).Encode(map[string]string{"error": err.Error()})
		return
	}

	w.Header().Set("Content-Type", "application/json")
	_ = json.NewEncoder(w).Encode(map[string]interface{}{
		"success": true,
		"message": "Seat successfully revoked.",
	})
}
