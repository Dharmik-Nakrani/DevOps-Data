package trade

import (
	"database/sql"
	"fmt"
	"math/rand"

	kotak "kotak-trading-bot/cmd/internal/kotakapi"

	_ "github.com/mattn/go-sqlite3"
)

// MockPrice calculates the mock price based on current price ±2%
func MockPrice(currentPrice float64) float64 {
	// rand.Seed(time.Now().UnixNano())

	var variation = rand.Float64()*0.04 - 0.02 // -2% to +2% range
	return currentPrice * (1 + variation)
}

// GetBudget fetches the user's investment budget from the database
func GetBudget() (float64, error) {
	db, err := sql.Open("sqlite3", "./kotak.db")
	if err != nil {
		return 0, fmt.Errorf("failed to open DB: %v", err)
	}
	defer db.Close()

	var budget float64
	row := db.QueryRow("SELECT budget FROM users LIMIT 1")
	if err := row.Scan(&budget); err != nil {
		return 0, fmt.Errorf("failed to fetch budget: %v", err)
	}

	return budget, nil
}

// ApplyTradeLogic calculates how many shares to buy based on the budget and price
func ApplyTradeLogic(expertCalls []kotak.ExpertCall) error {
	budget, err := GetBudget()
	if err != nil {
		return fmt.Errorf("failed to get budget: %v", err)
	}

	for _, call := range expertCalls {
		if call.CallStatus != "Open" {
			continue
		}

		// Price := MockPrice(call.EntryPrice1)
		Price := call.Closeprice
		maxBudgetPerTrade := 2000.0
		if Price > maxBudgetPerTrade {
			continue
		}

		quantity := int(budget / Price) // Split budget across eligible trades
		// Make sure quantity doesn't exceed budget
		if float64(quantity)*Price > maxBudgetPerTrade {
			quantity = int(maxBudgetPerTrade / Price)
		}

		// Now, place the trade (mock or real based on your logic)
		// Save the trade in DB or place a real order

		fmt.Printf("✅ Placing trade for %s: Buy %d shares at ₹%.2f\n", call.Symbol, quantity, Price)
	}

	return nil
}

func SyncPositionsToDB([]string) error {
	return nil
}

func HandleTip(tip kotak.ExpertCall, pos kotak.Position, ltp float64, orders map[string]db.Order) error {
	existingOrder, hasOrder := orders[tip.InstrumentToken]

	switch {
	case !hasOrder && tip.Status == "open":
		// No order yet, tip open -> Place a fresh order
		if ltp <= tip.SuggestedPrice {
			err := kotak.PlaceBuyOrder(tip, tip.SuggestedPrice)
			if err != nil {
				return fmt.Errorf("placing buy order failed: %v", err)
			}
			return db.SaveOrder(tip, "open")
		}
		fmt.Println(tip.Symbol, ": Waiting for price to reach", tip.SuggestedPrice)

	case hasOrder && (tip.Status == "closed" || tip.Status == "partialexit"):
		// Tip is closed or partial exit -> Square off if holding position
		if pos.BuyQty > 0 {
			err := kotak.SquareOffPosition(tip)
			if err != nil {
				return fmt.Errorf("square off failed: %v", err)
			}
			return db.UpdateOrderStatus(existingOrder.ID, "closed")
		}

	case hasOrder && pos.BuyQty > 0:
		// Active position, check if SL/Target hit
		if ltp <= tip.SL {
			fmt.Println(tip.Symbol, ": Stop Loss hit at", ltp)
			err := kotak.SquareOffPosition(tip)
			if err != nil {
				return fmt.Errorf("square off SL failed: %v", err)
			}
			return db.UpdateOrderStatus(existingOrder.ID, "sl-hit")
		}
		if ltp >= tip.Target {
			fmt.Println(tip.Symbol, ": Target hit at", ltp)
			err := kotak.SquareOffPosition(tip)
			if err != nil {
				return fmt.Errorf("square off Target failed: %v", err)
			}
			return db.UpdateOrderStatus(existingOrder.ID, "target-hit")
		}

	default:
		// Waiting or No action needed
	}

	return nil
}
