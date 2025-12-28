#!/usr/bin/env python3
"""
Orchestrator to monitor and manage parallel evaluations.
Acts as Chief AI Officer - prevents issues before they break.
"""
import subprocess
import sys
import os
import time
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

class EvaluationOrchestrator:
    """Monitor and manage multiple parallel evaluations."""
    
    def __init__(self):
        self.evaluations: Dict[str, Dict] = {}
        self.processes: Dict[str, subprocess.Popen] = {}
        self.log_files: Dict[str, Path] = {}
        self.start_times: Dict[str, float] = {}
        self.last_check: Dict[str, float] = {}
        
    def start_evaluation(self, model_name: str, tasks_file: str, output_dir: str, 
                        scratch_org_alias: str, api_key_env: str = None):
        """Start a single evaluation."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = model_name.replace('/', '-').replace('_', '-')
        log_file = Path(f"/tmp/eval_{safe_name}_{timestamp}.log")
        
        cmd = [
            sys.executable,
            "scripts/evaluate.py",
            "--model", model_name,
            "--tasks", tasks_file,
            "--max-workers", "2",
            "--functional",
            "--output", output_dir,
            "--scratch-org", scratch_org_alias
        ]
        
        print(f"🚀 Starting: {model_name}")
        print(f"   Scratch org: {scratch_org_alias}")
        print(f"   Log: {log_file}")
        
        env = os.environ.copy()
        if api_key_env:
            env[api_key_env] = os.getenv(api_key_env, '')
        
        with open(log_file, 'w') as f:
            process = subprocess.Popen(
                cmd,
                stdout=f,
                stderr=subprocess.STDOUT,
                env=env,
                cwd=Path(__file__).parent.parent
            )
        
        self.evaluations[model_name] = {
            "scratch_org": scratch_org_alias,
            "output_dir": output_dir,
            "status": "running"
        }
        self.processes[model_name] = process
        self.log_files[model_name] = log_file
        self.start_times[model_name] = time.time()
        self.last_check[model_name] = time.time()
        
        return process, log_file
    
    def check_evaluation(self, model_name: str) -> Tuple[str, str]:
        """
        Check evaluation status.
        Returns: (status, message)
        Status: 'running', 'completed', 'failed', 'stuck', 'error'
        """
        if model_name not in self.processes:
            return "unknown", "Evaluation not found"
        
        process = self.processes[model_name]
        log_file = self.log_files[model_name]
        
        # Check if process is still running
        if process.poll() is not None:
            exit_code = process.returncode
            if exit_code == 0:
                return "completed", f"Successfully completed (exit code: {exit_code})"
            else:
                return "failed", f"Failed with exit code: {exit_code}"
        
        # Check if process is stuck (no log updates in last 5 minutes)
        if log_file.exists():
            last_modified = log_file.stat().st_mtime
            time_since_update = time.time() - last_modified
            
            if time_since_update > 300:  # 5 minutes
                # Check if it's actually stuck or just slow
                elapsed = time.time() - self.start_times[model_name]
                if elapsed > 3600:  # More than 1 hour
                    return "stuck", f"No log updates for {int(time_since_update/60)} minutes"
        
        # Check for common errors in log
        if log_file.exists():
            try:
                with open(log_file, 'r') as f:
                    content = f.read()
                    if "LIMIT_EXCEEDED" in content:
                        return "error", "Scratch org limit exceeded"
                    if "quota" in content.lower() or "rate limit" in content.lower():
                        return "error", "API quota/rate limit hit"
                    if "corrupt patch" in content.lower():
                        return "error", "Patch application errors detected"
            except:
                pass
        
        return "running", "Evaluation in progress"
    
    def get_progress(self, model_name: str) -> str:
        """Get progress information from log file."""
        log_file = self.log_files.get(model_name)
        if not log_file or not log_file.exists():
            return "No log file yet"
        
        try:
            with open(log_file, 'r') as f:
                lines = f.readlines()
                if not lines:
                    return "Log file empty"
                
                # Look for progress indicators
                last_lines = lines[-20:]
                progress_info = []
                
                for line in last_lines:
                    if "Generated" in line and "solutions" in line:
                        progress_info.append(line.strip())
                    if "Completed:" in line:
                        progress_info.append(line.strip())
                    if "Pass Rate:" in line:
                        progress_info.append(line.strip())
                    if "EVALUATION COMPLETE" in line:
                        progress_info.append(line.strip())
                
                if progress_info:
                    return " | ".join(progress_info[-3:])  # Last 3 progress items
                else:
                    return f"Running... ({len(lines)} log lines)"
        except Exception as e:
            return f"Error reading log: {e}"
    
    def monitor_all(self, check_interval: int = 30):
        """Monitor all evaluations with periodic checks."""
        print("=" * 80)
        print("🎯 ORCHESTRATOR: Monitoring All Evaluations")
        print("=" * 80)
        print()
        
        iteration = 0
        while True:
            iteration += 1
            all_complete = True
            
            print(f"\n📊 Check #{iteration} - {datetime.now().strftime('%H:%M:%S')}")
            print("-" * 80)
            
            for model_name in list(self.processes.keys()):
                status, message = self.check_evaluation(model_name)
                elapsed = int((time.time() - self.start_times[model_name]) / 60)
                progress = self.get_progress(model_name)
                
                status_icon = {
                    "running": "⏳",
                    "completed": "✅",
                    "failed": "❌",
                    "stuck": "⚠️",
                    "error": "🚨"
                }.get(status, "❓")
                
                print(f"{status_icon} {model_name}")
                print(f"   Status: {status.upper()} - {message}")
                print(f"   Elapsed: {elapsed} minutes")
                print(f"   Progress: {progress}")
                print()
                
                if status == "running":
                    all_complete = False
                elif status in ["stuck", "error"]:
                    print(f"   ⚠️  WARNING: {model_name} may need attention!")
                    all_complete = False
                elif status == "failed":
                    all_complete = False
                # completed doesn't set all_complete to False
            
            if all_complete:
                print("\n" + "=" * 80)
                print("✅ ALL EVALUATIONS COMPLETE")
                print("=" * 80)
                break
            
            print(f"\n💤 Sleeping for {check_interval} seconds...")
            time.sleep(check_interval)
        
        # Final summary
        self.print_summary()
    
    def print_summary(self):
        """Print final summary of all evaluations."""
        print("\n" + "=" * 80)
        print("📋 FINAL SUMMARY")
        print("=" * 80)
        print()
        
        for model_name, eval_info in self.evaluations.items():
            status, message = self.check_evaluation(model_name)
            log_file = self.log_files[model_name]
            elapsed = int((time.time() - self.start_times[model_name]) / 60)
            
            status_icon = "✅" if status == "completed" else "❌"
            print(f"{status_icon} {model_name}")
            print(f"   Status: {status.upper()}")
            print(f"   Duration: {elapsed} minutes")
            print(f"   Log: {log_file}")
            print(f"   Output: {eval_info['output_dir']}")
            print()

def main():
    """Main orchestrator function."""
    tasks_file = "data/tasks/verified.json"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    orchestrator = EvaluationOrchestrator()
    
    # Start all three evaluations
    print("=" * 80)
    print("🚀 ORCHESTRATOR: Starting All Evaluations")
    print("=" * 80)
    print()
    
    # Grok 4.1 Fast
    orchestrator.start_evaluation(
        "grok-4.1-fast",
        tasks_file,
        f"results/grok-4.1-fast-{timestamp}",
        f"sfbench-grok-{timestamp}",
        "ROUTELLM_API_KEY"
    )
    time.sleep(5)
    
    # Haiku 4.5
    orchestrator.start_evaluation(
        "anthropic/claude-3.5-haiku",
        tasks_file,
        f"results/haiku-4.5-{timestamp}",
        f"sfbench-haiku-{timestamp}",
        "OPENROUTER_API_KEY"
    )
    time.sleep(5)
    
    # Gemini 3 Flash
    orchestrator.start_evaluation(
        "gemini-3-flash-preview",
        tasks_file,
        f"results/gemini-3-flash-{timestamp}",
        f"sfbench-gemini3-{timestamp}",
        "ROUTELLM_API_KEY"
    )
    
    print()
    print("=" * 80)
    print("✅ All Evaluations Started")
    print("=" * 80)
    print()
    
    # Start monitoring
    orchestrator.monitor_all(check_interval=30)

if __name__ == "__main__":
    main()
