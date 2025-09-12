package main

import (
	"fmt"
	"kotak-trading-bot/cmd/internal/auth"
	kotak "kotak-trading-bot/cmd/internal/kotakapi"
	db "kotak-trading-bot/cmd/internal/storage"
	logic "kotak-trading-bot/cmd/internal/trading"
	"log"
	"sync"
	"time"
)

func main() {
	fmt.Println("🚀 Starting Kotak Trading Bot...")

	token, sessionToken, sid, err := auth.Login()
	if err != nil {
		log.Fatalf("❌ Login failed: %v", err)
	}
	fmt.Println("✅ Login successful. Token fetched.", token)
	fmt.Println("SID fetched.", sid)

	ticker := time.NewTicker(2 * time.Second)
	defer ticker.Stop()

	for {
		select {
		case <-ticker.C:
			// Step 3: Fetch expert calls
			tips, err := kotak.FetchExpertCalls(token)
			if err != nil {
				fmt.Println("Error fetching expert calls:", err)
				continue
			}

			if len(tips) == 0 {
				fmt.Println("No active expert calls found.")
				continue
			}
			prices, err := kotak.FetchQuotePrice(tips, token)
			if err != nil {
				fmt.Println("Error fetching price calls:", err)
				continue
			}
			positions, err := kotak.FetchLivePositions(token, sessionToken, sid)
			if err != nil {
				fmt.Println("Error fetching positions:", err)
				continue
			}
			orderStatusMap, err := db.FetchAllOrders()
			if err != nil {
				fmt.Println("Error fetching orders from DB:", err)
				continue
			}

			var wg sync.WaitGroup
			for _, tip := range tips {
				wg.Add(1)

				go func(t kotak.ExpertCall) {
					defer wg.Done()

					price := prices[t.InstrumentToken]
					pos, _ := positions[t.Symbol] // Lookup from map, can be empty

					err := logic.HandleTip(t, pos, price, orderStatusMap)
					if err != nil {
						fmt.Println("Logic error for", t.Symbol, ":", err)
					}
				}(tip)
			}

			wg.Wait()
		}
	}
}

// https://lapi.kotaksecurities.com/wso2-scripmaster/v1/prod/2025-04-25/transformed/nse_cm.csv
// https://documenter.getpostman.com/view/21534797/UzBnqmpD#753c18da-ce1c-421f-834d-1e88a4395dfe
