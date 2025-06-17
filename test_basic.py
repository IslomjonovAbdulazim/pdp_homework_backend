#!/usr/bin/env python3
"""
Basic API tests for Homework Management System
Run this after starting the server to verify everything works
"""

import requests
import json
from datetime import datetime, timedelta

# Base URL - adjust if your server runs on different host/port
BASE_URL = "http://localhost:8000"


def test_server_health():
    """Test if server is running"""
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✓ Server is running")
            return True
        else:
            print(f"✗ Server responded with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to server. Is it running?")
        return False


def test_constants():
    """Test constants endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/app/constants")
        if response.status_code == 200:
            data = response.json()
            print("✓ Constants endpoint working")
            print(f"  - Line limits: {data['line_limit_options']}")
            print(f"  - File extensions: {data['file_extension_options'][:3]}...")
            return True
        else:
            print(f"✗ Constants endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Constants test failed: {e}")
        return False


def test_admin_login():
    """Test admin login"""
    try:
        login_data = {
            "username": "admin",
            "password": "admin123",
            "device_name": "Test Device"
        }

        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)

        if response.status_code == 200:
            data = response.json()
            print("✓ Admin login successful")
            print(f"  - User: {data['user']['fullname']}")
            print(f"  - Role: {data['user']['role']}")
            return data['access_token']
        else:
            print(f"✗ Admin login failed: {response.status_code}")
            if response.status_code == 422:
                print(f"  Error details: {response.json()}")
            return None
    except Exception as e:
        print(f"✗ Admin login test failed: {e}")
        return None


def test_teacher_login():
    """Test teacher login"""
    try:
        login_data = {
            "username": "teacher1",
            "password": "teacher123",
            "device_name": "Test Device"
        }

        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)

        if response.status_code == 200:
            data = response.json()
            print("✓ Teacher login successful")
            print(f"  - User: {data['user']['fullname']}")
            return data['access_token']
        else:
            print(f"✗ Teacher login failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"✗ Teacher login test failed: {e}")
        return None


def test_student_login():
    """Test student login"""
    try:
        login_data = {
            "username": "alice",
            "password": "student123",
            "device_name": "Test Device"
        }

        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)

        if response.status_code == 200:
            data = response.json()
            print("✓ Student login successful")
            print(f"  - User: {data['user']['fullname']}")
            return data['access_token']
        else:
            print(f"✗ Student login failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"✗ Student login test failed: {e}")
        return None


def test_admin_endpoints(token):
    """Test admin endpoints"""
    headers = {"Authorization": f"Bearer {token}"}

    try:
        # Test get teachers
        response = requests.get(f"{BASE_URL}/admin/teachers", headers=headers)
        if response.status_code == 200:
            teachers = response.json()
            print(f"✓ Admin can view teachers ({len(teachers)} found)")
        else:
            print(f"✗ Admin teachers endpoint failed: {response.status_code}")

        # Test get groups
        response = requests.get(f"{BASE_URL}/admin/groups", headers=headers)
        if response.status_code == 200:
            groups = response.json()
            print(f"✓ Admin can view groups ({len(groups)} found)")
        else:
            print(f"✗ Admin groups endpoint failed: {response.status_code}")

    except Exception as e:
        print(f"✗ Admin endpoints test failed: {e}")


def test_teacher_endpoints(token):
    """Test teacher endpoints"""
    headers = {"Authorization": f"Bearer {token}"}

    try:
        # Test get homework
        response = requests.get(f"{BASE_URL}/teacher/homework", headers=headers)
        if response.status_code == 200:
            homework = response.json()
            print(f"✓ Teacher can view homework ({len(homework)} found)")
        else:
            print(f"✗ Teacher homework endpoint failed: {response.status_code}")

        # Test get groups
        response = requests.get(f"{BASE_URL}/teacher/groups", headers=headers)
        if response.status_code == 200:
            groups = response.json()
            print(f"✓ Teacher can view groups ({len(groups)} found)")
        else:
            print(f"✗ Teacher groups endpoint failed: {response.status_code}")

    except Exception as e:
        print(f"✗ Teacher endpoints test failed: {e}")


def test_student_endpoints(token):
    """Test student endpoints"""
    headers = {"Authorization": f"Bearer {token}"}

    try:
        # Test get homework
        response = requests.get(f"{BASE_URL}/student/homework", headers=headers)
        if response.status_code == 200:
            homework = response.json()
            print(f"✓ Student can view homework ({len(homework)} found)")
        else:
            print(f"✗ Student homework endpoint failed: {response.status_code}")

        # Test get leaderboard
        response = requests.get(f"{BASE_URL}/student/leaderboard", headers=headers)
        if response.status_code == 200:
            leaderboard = response.json()
            print(f"✓ Student can view leaderboard")
        else:
            print(f"✗ Student leaderboard endpoint failed: {response.status_code}")

    except Exception as e:
        print(f"✗ Student endpoints test failed: {e}")


def test_create_homework(token):
    """Test creating homework (teacher)"""
    headers = {"Authorization": f"Bearer {token}"}

    homework_data = {
        "title": "Test Assignment",
        "description": "Write a simple Python function to add two numbers",
        "points": 50,
        "start_date": datetime.now().isoformat(),
        "deadline": (datetime.now() + timedelta(days=7)).isoformat(),
        "line_limit": 300,
        "file_extension": ".py",
        "group_id": 1,
        "ai_grading_prompt": "Check if the function correctly adds two numbers and follows good coding practices"
    }

    try:
        response = requests.post(f"{BASE_URL}/teacher/homework", json=homework_data, headers=headers)
        if response.status_code == 200:
            homework = response.json()
            print(f"✓ Created test homework: {homework['title']}")
            return homework['id']
        else:
            print(f"✗ Create homework failed: {response.status_code}")
            if response.status_code == 422:
                print(f"  Error details: {response.json()}")
            return None
    except Exception as e:
        print(f"✗ Create homework test failed: {e}")
        return None


def main():
    """Run all tests"""
    print("🧪 Running Basic API Tests")
    print("=" * 50)

    # Test server health
    if not test_server_health():
        return

    # Test public endpoints
    test_constants()

    print("\n" + "=" * 30)
    print("🔐 Testing Authentication")
    print("=" * 30)

    # Test logins
    admin_token = test_admin_login()
    teacher_token = test_teacher_login()
    student_token = test_student_login()

    print("\n" + "=" * 30)
    print("👑 Testing Admin Endpoints")
    print("=" * 30)

    if admin_token:
        test_admin_endpoints(admin_token)

    print("\n" + "=" * 30)
    print("🎓 Testing Teacher Endpoints")
    print("=" * 30)

    if teacher_token:
        test_teacher_endpoints(teacher_token)
        homework_id = test_create_homework(teacher_token)

    print("\n" + "=" * 30)
    print("📚 Testing Student Endpoints")
    print("=" * 30)

    if student_token:
        test_student_endpoints(student_token)

    print("\n" + "=" * 50)
    print("✅ Basic API testing completed!")
    print("\n📋 Next steps:")
    print("   1. Check server logs for any errors")
    print("   2. Test file upload functionality")
    print("   3. Test AI grading with DeepSeek API")
    print("   4. Verify all role permissions work correctly")


if __name__ == "__main__":
    main()