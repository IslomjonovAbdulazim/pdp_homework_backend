#!/usr/bin/env python3
"""
Quick diagnostic tool for Homework Management System
Run this to check for common issues and validate setup
"""

import os
import sys
import importlib
from pathlib import Path


def check_python_version():
    """Check Python version compatibility"""
    version = sys.version_info
    print(f"🐍 Python Version: {version.major}.{version.minor}.{version.micro}")

    if version < (3, 8):
        print("❌ Python 3.8+ required")
        return False
    elif version >= (3, 11):
        print("✅ Python version compatible")
    else:
        print("⚠️  Python 3.11+ recommended")
    return True


def check_required_files():
    """Check if all required files exist"""
    required_files = [
        "app/__init__.py",
        "app/main.py",
        "app/database.py",
        "requirements.txt",
        ".env"
    ]

    print("\n📁 Checking required files...")
    all_good = True

    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - Missing!")
            all_good = False

    return all_good


def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        "fastapi",
        "uvicorn",
        "sqlalchemy",
        "pydantic",
        "jose",
        "passlib",
        "httpx",
        "python-dotenv"
    ]

    print("\n📦 Checking dependencies...")
    missing = []

    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - Not installed!")
            missing.append(package)

    if missing:
        print(f"\n💡 Install missing packages: pip install {' '.join(missing)}")

    return len(missing) == 0


def check_environment():
    """Check environment configuration"""
    print("\n🔐 Checking environment configuration...")

    if not Path(".env").exists():
        print("❌ .env file missing!")
        return False

    # Load .env file manually
    env_vars = {}
    try:
        with open(".env", "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    env_vars[key] = value
    except Exception as e:
        print(f"❌ Error reading .env: {e}")
        return False

    # Check critical variables
    required_vars = ["SECRET_KEY", "DATABASE_URL"]
    optional_vars = ["DEEPSEEK_API_KEY"]

    all_good = True
    for var in required_vars:
        if var in env_vars and env_vars[var]:
            if env_vars[var] in ["your-secret-key-change-this-in-production", "your-secret-key-here"]:
                print(f"⚠️  {var} - Using default value (change in production)")
            else:
                print(f"✅ {var}")
        else:
            print(f"❌ {var} - Missing or empty!")
            all_good = False

    for var in optional_vars:
        if var in env_vars and env_vars[var] and env_vars[var] != "your-deepseek-api-key-here":
            print(f"✅ {var}")
        else:
            print(f"⚠️  {var} - Not configured (AI grading won't work)")

    return all_good


def test_imports():
    """Test critical imports"""
    print("\n🔍 Testing imports...")

    test_imports = [
        ("app.main", "FastAPI app"),
        ("app.models", "Database models"),
        ("app.schemas", "Pydantic schemas"),
        ("app.routers", "API routers"),
        ("app.services", "Business services")
    ]

    all_good = True
    for module_name, description in test_imports:
        try:
            importlib.import_module(module_name)
            print(f"✅ {description}")
        except Exception as e:
            print(f"❌ {description} - Import error: {str(e)[:50]}...")
            all_good = False

    return all_good


def check_database():
    """Check database status"""
    print("\n🗄️  Checking database...")

    if Path("homework.db").exists():
        print("✅ Database file exists")

        # Try to connect
        try:
            from app.database import engine
            from sqlalchemy import text

            with engine.connect() as conn:
                result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
                tables = [row[0] for row in result]

            if len(tables) > 0:
                print(f"✅ Database has {len(tables)} tables")
                print(f"   Tables: {', '.join(tables[:5])}{'...' if len(tables) > 5 else ''}")
            else:
                print("⚠️  Database is empty - run init_db.py")

        except Exception as e:
            print(f"❌ Database connection error: {str(e)[:50]}...")
            return False
    else:
        print("❌ Database file missing - run init_db.py")
        return False

    return True


def provide_solutions():
    """Provide common solutions"""
    print("\n💡 Common Solutions:")
    print("==================")
    print("📦 Install dependencies:    pip install -r requirements.txt")
    print("🔧 Quick setup:            python setup.py")
    print("🗄️  Initialize database:    python init_db.py")
    print("🚀 Start server:           python run.py")
    print("🧪 Test API:               python test_basic.py")
    print("📚 View documentation:     http://localhost:8000/docs")


def main():
    """Run all diagnostic checks"""
    print("🔍 Homework Management System Diagnostics")
    print("=" * 50)

    checks = [
        ("Python Version", check_python_version),
        ("Required Files", check_required_files),
        ("Dependencies", check_dependencies),
        ("Environment", check_environment),
        ("Imports", test_imports),
        ("Database", check_database)
    ]

    results = []

    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"❌ {check_name} check failed: {e}")
            results.append((check_name, False))

    # Summary
    print("\n" + "=" * 50)
    print("📊 Diagnostic Summary")
    print("=" * 50)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for check_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {check_name}")

    print(f"\n🎯 Overall: {passed}/{total} checks passed")

    if passed == total:
        print("🎉 All checks passed! Your system is ready to run.")
    else:
        print("⚠️  Some issues found. See solutions below.")
        provide_solutions()


if __name__ == "__main__":
    main()