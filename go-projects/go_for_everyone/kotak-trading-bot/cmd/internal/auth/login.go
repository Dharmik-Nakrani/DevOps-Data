package auth

import (
	"bytes"
	"database/sql"
	"encoding/base64"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"strings"

	_ "github.com/mattn/go-sqlite3"
)

type UserCredentials struct {
	Phone     string
	Email     string
	Password  string
	MPIN      string
	Apikey    string
	Apisecret string
}

type LoginResponse struct {
	Data struct {
		Token string `json:"token"`
		SID   string `json:"sid"`
	} `json:"data"`
}

type TokenResponse struct {
	Token string `json:"access_token"`
}

func Login() (string, string, string, error) {

	db, err := sql.Open("sqlite3", "./kotak.db")
	if err != nil {
		return "", "", "", fmt.Errorf("failed to open DB: %v", err)
	}
	defer db.Close()

	var creds UserCredentials
	row := db.QueryRow("SELECT phone, email, password, mpin,apikey,apisecret FROM users LIMIT 1")
	if err := row.Scan(&creds.Phone, &creds.Email, &creds.Password, &creds.MPIN, &creds.Apikey, &creds.Apisecret); err != nil {
		return "", "", "", fmt.Errorf("failed to read user credentials: %v", err)
	}

	auth := base64.StdEncoding.EncodeToString([]byte(creds.Apikey + ":" + creds.Apisecret))
	url := "https://napi.kotaksecurities.com/oauth2/token"
	method := "POST"

	payload := strings.NewReader("grant_type=client_credentials")

	client := &http.Client{}
	req, err := http.NewRequest(method, url, payload)
	if err != nil {
		// fmt.Println("Failed to create Step 1 request:", err)
		return "", "", "", err
	}
	req.Header.Add("Authorization", "Basic "+auth)
	req.Header.Add("Content-Type", "application/x-www-form-urlencoded")
	req.Header.Add("Cookie", "AWSALB=...") // You can keep or remove cookie based on need

	res, err := client.Do(req)
	if err != nil {
		// fmt.Println("Step 1 HTTP request failed:", err)
		return "", "", "", err
	}
	defer res.Body.Close()

	body, err := io.ReadAll(res.Body)
	if err != nil {
		// fmt.Println("Failed to read Step 1 response:", err)
		return "", "", "", err
	}

	// fmt.Println("Step 1 Raw Token Response:", string(body))

	if res.StatusCode != 200 {
		return "", "", "", fmt.Errorf("Step 1 failed with status %d, body: %s", res.StatusCode, string(body))
	}

	var token TokenResponse
	if err := json.Unmarshal(body, &token); err != nil {
		// fmt.Println("Failed to parse token response:", err)
		return "", "", "", err
	}

	// Step 2: Login with MPIN
	url = "https://gw-napi.kotaksecurities.com/login/1.0/login/v2/validate"
	payload2 := map[string]string{
		"mobileNumber": creds.Phone,
		"mpin":         creds.MPIN,
	}
	body2, err := json.Marshal(payload2)
	if err != nil {
		// fmt.Println("Failed to marshal Step 2 payload:", err)
		return "", "", "", err
	}
	// fmt.Println("Step 2 Payload:", string(body2))

	req2, err := http.NewRequest("POST", url, bytes.NewBuffer(body2))
	if err != nil {
		// fmt.Println("Failed to create Step 2 request:", err)
		return "", "", "", err
	}
	req2.Header.Add("accept", "*/*")
	req2.Header.Add("Content-Type", "application/json")
	req2.Header.Add("Authorization", "Bearer "+token.Token)

	res2, err := client.Do(req2)
	if err != nil {
		// fmt.Println("Step 2 HTTP request failed:", err)
		return "", "", "", err
	}
	defer res2.Body.Close()

	respBody, err := io.ReadAll(res2.Body)
	if err != nil {
		// fmt.Println("Failed to read Step 2 response:", err)
		return "", "", "", err
	}

	// fmt.Println("Step 2 Raw Login Response:", string(respBody))

	if res2.StatusCode != 201 {
		return "", "", "", fmt.Errorf("Step 2 failed with status %d, body: %s", res2.StatusCode, string(respBody))
	}

	var resp LoginResponse
	if err := json.Unmarshal(respBody, &resp); err != nil {
		// fmt.Println("Failed to parse login response:", err)
		return "", "", "", err
	}

	fmt.Println("Session Token:", resp.Data.Token)

	return token.Token, resp.Data.Token, resp.Data.SID, nil
}

// CREATE TABLE IF NOT EXISTS users (
//     id INTEGER PRIMARY KEY AUTOINCREMENT,
//     phone TEXT NOT NULL UNIQUE,
//     email TEXT NOT NULL UNIQUE,
//     password TEXT NOT NULL,
//     mpin TEXT NOT NULL,
//     budget REAL NOT NULL DEFAULT 0,
//     max_trade_per_call REAL NOT NULL DEFAULT 2000,
//     is_active BOOLEAN NOT NULL DEFAULT 1,
//     created_at DATETIME DEFAULT CURRENT_TIMESTAMP
// );
