#!/bin/bash
# Quick monitoring script for evaluations

echo "🎯 Evaluation Orchestrator Status Check"
echo "========================================"
echo ""

# Check orchestrator process
if pgrep -f "orchestrator.py" > /dev/null; then
    echo "✅ Orchestrator: RUNNING"
    echo "   PID: $(pgrep -f orchestrator.py)"
else
    echo "❌ Orchestrator: NOT RUNNING"
fi

echo ""
echo "📊 Active Evaluations:"
echo "----------------------"

# Check for evaluation processes
eval_count=0
for model in "grok-4.1-fast" "claude-3.5-haiku" "gemini-3-flash"; do
    if pgrep -f "evaluate.py.*$model" > /dev/null; then
        pid=$(pgrep -f "evaluate.py.*$model" | head -1)
        echo "  ✅ $model (PID: $pid)"
        eval_count=$((eval_count + 1))
    else
        echo "  ❌ $model: Not running"
    fi
done

echo ""
echo "📋 Recent Log Activity:"
echo "----------------------"

# Show last lines from orchestrator log
if [ -f /tmp/orchestrator.log ]; then
    echo "Orchestrator log (last 10 lines):"
    tail -10 /tmp/orchestrator.log | sed 's/^/  /'
else
    echo "  No orchestrator log found"
fi

echo ""
echo "💾 Scratch Org Usage:"
echo "-------------------"
sf org list --json 2>/dev/null | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    scratch_orgs = data.get('result', {}).get('scratchOrgs', [])
    active = [o for o in scratch_orgs if o.get('status') == 'Active']
    print(f'  Active scratch orgs: {len(active)}/40')
    if active:
        print('  Recent orgs:')
        for org in active[:5]:
            print(f'    - {org.get(\"alias\", org.get(\"username\", \"N/A\"))}')
except:
    print('  Could not check scratch org status')
" 2>/dev/null || echo "  Could not check scratch org status"

echo ""
echo "📈 Resource Usage:"
echo "-----------------"
echo "  CPU: $(ps aux | grep -E 'evaluate.py|orchestrator' | grep -v grep | awk '{sum+=$3} END {print sum"%"}')"
echo "  Memory: $(ps aux | grep -E 'evaluate.py|orchestrator' | grep -v grep | awk '{sum+=$4} END {print sum"%"}')"

echo ""
echo "💡 Commands:"
echo "  - Watch orchestrator: tail -f /tmp/orchestrator.log"
echo "  - Check individual logs: ls -lt /tmp/eval_*.log | head -3"
echo "  - Full status: python3 scripts/orchestrator.py (if not running)"
