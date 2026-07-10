package handler

import (
	"net/http"
	"strings"

	"github.com/XiaoleC05/dormguard-go/internal/auth"
	"github.com/XiaoleC05/dormguard-go/internal/config"
	"github.com/gin-gonic/gin"
)

type AuthHandler struct{}

func NewAuthHandler() *AuthHandler {
	return &AuthHandler{}
}

// Login 管理员登录
// POST /api/auth/login
func (h *AuthHandler) Login(c *gin.Context) {
	var req struct {
		Username string `json:"username" binding:"required"`
		Password string `json:"password" binding:"required"`
	}
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "请求格式错误"})
		return
	}

	// 验证密码
	if !auth.VerifyPassword(req.Username, req.Password) {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "用户名或密码错误"})
		return
	}

	// 生成 token
	token := auth.CreateAccessToken(req.Username)

	c.JSON(http.StatusOK, gin.H{
		"access_token": token,
		"token_type":   "bearer",
		"username":     req.Username,
	})
}

// AuthMiddleware 认证中间件（网关模式 / JWT 兼容）
func AuthMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		cfg := config.Cfg
		if cfg.OxeliaGatewayMode {
			// 优先读短 header（GW-FIX），兼容长 header
			userID := getHeaderAny(c, "X-User-Id", "X-Oxelia51-User-Id")
			username := getHeaderAny(c, "X-Username", "X-Oxelia51-Username")
			role := getHeaderAny(c, "X-Role", "X-Oxelia51-Role")

			if userID != "" && username != "" && role != "" {
				// 验证网关密钥（如果配置了）
				if cfg.OxeliaGatewaySecret != "" {
					secret := c.GetHeader("X-Oxelia51-Gateway-Secret")
					if secret != cfg.OxeliaGatewaySecret {
						c.JSON(http.StatusUnauthorized, gin.H{"error": "网关密钥错误"})
						c.Abort()
						return
					}
				}
				c.Set("username", username)
				c.Set("role", role)
				c.Next()
				return
			}
		}

		// 标准 JWT 认证
		authHeader := c.GetHeader("Authorization")
		if authHeader == "" {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "缺少认证头"})
			c.Abort()
			return
		}

		parts := strings.SplitN(authHeader, " ", 2)
		if len(parts) != 2 || parts[0] != "Bearer" {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "认证格式错误"})
			c.Abort()
			return
		}

		tokenString := parts[1]
		username, valid := auth.VerifyAccessToken(tokenString)
		if !valid {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "无效的认证令牌"})
			c.Abort()
			return
		}

		c.Set("username", username)
		// DormGuard 褰撳墠浠呯鐞嗗憳浣跨敤锛屾湭鏉ヨ嫢鏀寔鏅€氱敤鎴烽渶浠?JWT claims 璇?role
		c.Set("role", "admin")
		c.Next()
	}
}

// AdminOnly 管理员权限中间件——仅 role=admin 可访问
func AdminOnly() gin.HandlerFunc {
	return func(c *gin.Context) {
		role, _ := c.Get("role")
		roleStr, _ := role.(string)
		if roleStr != "admin" {
			c.JSON(http.StatusForbidden, gin.H{"error": "该功能仅管理员可用"})
			c.Abort()
			return
		}
		c.Next()
	}
}

// GetRole 从 context 提取角色
func GetRole(c *gin.Context) string {
	role, _ := c.Get("role")
	roleStr, _ := role.(string)
	return roleStr
}

// getHeaderAny 按顺序尝试多个 header 名，返回第一个非空值
func getHeaderAny(c *gin.Context, names ...string) string {
	for _, name := range names {
		if v := c.GetHeader(name); v != "" {
			return v
		}
	}
	return ""
}
