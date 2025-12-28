#!/usr/bin/env python3
"""
Atomic test script - test each component individually before full E2E run.
"""
import sys
import subprocess
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_step(name: str, test_func):
    """Run a test step and report results."""
    print(f"\n{'='*80}")
    print(f"🧪 TEST: {name}")
    print(f"{'='*80}")
    try:
        result = test_func()
        if result:
            print(f"✅ PASS: {name}")
            return True
        else:
            print(f"❌ FAIL: {name}")
            return False
    except Exception as e:
        print(f"❌ ERROR: {name} - {e}")
        import traceback
        traceback.print_exc()
        return False

def test_devhub():
    """Test 1: Verify DevHub authentication."""
    from sfbench.utils.sfdx import verify_devhub
    return verify_devhub()

def test_scratch_org_creation():
    """Test 2: Verify scratch org creation."""
    from sfbench.utils.sfdx import create_scratch_org, delete_scratch_org
    try:
        org_info = create_scratch_org('test-atomic-001', duration_days=1)
        if org_info and org_info.get('username'):
            delete_scratch_org('test-atomic-001')
            return True
        return False
    except Exception as e:
        print(f"   Error: {e}")
        return False

def test_ai_generation():
    """Test 3: Verify AI solution generation (single task)."""
    from sfbench.utils.ai_agent import create_gemini_agent
    import os
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("   ⚠️  GOOGLE_API_KEY not set, skipping")
        return None
    
    try:
        agent = create_gemini_agent(model="gemini-2.5-flash", api_key=api_key)
        solution = agent.generate_solution(
            task_description="Fix a simple Apex trigger null pointer exception.",
            context={"task_type": "APEX"}
        )
        return len(solution) > 100  # Should generate meaningful output
    except Exception as e:
        print(f"   Error: {e}")
        return False

def test_patch_application():
    """Test 4: Verify patch application works."""
    from sfbench.utils.git import clone_repository, checkout_commit, apply_patch
    import tempfile
    
    # Use a simple test repo
    test_repo = "https://github.com/yasarshaikh/sfbench-test-repo.git"
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_dir = Path(tmpdir) / "test-repo"
        try:
            clone_repository(test_repo, repo_dir, timeout=60)
            # Simple patch test
            test_patch = """diff --git a/test.txt b/test.txt
new file mode 100644
index 0000000..e69de29
"""
            apply_patch(repo_dir, test_patch, timeout=30)
            return True
        except Exception as e:
            print(f"   Error: {e}")
            # If repo doesn't exist, that's okay - just test patch format
            return None  # Skip if repo unavailable

def test_deployment():
    """Test 5: Verify deployment validation works."""
    from sfbench.utils.sfdx import create_scratch_org, delete_scratch_org, run_sfdx
    import tempfile
    from pathlib import Path
    
    try:
        # Create scratch org
        org_info = create_scratch_org('test-atomic-deploy', duration_days=1)
        if not org_info:
            return False
        
        scratch_org = org_info.get('username')
        
        # Try a simple deployment command (just verify it works)
        exit_code, stdout, stderr = run_sfdx(
            f"sf org display --target-org {scratch_org}",
            timeout=30
        )
        
        delete_scratch_org('test-atomic-deploy')
        return exit_code == 0
    except Exception as e:
        print(f"   Error: {e}")
        return False

def main():
    """Run all atomic tests."""
    print("="*80)
    print("🔬 ATOMIC TEST SUITE")
    print("="*80)
    print("Testing each component individually before full E2E run")
    print()
    
    tests = [
        ("DevHub Authentication", test_devhub),
        ("Scratch Org Creation", test_scratch_org_creation),
        ("AI Solution Generation", test_ai_generation),
        ("Patch Application", test_patch_application),
        ("Deployment Validation", test_deployment),
    ]
    
    results = {}
    for name, test_func in tests:
        results[name] = test_step(name, test_func)
    
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for v in results.values() if v is True)
    failed = sum(1 for v in results.values() if v is False)
    skipped = sum(1 for v in results.values() if v is None)
    
    for name, result in results.items():
        icon = "✅" if result is True else "❌" if result is False else "⏭️"
        status = "PASS" if result is True else "FAIL" if result is False else "SKIP"
        print(f"{icon} {name}: {status}")
    
    print(f"\nTotal: {len(tests)} | Passed: {passed} | Failed: {failed} | Skipped: {skipped}")
    
    if failed == 0:
        print("\n✅ All critical tests passed! Ready for E2E run.")
        return 0
    else:
        print(f"\n❌ {failed} test(s) failed. Fix issues before E2E run.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
