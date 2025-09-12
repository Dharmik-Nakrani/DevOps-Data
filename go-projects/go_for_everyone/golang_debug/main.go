package main

import (
	"fmt"
)

func main() {
	// Example usage of the function
	words := []string{"apple", "banana", "cherry"}
	result := joinWords(words)
	fmt.Println(result) // Output: apple, banana, cherry
}

// joinWords takes a slice of strings and joins them into a single string
// separated by commas. It returns the resulting string.
func joinWords(words []string) string {
	// Check if the slice is empty
	if len(words) == 0 {
		return ""
	}

	// Initialize an empty string to hold the result
	result := ""

	// Iterate over the words and append them to the result string
	for i, word := range words {
		if i > 0 {
			result += ", "
		}
		result += word
	}

	return result
}
