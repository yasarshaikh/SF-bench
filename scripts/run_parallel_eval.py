#!/usr/bin/env python3
"""
Run parallel evaluations for multiple models.
"""
import subprocess
import sys
import os
from pathlib import Path
from datetime import datetime
import time

def run_evaluation(model_name: str, provider: str, api_key_env: str, tasks_file: str, output_dir: str, scratch_org_prefix: str):
    """Run a single evaluation in the background."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    scratch_org_alias = f"{scratch_org_prefix}-{model_name.replace('/', '-').replace('_', '-')}-{timestamp}"
    
    log_file = Path(f"/tmp/eval_{model_name.replace('/', '-')}_{timestamp}.log")
    
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
    
    print(f"🚀 Starting evaluation for {model_name}...")
    print(f"   Scratch org: {scratch_org_alias}")
    print(f"   Log: {log_file}")
    
    with open(log_file, 'w') as f:
        env = os.environ.copy()
        if api_key_env:
            env[api_key_env] = os.getenv(api_key_env, '')
        
        process = subprocess.Popen(
            cmd,
            stdout=f,
            stderr=subprocess.STDOUT,
            env=env,
            cwd=Path(__file__).parent.parent
        )
    
    return process, log_file, scratch_org_alias

def main():
    """Run parallel evaluations."""
    tasks_file = "data/tasks/verified.json"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Define models to evaluate
    evaluations = [
        {
            "model": "grok-4.1-fast",
            "provider": "routellm",
            "api_key_env": "ROUTELLM_API_KEY",
            "output_dir": f"results/grok-4.1-fast-{timestamp}",
            "scratch_org_prefix": "sfbench-grok"
        },
        {
            "model": "anthropic/claude-3.5-haiku",
            "provider": "openrouter",
            "api_key_env": "OPENROUTER_API_KEY",
            "output_dir": f"results/haiku-4.5-{timestamp}",
            "scratch_org_prefix": "sfbench-haiku"
        },
        {
            "model": "gemini-3-flash-preview",
            "provider": "routellm",
            "api_key_env": "ROUTELLM_API_KEY",
            "output_dir": f"results/gemini-3-flash-{timestamp}",
            "scratch_org_prefix": "sfbench-gemini3"
        }
    ]
    
    processes = []
    log_files = []
    scratch_orgs = []
    
    print("=" * 80)
    print("🚀 Starting Parallel Evaluations")
    print("=" * 80)
    print()
    
    # Start all evaluations
    for eval_config in evaluations:
        process, log_file, scratch_org = run_evaluation(
            eval_config["model"],
            eval_config["provider"],
            eval_config["api_key_env"],
            tasks_file,
            eval_config["output_dir"],
            eval_config["scratch_org_prefix"]
        )
        processes.append((process, eval_config["model"]))
        log_files.append((log_file, eval_config["model"]))
        scratch_orgs.append(scratch_org)
        time.sleep(5)  # Stagger starts slightly
    
    print()
    print("=" * 80)
    print("📊 Monitoring Progress")
    print("=" * 80)
    print()
    
    # Monitor progress
    completed = []
    while len(completed) < len(processes):
        for i, (process, model_name) in enumerate(processes):
            if i in completed:
                continue
            
            if process.poll() is not None:
                # Process finished
                exit_code = process.returncode
                log_file, _ = log_files[i]
                
                print(f"\n{'✅' if exit_code == 0 else '❌'} {model_name} finished (exit code: {exit_code})")
                print(f"   Log: {log_file}")
                
                # Show last 20 lines of log
                if log_file.exists():
                    with open(log_file, 'r') as f:
                        lines = f.readlines()
                        if lines:
                            print(f"   Last output:")
                            for line in lines[-5:]:
                                print(f"      {line.rstrip()}")
                
                completed.append(i)
        
        if len(completed) < len(processes):
            time.sleep(10)
            # Show status
            running = [name for i, (_, name) in enumerate(processes) if i not in completed]
            if running:
                print(f"⏳ Running: {', '.join(running)}", end='\r')
    
    print()
    print("=" * 80)
    print("✅ All Evaluations Complete")
    print("=" * 80)
    print()
    
    # Summary
    for i, (process, model_name) in enumerate(processes):
        exit_code = process.returncode
        log_file, _ = log_files[i]
        status = "✅ SUCCESS" if exit_code == 0 else "❌ FAILED"
        print(f"{status}: {model_name}")
        print(f"   Log: {log_file}")
        print(f"   Scratch org: {scratch_orgs[i]}")
        print()

if __name__ == "__main__":
    main()
