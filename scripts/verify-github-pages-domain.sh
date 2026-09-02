#!/bin/bash
# Script to verify GitHub Pages domain DNS configuration
# Checks for TXT record at _github-pages-challenge-xiaunknown116-del.apexcapitalweb.com

echo "[*] Querying DNS for GitHub Pages challenge record..."
dig _github-pages-challenge-xiaunknown116-del.apexcapitalweb.com TXT +short

echo ""
echo "[*] Expected DNS response:"
echo "911ea466a730baa82f13a9bf78e011"
