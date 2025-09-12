package db

func FetchAllOrders() (map[string]Order, error) {
	// Return a map of InstrumentToken -> Order
}

func SaveOrder(tip kotak.ExpertCall, status string) error {
	// Insert into database
}

func UpdateOrderStatus(orderID int, newStatus string) error {
	// Update status in DB
}
