package crawler

import (
	"crypto/tls"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"time"

	"github.com/XiaoleC05/dormguard-go/internal/config"
)

type PowerCrawler struct {
	baseURL     string
	roomID      string
	areaID      string
	yqID        string
	buildingID  string
	floorID     string
	factoryCode string
	sign        string
	orgID       string
	dormNumber  string
	openID      string
	jSessionID  string
	client      *http.Client
}

type PowerData struct {
	DormNumber       string  `json:"dorm_number"`
	Balance          float64 `json:"balance"`
	KBalance         float64 `json:"kbalance"`
	ZBalance         float64 `json:"zbalance"`
	PowerConsumption *float64 `json:"power_consumption"`
}

func NewPowerCrawler() *PowerCrawler {
	cfg := config.Cfg

	return &PowerCrawler{
		baseURL:     cfg.CrawlerBaseURL,
		roomID:      cfg.CrawlerRoomID,
		areaID:      cfg.CrawlerAreaID,
		yqID:        cfg.CrawlerYQID,
		buildingID:  cfg.CrawlerBuildingID,
		floorID:     cfg.CrawlerFloorID,
		factoryCode: cfg.CrawlerFactoryCode,
		sign:        cfg.CrawlerSign,
		orgID:       cfg.CrawlerOrgID,
		dormNumber:  cfg.CrawlerDormNumber,
		openID:      cfg.CrawlerOpenID,
		jSessionID:  cfg.CrawlerJSessionID,
		client: &http.Client{
			Timeout: 15 * time.Second,
			Transport: &http.Transport{
				TLSClientConfig: &tls.Config{InsecureSkipVerify: true},
			},
		},
	}
}

func (c *PowerCrawler) FetchPowerData(dormNumber, roomID string) (*PowerData, error) {
	targetDorm := dormNumber
	if targetDorm == "" {
		targetDorm = c.dormNumber
	}
	targetRoom := roomID
	if targetRoom == "" {
		targetRoom = c.roomID
	}

	if targetRoom == "" {
		return nil, fmt.Errorf("未配置房间ID，无法查询宿舍 %s 的电费", targetDorm)
	}

	if c.openID == "" {
		return nil, fmt.Errorf("未配置openid，无法登录")
	}

	apiURL := c.baseURL + "/channel/querySydl"
	params := url.Values{}
	params.Set("areaid", c.areaID)
	params.Set("yqid", c.yqID)
	params.Set("buildingid", c.buildingID)
	params.Set("floorid", c.floorID)
	params.Set("roomid", targetRoom)
	params.Set("factorycode", c.factoryCode)
	params.Set("sign", c.sign)
	params.Set("openid", c.openID)
	params.Set("orgid", c.orgID)

	fullURL := apiURL + "?" + params.Encode()

	req, err := http.NewRequest("GET", fullURL, nil)
	if err != nil {
		return nil, err
	}

	req.Header.Set("Host", "ecard.xhu.edu.cn")
	req.Header.Set("isWechatApp", "true")
	req.Header.Set("session-type", "uniapp")
	req.Header.Set("orgid", c.orgID)
	req.Header.Set("User-Agent", "Mozilla/5.0 (Linux; Android 16; V2408A) AppleWebKit/537.36")
	req.Header.Set("content-type", "application/json")
	req.Header.Set("Accept", "*/*")
	req.Header.Set("Referer", c.baseURL+"/")

	if c.jSessionID != "" {
		req.AddCookie(&http.Cookie{Name: "JSESSIONID", Value: c.jSessionID})
	}

	resp, err := c.client.Do(req)
	if err != nil {
		return nil, fmt.Errorf("API请求失败: %w", err)
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, err
	}

	var result struct {
		Success    bool   `json:"success"`
		Message    string `json:"message"`
		Code       string `json:"code"`
		ResultData struct {
			BalanceList []struct {
				KBalance string `json:"kbalance"`
				ZBalance string `json:"zbalance"`
			} `json:"balancelist"`
		} `json:"resultData"`
	}

	if err := json.Unmarshal(body, &result); err != nil {
		return nil, err
	}

	if !result.Success {
		return nil, fmt.Errorf("API返回失败: %s (code: %s)", result.Message, result.Code)
	}

	if len(result.ResultData.BalanceList) == 0 {
		return nil, fmt.Errorf("响应中未找到余额数据")
	}

	balanceInfo := result.ResultData.BalanceList[0]
	var kbalance, zbalance float64
	fmt.Sscanf(balanceInfo.KBalance, "%f", &kbalance)
	fmt.Sscanf(balanceInfo.ZBalance, "%f", &zbalance)

	return &PowerData{
		DormNumber: targetDorm,
		Balance:    kbalance,
		KBalance:   kbalance,
		ZBalance:   zbalance,
	}, nil
}
