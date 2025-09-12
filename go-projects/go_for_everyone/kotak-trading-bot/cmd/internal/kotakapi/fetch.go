package expertcalls

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"strconv"
	"strings"
)

// ExpertCall represents the structure of an expert call
type ExpertCall struct {
	CallStatus      string  `json:"callStatus"`
	TargetPrice1    float64 `json:"targetPrice1,string"`
	StopLossPrice1  float64 `json:"stopLossPrice1,string"`
	EntryPrice1     float64 `json:"entryPrice1,string"`
	CallType        string  `json:"callType"`
	CallId          string  `json:"callId"`
	Trdsymbol       string  `json:"trdSymbol"`
	Segment         string  `json:"exchangeSegment"`
	Closeprice      float64 `json:"closePrice,string"`
	Category        string  `json:"category"`
	Symbol          string  `json:"symbol"`
	InstrumentToken string  `json:"exchangeIdentifier"`
	Status          string  `json:"callStatus"`
}

type LTPResponse struct {
	ExchangeToken string  `json:"exchange_token"`
	DisplaySymbol string  `json:"display_symbol"`
	Exchange      string  `json:"exchange"`
	LTP           float64 `json:"ltp,string"`
}

// FetchExpertCalls fetches open expert calls from Kotak Neo API
func FetchExpertCalls(token string) ([]ExpertCall, error) {
	url := "https://neo.kotaksecurities.com/api/1research/recommendations?callStatus=open&subCategory=technical&isCommodity=true"
	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %v", err)
	}

	// Add authorization token
	req.Header.Set("Authorization", "Bearer "+token)
	req.Header.Set("Accept", "*/*")
	req.Header.Set("Content-Type", "application/json")

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return nil, fmt.Errorf("failed to send request: %v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("failed to fetch expert calls: %s", string(body))
	}

	var response struct {
		Data []ExpertCall `json:"data"`
	}

	if err := json.NewDecoder(resp.Body).Decode(&response); err != nil {
		return nil, fmt.Errorf("failed to decode response: %v", err)
	}

	return response.Data, nil
}

func FetchQuotePrice(tips []ExpertCall, token string) (map[string]float64, error) {
	var parts []string
	for _, tip := range tips {
		part := fmt.Sprintf("%s|%s", tip.Segment, tip.InstrumentToken)
		parts = append(parts, part)
	}
	rawString := strings.Join(parts, ",")
	encodedString := url.QueryEscape(rawString)
	url := "https://gw-napi.kotaksecurities.com/apim/quotes/1.0/quotes/neosymbol/" + encodedString + "/ltp"
	method := "GET"

	client := &http.Client{}
	req, err := http.NewRequest(method, url, nil)

	if err != nil {
		fmt.Println(err)
		return nil, err
	}
	req.Header.Add("accept", "application/json")
	req.Header.Add("Authorization", "Bearer "+token)

	res, err := client.Do(req)
	if err != nil {
		fmt.Println(err)
		return nil, err
	}
	defer res.Body.Close()

	body, err := io.ReadAll(res.Body)
	if err != nil {
		fmt.Println(err)
		return nil, err
	}

	var ltpResponses []LTPResponse
	if err := json.Unmarshal(body, &ltpResponses); err != nil {
		return nil, fmt.Errorf("failed to parse JSON: %v", err)
	}

	// Create dictionary: key = exchange_token, value = ltp
	ltpMap := make(map[string]float64)
	for _, resp := range ltpResponses {
		ltpMap[resp.ExchangeToken] = resp.LTP
	}

	return ltpMap, nil

}

type Position struct {
	Symbol          string
	TradingSymbol   string
	ExchangeSegment string
	Token           string
	BuyQty          int
	SellQty         int
}

type positionsResponse struct {
	Data []struct {
		Symbol        string `json:"sym"`
		TradingSymbol string `json:"trdSym"`
		ExchangeSeg   string `json:"exSeg"`
		Token         string `json:"tok"`
		BuyQty        string `json:"flBuyQty"`
		SellQty       string `json:"flSellQty"`
		BuyAmt        string `json:"buyAmt"`
	} `json:"data"`
}

func FetchLivePositions(authToken, sessionToken, sid string) (map[string]Position, error) {
	url := "https://gw-napi.kotaksecurities.com/Orders/2.0/quick/user/positions?sId=server1"

	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		return nil, err
	}

	// Headers
	req.Header.Add("accept", "application/json")
	req.Header.Add("Sid", sid)
	req.Header.Add("Auth", sessionToken)
	req.Header.Add("neo-fin-key", "neotradeapi")
	req.Header.Add("Authorization", "Bearer "+authToken)

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	bodyBytes, _ := io.ReadAll(resp.Body)
	var posResp positionsResponse
	err = json.Unmarshal(bodyBytes, &posResp)
	if err != nil {
		return nil, err
	}

	// Create a map
	positionMap := make(map[string]Position)
	for _, p := range posResp.Data {
		buyQty := safeAtoi(p.BuyQty)
		sellQty := safeAtoi(p.SellQty)

		positionMap[p.Token] = Position{
			TradingSymbol:   p.TradingSymbol,
			ExchangeSegment: p.ExchangeSeg,
			Token:           p.Token,
			BuyQty:          buyQty,
			SellQty:         sellQty,
		}
	}
	return positionMap, nil
}

func safeAtoi(str string) int {
	n, err := strconv.Atoi(str)
	if err != nil {
		return 0
	}
	return n
}
