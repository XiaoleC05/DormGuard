package bot

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"time"

	"github.com/XiaoleC05/dormguard-go/internal/config"
)

type Client struct {
	apiURL string
	token  string
	client *http.Client
}

func NewClient() *Client {
	cfg := config.Cfg
	return &Client{
		apiURL: cfg.QQBotAPIURL,
		token:  cfg.QQBotAPIToken,
		client: &http.Client{Timeout: 10 * time.Second},
	}
}

type sendGroupMsgRequest struct {
	GroupID int    `json:"group_id"`
	Message string `json:"message"`
}

type sendGroupMsgResponse struct {
	Status  string `json:"status"`
	RetCode int    `json:"retcode"`
	Msg     string `json:"msg"`
}

type statusResponse struct {
	Status  string `json:"status"`
	RetCode int    `json:"retcode"`
	Data    struct {
		Online bool   `json:"online"`
		BotID  string `json:"bot_id"`
	} `json:"data"`
	Msg string `json:"msg"`
}

func (c *Client) SendGroupMsg(groupID int, message string) (bool, string) {
	url := c.apiURL + "/api/send_group_msg"
	payload := sendGroupMsgRequest{GroupID: groupID, Message: message}
	body, _ := json.Marshal(payload)

	req, err := http.NewRequest("POST", url, bytes.NewReader(body))
	if err != nil {
		return false, fmt.Sprintf("创建请求失败: %v", err)
	}
	req.Header.Set("Content-Type", "application/json")
	if c.token != "" {
		req.Header.Set("Authorization", "Bearer "+c.token)
	}

	resp, err := c.client.Do(req)
	if err != nil {
		return false, fmt.Sprintf("QQ告警发送失败: %v", err)
	}
	defer resp.Body.Close()

	var result sendGroupMsgResponse
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return false, "解析响应失败"
	}

	if resp.StatusCode == 200 && (result.Status == "ok" || result.RetCode == 0) {
		return true, ""
	}
	return false, result.Msg
}

func (c *Client) GetStatus() (bool, bool, string, string) {
	url := c.apiURL + "/api/get_status"

	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		return false, false, "", fmt.Sprintf("创建请求失败: %v", err)
	}
	if c.token != "" {
		req.Header.Set("Authorization", "Bearer "+c.token)
	}

	resp, err := c.client.Do(req)
	if err != nil {
		return false, false, "", fmt.Sprintf("连接NoneBot失败: %v", err)
	}
	defer resp.Body.Close()

	var result statusResponse
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return true, false, "", "解析响应失败"
	}

	if result.Status == "ok" && result.RetCode == 0 {
		return true, result.Data.Online, result.Data.BotID, ""
	}
	return true, false, "", result.Msg
}
