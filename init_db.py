#!/usr/bin/env python3
"""
Database initialization script for Homework Management System
Run this script to create tables and add initial admin user
"""

import os
import sys
from sqlalchemy.orm import Session

# Add the app directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, SessionLocal, Base
from app.models import User, Group, Homework, Submission, Grade, Session as UserSession
from app.utils.security import get_password_hash


def create_tables():
    """Create all database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created successfully")


def create_admin_user(db: Session):
    """Create default admin user if not exists"""
    print("Checking for admin user...")

    admin = db.query(User).filter(User.role == "admin").first()
    if admin:
        print(f"✓ Admin user already exists: {admin.username}")
        return admin

    # Create default admin
    admin_user = User(
        fullname="System Administrator",
        username="admin",
        password_hash=get_password_hash("admin123"),  # Change this in production!
        role="admin"
    )

    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)

    print(f"✓ Created admin user: {admin_user.username}")
    print("⚠️  Default password is 'admin123' - CHANGE THIS IN PRODUCTION!")

    return admin_user


def create_sample_data(db: Session):
    """Create sample teacher, group, and students for testing"""
    print("Creating sample data...")

    # Check if sample data already exists
    if db.query(User).filter(User.role == "teacher").first():
        print("✓ Sample data already exists")
        return

    # Create sample teacher
    teacher = User(
        fullname="John Smith",
        username="teacher1",
        password_hash=get_password_hash("teacher123"),
        role="teacher"
    )
    db.add(teacher)
    db.flush()  # Get teacher ID

    # Create sample group
    group = Group(
        name="Computer Science 101",
        teacher_id=teacher.id
    )
    db.add(group)
    db.flush()  # Get group ID

    # Create sample students
    students = [
        User(
            fullname="Alice Johnson",
            username="alice",
            password_hash=get_password_hash("student123"),
            role="student",
            group_id=group.id
        ),
        User(
            fullname="Bob Wilson",
            username="bob",
            password_hash=get_password_hash("student123"),
            role="student",
            group_id=group.id
        ),
        User(
            fullname="Charlie Brown",
            username="charlie",
            password_hash=get_password_hash("student123"),
            role="student",
            group_id=group.id
        )
    ]

    for student in students:
        db.add(student)

    db.commit()

    print("✓ Created sample teacher: teacher1 (password: teacher123)")
    print("✓ Created sample group: Computer Science 101")
    print("✓ Created sample students: alice, bob, charlie (password: student123)")


def main():
    """Main initialization function"""
    print("🚀 Initializing Homework Management System Database")
    print("=" * 50)

    try:
        # Create tables
        create_tables()

        # Create database session
        db = SessionLocal()

        try:
            # Create admin user
            create_admin_user(db)

            # Create sample data for testing
            create_sample_data(db)

            print("\n" + "=" * 50)
            print("✅ Database initialization completed successfully!")
            print("\n📋 Login credentials:")
            print("   Admin: admin / admin123")
            print("   Teacher: teacher1 / teacher123")
            print("   Students: alice, bob, charlie / student123")
            print("\n⚠️  Remember to change default passwords in production!")

        finally:
            db.close()

    except Exception as e:
        print(f"❌ Error during initialization: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()