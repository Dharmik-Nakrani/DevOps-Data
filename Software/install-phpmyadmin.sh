#!/usr/bin/env bash

set -e

echo "======================================"
echo "        Install phpMyAdmin"
echo "======================================"
echo

# Check if Apache is installed
if ! command -v apache2 >/dev/null 2>&1; then
    echo "✗ Apache2 is not installed."
    echo "Please install Apache first."
    exit 1
fi

# Check if MySQL is installed
if ! command -v mysql >/dev/null 2>&1; then
    echo "✗ MySQL is not installed."
    echo "Please install MySQL first."
    exit 1
fi

# Install phpMyAdmin
echo "Installing phpMyAdmin..."
sudo apt-get update
sudo apt-get install -y phpmyadmin

# Configure Apache
echo
echo "Configuring Apache..."

APACHE_CONF="/etc/apache2/apache2.conf"
PHPMYADMIN_CONF="/etc/phpmyadmin/apache.conf"

if ! grep -Fq "Include $PHPMYADMIN_CONF" "$APACHE_CONF"; then
    echo "Include $PHPMYADMIN_CONF" | sudo tee -a "$APACHE_CONF" > /dev/null
    echo "✓ phpMyAdmin Apache configuration added."
else
    echo "✓ phpMyAdmin Apache configuration already exists."
fi

# Test Apache configuration
echo
echo "Testing Apache configuration..."

if sudo apache2ctl configtest; then
    echo "✓ Apache configuration is valid."
else
    echo "✗ Apache configuration has an error."
    exit 1
fi

# Restart Apache
echo
echo "Restarting Apache..."
sudo systemctl restart apache2

# Ask for MySQL application user
echo
echo "======================================"
echo "       Create MySQL User"
echo "======================================"
echo

read -rp "Enter MySQL username [harshad]: " MYSQL_USER
MYSQL_USER=${MYSQL_USER:-harshad}

read -rsp "Enter password for '$MYSQL_USER': " MYSQL_PASSWORD
echo

if [ -z "$MYSQL_PASSWORD" ]; then
    echo "✗ Password cannot be empty."
    exit 1
fi

# Create MySQL user and grant privileges
echo
echo "Creating MySQL user '$MYSQL_USER'..."

sudo mysql <<SQL
CREATE USER IF NOT EXISTS '$MYSQL_USER'@'localhost' IDENTIFIED BY '$MYSQL_PASSWORD';
ALTER USER '$MYSQL_USER'@'localhost' IDENTIFIED BY '$MYSQL_PASSWORD';
GRANT ALL PRIVILEGES ON *.* TO '$MYSQL_USER'@'localhost';
FLUSH PRIVILEGES;
SQL

echo
echo "======================================"
echo " phpMyAdmin Installation Complete"
echo "======================================"

echo
echo "✓ phpMyAdmin installed."
echo "✓ Apache configured."
echo "✓ Apache restarted."
echo "✓ MySQL user '$MYSQL_USER' created."
echo
echo "Open phpMyAdmin:"
echo "http://localhost/phpmyadmin"
echo
echo "Login:"
echo "Username: $MYSQL_USER"
echo "Password: ********"
echo
echo "======================================"
