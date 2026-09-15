#!/usr/bin/env bash

set -e

SWAPPINESS=10
SYSCTL_FILE="/etc/sysctl.conf"

echo "======================================"
echo "       Change Linux Swappiness"
echo "======================================"

# Check current value
CURRENT=$(cat /proc/sys/vm/swappiness)

echo "Current swappiness: $CURRENT"
echo "Target swappiness:  $SWAPPINESS"
echo

# Check if already configured
if grep -qE '^[[:space:]]*vm\.swappiness[[:space:]]*=' "$SYSCTL_FILE"; then
    echo "Updating existing vm.swappiness setting..."

    sudo sed -i \
        -E "s/^[[:space:]]*vm\.swappiness[[:space:]]*=.*/vm.swappiness=$SWAPPINESS/" \
        "$SYSCTL_FILE"
else
    echo "Adding vm.swappiness=$SWAPPINESS..."

    sudo tee -a "$SYSCTL_FILE" > /dev/null <<EOF

# Sharply reduce the inclination to swap
vm.swappiness=$SWAPPINESS
EOF
fi

# Apply immediately without reboot
echo
echo "Applying new swappiness setting..."
sudo sysctl -p "$SYSCTL_FILE"

# Verify
NEW_VALUE=$(cat /proc/sys/vm/swappiness)

echo
echo "======================================"
echo "Swappiness updated successfully!"
echo "Current swappiness: $NEW_VALUE"
echo "======================================"

if [ "$NEW_VALUE" -eq "$SWAPPINESS" ]; then
    echo "✓ Swappiness is correctly set to $SWAPPINESS."
else
    echo "✗ Failed to set swappiness."
    exit 1
fi
