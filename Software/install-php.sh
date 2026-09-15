#!/usr/bin/env bash

set -e

echo "======================================"
echo "       Install PHP for Apache"
echo "======================================"
echo

# Ask user for PHP version
read -rp "Enter PHP version to install (example: 8.2, 8.3, 8.4): " PHP_VERSION

# Validate PHP version format
if [[ ! "$PHP_VERSION" =~ ^[0-9]+\.[0-9]+$ ]]; then
    echo "✗ Invalid PHP version: $PHP_VERSION"
    echo "Example: 8.2"
    exit 1
fi

PHP_PACKAGE="php${PHP_VERSION}"
APACHE_MODULE="libapache2-mod-php${PHP_VERSION}"
MYSQL_MODULE="php${PHP_VERSION}-mysql"

echo
echo "PHP version selected: $PHP_VERSION"
echo

# Check if the requested PHP package exists
echo "Checking PHP ${PHP_VERSION} packages..."

if ! apt-cache show "$PHP_PACKAGE" >/dev/null 2>&1; then
    echo "✗ PHP ${PHP_VERSION} is not available in your configured APT repositories."
    echo
    echo "You may need to add a PHP repository such as Ondřej Surý's PPA"
    echo "for Ubuntu before running this script."
    exit 1
fi

echo "✓ PHP ${PHP_VERSION} package found."

# Update package list
echo
echo "Updating package lists..."
sudo apt-get update

# Install PHP + Apache module + MySQL module
echo
echo "Installing PHP ${PHP_VERSION}..."
sudo apt-get install -y \
    "$PHP_PACKAGE" \
    "$APACHE_MODULE" \
    "$MYSQL_MODULE"

# Enable Apache PHP module
echo
echo "Configuring Apache..."

sudo a2enmod "php${PHP_VERSION}" 2>/dev/null || true

# Configure Apache to prefer index.php
if [ -f /etc/apache2/mods-enabled/dir.conf ]; then
    sudo sed -i \
        's/DirectoryIndex .*/DirectoryIndex index.php index.html index.cgi index.pl index.xhtml index.htm/' \
        /etc/apache2/mods-enabled/dir.conf
fi

# Set safe permissions for web root
echo
echo "Setting permissions for /var/www/html..."

sudo chown -R "$USER":www-data /var/www/html
sudo find /var/www/html -type d -exec chmod 755 {} \;
sudo find /var/www/html -type f -exec chmod 644 {} \;

# Create PHP info page
echo
echo "Creating PHP info page..."

sudo tee /var/www/html/phpinfo.php > /dev/null <<'PHP'
<?php
phpinfo();
?>
PHP

# Restart Apache
echo
echo "Restarting Apache..."
sudo systemctl restart apache2

# Verify PHP
echo
echo "======================================"
echo " PHP Installation Complete"
echo "======================================"

echo
echo "PHP version:"
php -v

echo
echo "Apache status:"

if systemctl is-active --quiet apache2; then
    echo "✓ Apache is running."
else
    echo "✗ Apache is not running."
    sudo systemctl status apache2 --no-pager
    exit 1
fi

echo
echo "PHP info page:"
echo "http://localhost/phpinfo.php"

echo
echo "======================================"
echo " Installation successful!"
echo "======================================"
