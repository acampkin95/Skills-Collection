#!/bin/bash
###############################################################################
# Real-time Deployment Monitor
# Watch deployment progress and server metrics in real-time
###############################################################################

SERVER="${1:-vmi02d}"
REFRESH_RATE="${2:-2}"  # seconds

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m'

clear_screen() {
    printf '\033[2J\033[H'
}

get_server_stats() {
    ssh "$SERVER" "
        # CPU usage
        top -bn1 | grep 'Cpu(s)' | awk '{print 100 - \$8}' | cut -d. -f1

        # Memory usage
        free | grep Mem | awk '{print int(\$3/\$2 * 100)}'

        # Disk usage
        df -h /opt/wattlewool 2>/dev/null | tail -1 | awk '{print \$5}' | sed 's/%//'

        # PM2 status
        pm2 jlist 2>/dev/null | jq -r '.[] | select(.name==\"wattlewool\") | .pm2_env.status' | head -1

        # Active SSH connections
        ss -tn state established '( dport = :22 or sport = :22 )' 2>/dev/null | wc -l

        # Uptime
        uptime | awk -F'up ' '{print \$2}' | awk -F',' '{print \$1}'
    " 2>/dev/null
}

get_pm2_details() {
    ssh "$SERVER" "pm2 jlist 2>/dev/null | jq -r '.[] | select(.name==\"wattlewool\") |
        \"\\(.pm2_env.pm_id),\\(.monit.cpu),\\(.monit.memory),\\(.pm2_env.restart_time),\\(.pm2_env.unstable_restarts)\"
    '"
}

get_recent_logs() {
    ssh "$SERVER" "pm2 logs wattlewool --lines 5 --nostream --raw 2>/dev/null | tail -10"
}

draw_header() {
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║${NC}          ${CYAN}SFTP Deployment Monitor${NC} - ${GREEN}$SERVER${NC}                 ${BLUE}║${NC}"
    echo -e "${BLUE}║${NC}          Refresh: ${REFRESH_RATE}s | Press Ctrl+C to exit            ${BLUE}║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

draw_server_stats() {
    local stats=$(get_server_stats)

    local cpu=$(echo "$stats" | sed -n '1p')
    local mem=$(echo "$stats" | sed -n '2p')
    local disk=$(echo "$stats" | sed -n '3p')
    local status=$(echo "$stats" | sed -n '4p')
    local ssh_conn=$(echo "$stats" | sed -n '5p')
    local uptime=$(echo "$stats" | sed -n '6p')

    # Color coding
    local cpu_color=$GREEN
    [ "$cpu" -gt 80 ] && cpu_color=$YELLOW
    [ "$cpu" -gt 90 ] && cpu_color=$RED

    local mem_color=$GREEN
    [ "$mem" -gt 80 ] && mem_color=$YELLOW
    [ "$mem" -gt 90 ] && mem_color=$RED

    local disk_color=$GREEN
    [ "$disk" -gt 80 ] && disk_color=$YELLOW
    [ "$disk" -gt 90 ] && disk_color=$RED

    local status_color=$GREEN
    [ "$status" != "online" ] && status_color=$RED

    echo -e "${CYAN}Server Statistics${NC}"
    echo "─────────────────────────────────────────────────────────────"
    printf "  CPU:     [%-20s] ${cpu_color}%3s%%${NC}\n" "$(printf '█%.0s' $(seq 1 $((cpu/5))))" "$cpu"
    printf "  Memory:  [%-20s] ${mem_color}%3s%%${NC}\n" "$(printf '█%.0s' $(seq 1 $((mem/5))))" "$mem"
    printf "  Disk:    [%-20s] ${disk_color}%3s%%${NC}\n" "$(printf '█%.0s' $(seq 1 $((disk/5))))" "$disk"
    echo ""
    printf "  PM2 Status:       ${status_color}%-10s${NC}\n" "$status"
    printf "  SSH Connections:  ${GREEN}%-10s${NC}\n" "$ssh_conn"
    printf "  Uptime:           ${GREEN}%-10s${NC}\n" "$uptime"
    echo ""
}

draw_pm2_details() {
    echo -e "${CYAN}PM2 Process Details${NC}"
    echo "─────────────────────────────────────────────────────────────"

    local pm2_data=$(get_pm2_details)

    if [ -n "$pm2_data" ]; then
        IFS=',' read -r id cpu mem restarts unstable <<< "$pm2_data"

        local mem_mb=$((mem / 1024 / 1024))

        echo "  Instance ID:       $id"
        printf "  CPU Usage:         ${GREEN}%s%%${NC}\n" "$cpu"
        printf "  Memory Usage:      ${GREEN}%sMB${NC}\n" "$mem_mb"
        printf "  Restarts:          ${YELLOW}%s${NC}\n" "$restarts"
        printf "  Unstable Restarts: ${YELLOW}%s${NC}\n" "$unstable"
    else
        echo "  ${RED}PM2 process not found${NC}"
    fi
    echo ""
}

draw_transfer_stats() {
    echo -e "${CYAN}Active Transfers${NC}"
    echo "─────────────────────────────────────────────────────────────"

    # Check for active rsync/scp processes
    local transfers=$(ssh "$SERVER" "ps aux | grep -E '(rsync|scp)' | grep -v grep | wc -l" 2>/dev/null)

    if [ "$transfers" -gt 0 ]; then
        echo -e "  ${GREEN}✓${NC} Active transfers: $transfers"

        # Show bandwidth if iftop is available
        if ssh "$SERVER" "command -v iftop >/dev/null 2>&1"; then
            local bandwidth=$(ssh "$SERVER" "iftop -t -s 1 -n 2>/dev/null | tail -1" 2>/dev/null)
            [ -n "$bandwidth" ] && echo "  Bandwidth: $bandwidth"
        fi
    else
        echo "  No active transfers"
    fi
    echo ""
}

draw_recent_logs() {
    echo -e "${CYAN}Recent Logs (Last 5 lines)${NC}"
    echo "─────────────────────────────────────────────────────────────"

    local logs=$(get_recent_logs)

    if [ -n "$logs" ]; then
        echo "$logs" | while IFS= read -r line; do
            # Color code based on content
            if echo "$line" | grep -qi error; then
                echo -e "  ${RED}$line${NC}"
            elif echo "$line" | grep -qi warn; then
                echo -e "  ${YELLOW}$line${NC}"
            else
                echo "  $line"
            fi
        done
    else
        echo "  No recent logs"
    fi
    echo ""
}

draw_footer() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "─────────────────────────────────────────────────────────────"
    echo -e "Last updated: ${CYAN}$timestamp${NC}"
}

###############################################################################
# Main Monitor Loop
###############################################################################

main() {
    # Check if server is accessible
    if ! ssh -o ConnectTimeout=5 "$SERVER" "echo test" &>/dev/null; then
        echo "Error: Cannot connect to $SERVER"
        exit 1
    fi

    # Main loop
    while true; do
        clear_screen
        draw_header
        draw_server_stats
        draw_pm2_details
        draw_transfer_stats
        draw_recent_logs
        draw_footer

        sleep "$REFRESH_RATE"
    done
}

# Handle Ctrl+C gracefully
trap 'echo -e "\n${GREEN}Monitor stopped${NC}"; exit 0' INT

# Run
main
