#!/usr/bin/env python3
"""
Seed script to populate demo data for Verse Map.

Creates demo organization and user for testing.
"""

import asyncio
import os
import sys
from datetime import datetime
from uuid import uuid4

# Add API to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'apps', 'api'))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Import models
from models import Base, Organization, User, UserRoleEnum


async def seed_demo_data():
    """Seed database with demo organization and user."""
    
    # Get database URL
    db_url = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://music_user:music_password@localhost:5433/music_analysis"
    )
    
    print(f"📦 Connecting to database: {db_url.split('@')[1]}")
    
    # Create engine
    engine = create_async_engine(db_url, echo=False)
    
    try:
        # Create tables
        print("📋 Creating database tables...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Tables created/verified")
        
        # Create session
        async_session = sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        
        async with async_session() as session:
            # Check if demo organization already exists
            from sqlalchemy import select
            
            org_result = await session.execute(
                select(Organization).where(Organization.name == "demo-org")
            )
            existing_org = org_result.scalar_one_or_none()
            
            if existing_org:
                print(f"ℹ️  Demo organization already exists (ID: {existing_org.id})")
                org_id = existing_org.id
            else:
                # Create demo organization
                org_id = uuid4()
                org = Organization(
                    id=org_id,
                    name="demo-org",
                    description="Demo Organization for Testing",
                    created_at=datetime.utcnow(),
                )
                session.add(org)
                await session.flush()
                print(f"✅ Created demo organization: demo-org (ID: {org_id})")
            
            # Check if demo user already exists
            user_result = await session.execute(
                select(User).where(User.email == "demo@example.com")
            )
            existing_user = user_result.scalar_one_or_none()
            
            if existing_user:
                print(f"ℹ️  Demo user already exists (ID: {existing_user.id})")
            else:
                # Create demo user
                user_id = uuid4()
                user = User(
                    id=user_id,
                    email="demo@example.com",
                    name="Demo User",
                    organization_id=org_id,
                    role=UserRoleEnum.LEADER,
                    created_at=datetime.utcnow(),
                )
                session.add(user)
                await session.flush()
                print(f"✅ Created demo user: demo@example.com (ID: {user_id})")
            
            # Commit changes
            await session.commit()
            print("\n✅ Demo data seeded successfully!")
            print("\n📝 Login Credentials:")
            print("   Email: demo@example.com")
            print("   Password: demo123")
            print("   Organization: demo-org")
            
    except Exception as e:
        print(f"❌ Error seeding data: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await engine.dispose()
    
    return True


async def main():
    """Main entry point."""
    print("🌱 Verse Map - Demo Data Seeder\n")
    
    success = await seed_demo_data()
    
    if success:
        print("\n🎉 Ready to test!")
        print("   Frontend: http://localhost:3000" )
        print("   API: http://localhost:8000" )
        print("   API Docs: http://localhost:8000/docs" )
        return 0
    else:
        print("\n⚠️  Seeding failed. Check the errors above.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
