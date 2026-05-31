#!/usr/bin/env python3
"""
ADK Project Verification Script
Checks if the project structure is correctly configured for adk web
"""

import os
import sys
from pathlib import Path

def check_structure():
    """Verify the ADK project structure"""
    print("=" * 70)
    print("🔍 ADK PROJECT STRUCTURE VERIFICATION")
    print("=" * 70)
    
    checks = []
    current_dir = Path.cwd()
    
    # Check 1: adk.yaml exists
    adk_yaml = current_dir / "adk.yaml"
    check = {
        "name": "adk.yaml exists",
        "passed": adk_yaml.exists(),
        "file": str(adk_yaml)
    }
    checks.append(check)
    print(f"{'✅' if check['passed'] else '❌'} adk.yaml exists")
    
    # Check 2: my_agent directory exists
    my_agent_dir = current_dir / "my_agent"
    check = {
        "name": "my_agent/ directory exists",
        "passed": my_agent_dir.exists() and my_agent_dir.is_dir(),
        "file": str(my_agent_dir)
    }
    checks.append(check)
    print(f"{'✅' if check['passed'] else '❌'} my_agent/ directory exists")
    
    # Check 3: my_agent/agent.py exists
    agent_py = my_agent_dir / "agent.py"
    check = {
        "name": "my_agent/agent.py exists",
        "passed": agent_py.exists(),
        "file": str(agent_py)
    }
    checks.append(check)
    print(f"{'✅' if check['passed'] else '❌'} my_agent/agent.py exists")
    
    # Check 4: my_agent/__init__.py exists
    init_py = my_agent_dir / "__init__.py"
    check = {
        "name": "my_agent/__init__.py exists",
        "passed": init_py.exists(),
        "file": str(init_py)
    }
    checks.append(check)
    print(f"{'✅' if check['passed'] else '❌'} my_agent/__init__.py exists")
    
    # Check 5: .adkignore exists
    adkignore = current_dir / ".adkignore"
    check = {
        "name": ".adkignore exists",
        "passed": adkignore.exists(),
        "file": str(adkignore)
    }
    checks.append(check)
    print(f"{'✅' if check['passed'] else '❌'} .adkignore exists")
    
    # Check 6: .env exists
    env_file = current_dir / ".env"
    check = {
        "name": ".env file exists",
        "passed": env_file.exists(),
        "file": str(env_file)
    }
    checks.append(check)
    print(f"{'✅' if check['passed'] else '❌'} .env file exists")
    
    # Check 7: root_agent in agent.py
    if agent_py.exists():
        with open(agent_py, 'r') as f:
            content = f.read()
            has_root_agent = "root_agent" in content and "Agent(" in content
            check = {
                "name": "root_agent defined in agent.py",
                "passed": has_root_agent,
                "file": str(agent_py)
            }
            checks.append(check)
            print(f"{'✅' if has_root_agent else '❌'} root_agent defined in agent.py")
    
    # Check 8: adk.yaml has exclude_patterns
    if adk_yaml.exists():
        with open(adk_yaml, 'r') as f:
            content = f.read()
            has_exclude = "exclude_patterns" in content and "node_modules" in content
            check = {
                "name": "adk.yaml has exclude_patterns (node_modules)",
                "passed": has_exclude,
                "file": str(adk_yaml)
            }
            checks.append(check)
            print(f"{'✅' if has_exclude else '❌'} adk.yaml has exclude_patterns (node_modules)")
    
    # Summary
    print("\n" + "=" * 70)
    passed = sum(1 for c in checks if c['passed'])
    total = len(checks)
    print(f"Summary: {passed}/{total} checks passed")
    
    if passed == total:
        print("✅ Project structure is CORRECT!")
        print("\n🚀 Ready to run: .venv\\Scripts\\python.exe -m google.adk web")
        return 0
    else:
        print("❌ Some checks failed. Please review the errors above.")
        return 1
    
    print("=" * 70)

if __name__ == "__main__":
    sys.exit(check_structure())
