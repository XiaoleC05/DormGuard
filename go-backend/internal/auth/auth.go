package auth

import (
	"crypto/hmac"
	"crypto/sha256"
	"crypto/subtle"
	"encoding/base64"
	"encoding/json"
	"fmt"
	"net"
	"strings"
	"time"

	"github.com/XiaoleC05/dormguard-go/internal/config"
)

type Claims struct {
	Sub string `json:"sub"`
	Exp int64  `json:"exp"`
}

func CreateAccessToken(username string) string {
	cfg := config.Cfg
	payload := Claims{
		Sub: username,
		Exp: time.Now().Add(time.Duration(cfg.AdminTokenExpireHours) * time.Hour).Unix(),
	}

	payloadBytes, _ := json.Marshal(payload)
	payloadB64 := base64.RawURLEncoding.EncodeToString(payloadBytes)
	signature := signPayload(payloadB64, cfg.AdminJWTSecret)

	return payloadB64 + "." + signature
}

func VerifyAccessToken(token string) (string, bool) {
	cfg := config.Cfg
	parts := strings.Split(token, ".")
	if len(parts) != 2 {
		return "", false
	}

	payloadB64 := parts[0]
	signature := parts[1]

	expectedSig := signPayload(payloadB64, cfg.AdminJWTSecret)
	if subtle.ConstantTimeCompare([]byte(signature), []byte(expectedSig)) != 1 {
		return "", false
	}

	payloadBytes, err := base64.RawURLEncoding.DecodeString(payloadB64)
	if err != nil {
		return "", false
	}

	var claims Claims
	if err := json.Unmarshal(payloadBytes, &claims); err != nil {
		return "", false
	}

	if claims.Exp < time.Now().Unix() {
		return "", false
	}

	if claims.Sub != cfg.AdminUsername {
		return "", false
	}

	return claims.Sub, true
}

func VerifyPassword(username, password string) bool {
	cfg := config.Cfg
	if username != cfg.AdminUsername {
		return false
	}
	return subtle.ConstantTimeCompare([]byte(password), []byte(cfg.AdminPassword)) == 1
}

func signPayload(payloadB64, secret string) string {
	h := hmac.New(sha256.New, []byte(secret))
	h.Write([]byte(payloadB64))
	return fmt.Sprintf("%x", h.Sum(nil))
}

// Gateway trust logic
func IsTrustedGatewayClient(clientIP string) bool {
	if clientIP == "" {
		return false
	}
	if clientIP == "localhost" || clientIP == "127.0.0.1" || clientIP == "::1" {
		return true
	}

	ip := net.ParseIP(clientIP)
	if ip == nil {
		return false
	}
	return ip.IsLoopback()
}

type GatewayUser struct {
	UserID   string
	Username string
	Role     string
}

func GetGatewayUser(clientIP string, headers map[string]string) (*GatewayUser, bool) {
	cfg := config.Cfg
	if !cfg.OxeliaGatewayMode {
		return nil, false
	}

	if !IsTrustedGatewayClient(clientIP) {
		return nil, false
	}

	userID := headers["X-Oxelia51-User-Id"]
	username := headers["X-Oxelia51-Username"]
	role := headers["X-Oxelia51-Role"]

	if userID == "" || username == "" || (role != "admin" && role != "user") {
		return nil, false
	}

	if cfg.OxeliaGatewaySecret != "" {
		got := headers["X-Oxelia51-Gateway-Secret"]
		if subtle.ConstantTimeCompare([]byte(got), []byte(cfg.OxeliaGatewaySecret)) != 1 {
			return nil, false
		}
	}

	return &GatewayUser{
		UserID:   userID,
		Username: username,
		Role:     role,
	}, true
}
