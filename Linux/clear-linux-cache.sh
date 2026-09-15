#!/usr/bin/env bash

set -e

echo "======================================"
echo "   Clear Linux RAM Cache & Buffers"
echo "======================================"

echo
echo "Memory BEFORE clearing:"
free -mh

echo
echo "Clearing filesystem buffers and caches..."

# Flush filesystem buffers to disk
sync

# Drop page cache, dentries and inodes
sudo sh -c 'echo 3 > /proc/sys/vm/drop_caches'

echo
echo "Memory AFTER clearing:"
free -mh

echo
echo "======================================"
echo "Cache clearing completed!"
echo "======================================"
