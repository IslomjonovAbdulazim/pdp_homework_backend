#!/usr/bin/env python3
"""
Configuration validator for Homework Management System
Validates .env file and configuration settings
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv


def load_environment():
    """Load environment variables from .env file"""
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found!")
        print("💡 Run 'python setup.py' or 'python config_manager.py' to create one")
        return False

    load_dotenv()
    print("✅ Environment variables loaded from .env")
    return True


def validate_security_settings():
    """Validate security configuration"""
    print("\n🔐 Security Settings")
    print("-" * 30)

    issues = []

    # Secret Key
    secret_key = os.getenv("SECRET_KEY", "")
    if not secret_key:
        issues.append("SECRET_KEY is not set")
    elif secret_key in ["your-secret-key-change-this-in-production", "fallback-secret-key-change-in-production"]:
        issues.append("SECRET_KEY is using default value - change for production!")
    elif len(secret_key) < 32:
        issues.append("SECRET_KEY is too short (minimum 32 characters recommended)")
    else:
        print(f"✅ SECRET_KEY configured ({len(secret_key)} characters)")

    # JWT Algorithm
    algorithm = os.getenv("JWT_ALGORITHM", "")
    if algorithm in ["HS256", "HS384", "HS512"]:
        print(f"✅ JWT_ALGORITHM: {algorithm}")
    elif algorithm:
        issues.append(f"JWT_ALGORITHM '{algorithm}' may not be supported")
    else:
        print("⚠️  JWT_ALGORITHM not set, using default: HS256")

    # Token expiry
    try:
        expiry = int(os.getenv("ACCESS_TOKEN_EXPIRE_HOURS", "168"))
        if expiry < 1:
            issues.append("ACCESS_TOKEN_EXPIRE_HOURS must be positive")
        elif expiry > 8760:  # 1 year
            issues.append("ACCESS_TOKEN_EXPIRE_HOURS is very long (>1 year)")
        else:
            print(f"✅ Token expiry: {expiry} hours ({expiry / 24:.1f} days)")
    except ValueError:
        issues.append("ACCESS_TOKEN_EXPIRE_HOURS must be a number")

    return issues


def validate_ai_settings():
    """Validate AI service configuration"""
    print("\n🤖 AI Service Settings")
    print("-" * 30)

    issues = []

    # API Key
    api_key = os.getenv("DEEPSEEK_API_KEY", "")
    if not api_key or api_key == "your-deepseek-api-key-here":
        issues.append("DEEPSEEK_API_KEY not configured - AI grading will not work")
        print("⚠️  DeepSeek API key not configured")
    else:
        print(f"✅ DeepSeek API key configured ({api_key[:8]}...)")

    # API URL
    api_url = os.getenv("DEEPSEEK_API_URL", "")
    if api_url:
        if api_url.startswith("https://"):
            print(f"✅ API URL: {api_url}")
        else:
            issues.append("DEEPSEEK_API_URL should use HTTPS")
    else:
        issues.append("DEEPSEEK_API_URL not set")

    # Model
    model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
    print(f"✅ Model: {model}")

    # Temperature
    try:
        temp = float(os.getenv("DEEPSEEK_TEMPERATURE", "0.3"))
        if 0 <= temp <= 2:
            print(f"✅ Temperature: {temp}")
        else:
            issues.append("DEEPSEEK_TEMPERATURE should be between 0 and 2")
    except ValueError:
        issues.append("DEEPSEEK_TEMPERATURE must be a number")

    # Max tokens
    try:
        max_tokens = int(os.getenv("DEEPSEEK_MAX_TOKENS", "1000"))
        if max_tokens > 0:
            print(f"✅ Max tokens: {max_tokens}")
        else:
            issues.append("DEEPSEEK_MAX_TOKENS must be positive")
    except ValueError:
        issues.append("DEEPSEEK_MAX_TOKENS must be a number")

    # Timeout
    try:
        timeout = int(os.getenv("DEEPSEEK_TIMEOUT", "30"))
        if timeout > 0:
            print(f"✅ Timeout: {timeout} seconds")
        else:
            issues.append("DEEPSEEK_TIMEOUT must be positive")
    except ValueError:
        issues.append("DEEPSEEK_TIMEOUT must be a number")

    return issues


def validate_database_settings():
    """Validate database configuration"""
    print("\n🗄️  Database Settings")
    print("-" * 30)

    issues = []

    db_url = os.getenv("DATABASE_URL", "")
    if not db_url:
        issues.append("DATABASE_URL not set")
    elif db_url.startswith("sqlite://"):
        print(f"✅ Database: SQLite")
        # Check if file path is accessible
        if "///" in db_url:
            db_path = db_url.split("///")[1]
            db_dir = Path(db_path).parent
            if not db_dir.exists():
                issues.append(f"Database directory does not exist: {db_dir}")
            else:
                print(f"✅ Database path: {db_path}")
    elif db_url.startswith("postgresql://"):
        print(f"✅ Database: PostgreSQL")
        # Validate pool settings for PostgreSQL
        try:
            pool_size = int(os.getenv("DB_POOL_SIZE", "5"))
            if pool_size > 0:
                print(f"✅ Pool size: {pool_size}")
            else:
                issues.append("DB_POOL_SIZE must be positive")
        except ValueError:
            issues.append("DB_POOL_SIZE must be a number")
    else:
        issues.append(f"Unsupported database URL format: {db_url[:20]}...")

    return issues


def validate_server_settings():
    """Validate server configuration"""
    print("\n🌐 Server Settings")
    print("-" * 30)

    issues = []

    # Host
    host = os.getenv("HOST", "127.0.0.1")
    print(f"✅ Host: {host}")

    # Port
    try:
        port = int(os.getenv("PORT", "8000"))
        if 1 <= port <= 65535:
            print(f"✅ Port: {port}")
        else:
            issues.append("PORT must be between 1 and 65535")
    except ValueError:
        issues.append("PORT must be a number")

    # Reload
    reload = os.getenv("RELOAD", "true").lower()
    if reload in ["true", "false"]:
        print(f"✅ Auto-reload: {reload}")
    else:
        issues.append("RELOAD must be 'true' or 'false'")

    # Debug
    debug = os.getenv("DEBUG", "false").lower()
    if debug in ["true", "false"]:
        print(f"✅ Debug mode: {debug}")
        if debug == "true":
            print("⚠️  Debug mode enabled - disable for production!")
    else:
        issues.append("DEBUG must be 'true' or 'false'")

    # Log level
    log_level = os.getenv("LOG_LEVEL", "info").lower()
    valid_levels = ["critical", "error", "warning", "info", "debug"]
    if log_level in valid_levels:
        print(f"✅ Log level: {log_level}")
    else:
        issues.append(f"LOG_LEVEL must be one of: {', '.join(valid_levels)}")

    return issues


def validate_limits():
    """Validate system limits"""
    print("\n⚙️  System Limits")
    print("-" * 30)

    issues = []

    limits = [
        ("MAX_FILES_PER_HOMEWORK", 1, 50),
        ("MAX_LINES_PER_FILE", 10, 10000),
        ("MAX_SESSIONS_PER_USER", 1, 10),
        ("MAX_FILE_SIZE_MB", 1, 100)
    ]

    for limit_name, min_val, max_val in limits:
        try:
            value = int(os.getenv(limit_name, "0"))
            if min_val <= value <= max_val:
                print(f"✅ {limit_name}: {value}")
            else:
                issues.append(f"{limit_name} should be between {min_val} and {max_val}")
        except ValueError:
            issues.append(f"{limit_name} must be a number")

    # Check list options
    line_limits = os.getenv("LINE_LIMIT_OPTIONS", "")
    if line_limits:
        try:
            limits_list = [int(x.strip()) for x in line_limits.split(",")]
            print(f"✅ Line limit options: {limits_list}")
        except ValueError:
            issues.append("LINE_LIMIT_OPTIONS must be comma-separated numbers")
    else:
        issues.append("LINE_LIMIT_OPTIONS not set")

    file_exts = os.getenv("FILE_EXTENSION_OPTIONS", "")
    if file_exts:
        exts_list = [x.strip() for x in file_exts.split(",")]
        print(f"✅ File extensions: {len(exts_list)} types")
    else:
        issues.append("FILE_EXTENSION_OPTIONS not set")

    return issues


def validate_imports():
    """Validate that the application can be imported"""
    print("\n📦 Import Validation")
    print("-" * 30)

    issues = []

    try:
        # Test importing constants (this will validate config)
        from app.utils.constants import validate_configuration
        print("✅ App constants imported successfully")

        # Run built-in validation
        try:
            validate_configuration()
            print("✅ Built-in configuration validation passed")
        except Exception as e:
            issues.append(f"Built-in validation failed: {str(e)}")

    except Exception as e:
        issues.append(f"Failed to import app constants: {str(e)}")
        return issues

    try:
        from app.main import app
        print("✅ FastAPI app imported successfully")
    except Exception as e:
        issues.append(f"Failed to import FastAPI app: {str(e)}")

    return issues


def main():
    """Main validation function"""
    print("🔍 Configuration Validation")
    print("=" * 50)

    # Load environment
    if not load_environment():
        return

    # Run validation sections
    all_issues = []

    validation_sections = [
        ("Security Settings", validate_security_settings),
        ("AI Service Settings", validate_ai_settings),
        ("Database Settings", validate_database_settings),
        ("Server Settings", validate_server_settings),
        ("System Limits", validate_limits),
        ("Import Validation", validate_imports)
    ]

    for section_name, validator in validation_sections:
        try:
            issues = validator()
            all_issues.extend(issues)
        except Exception as e:
            all_issues.append(f"Error validating {section_name}: {str(e)}")

    # Summary
    print("\n" + "=" * 50)
    print("📊 Validation Summary")
    print("=" * 50)

    if all_issues:
        print(f"❌ Found {len(all_issues)} issue(s):")
        for i, issue in enumerate(all_issues, 1):
            print(f"   {i}. {issue}")

        print("\n💡 Suggestions:")
        print("   • Run 'python config_manager.py' for interactive setup")
        print("   • Check .env.example for reference configuration")
        print("   • Ensure all required environment variables are set")
        print("   • Verify API keys and database connectivity")
    else:
        print("🎉 All validation checks passed!")
        print("✅ Your configuration looks good!")

        print("\n🚀 Ready to start:")
        print("   python run.py")


if __name__ == "__main__":
    main()