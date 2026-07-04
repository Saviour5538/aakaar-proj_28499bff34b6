import uuid
from datetime import datetime, timedelta
from database.models import Base, engine, SessionLocal, User, Task, Session

def seed_database():
    session = SessionLocal()
    try:
        # Clear existing data
        session.query(Task).delete()
        session.query(Session).delete()
        session.query(User).delete()

        # Insert sample users
        user1 = User(
            id=uuid.uuid4(),
            email="alice@example.com",
            password_hash="hashed_password_1",
            created_at=datetime.utcnow()
        )
        user2 = User(
            id=uuid.uuid4(),
            email="bob@example.com",
            password_hash="hashed_password_2",
            created_at=datetime.utcnow()
        )
        user3 = User(
            id=uuid.uuid4(),
            email="charlie@example.com",
            password_hash="hashed_password_3",
            created_at=datetime.utcnow()
        )

        session.add_all([user1, user2, user3])
        session.commit()

        # Insert sample tasks
        task1 = Task(
            id=uuid.uuid4(),
            user_id=user1.id,
            title="Buy groceries",
            description="Milk, Bread, Eggs",
            completed=False,
            created_at=datetime.utcnow()
        )
        task2 = Task(
            id=uuid.uuid4(),
            user_id=user2.id,
            title="Complete project",
            description="Finish the TaskFlow app",
            completed=False,
            created_at=datetime.utcnow()
        )
        task3 = Task(
            id=uuid.uuid4(),
            user_id=user3.id,
            title="Read a book",
            description="Start reading 'Atomic Habits'",
            completed=False,
            created_at=datetime.utcnow()
        )

        session.add_all([task1, task2, task3])
        session.commit()

        # Insert sample sessions
        session1 = Session(
            id=uuid.uuid4(),
            user_id=user1.id,
            token="sample_token_1",
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(days=1)
        )
        session2 = Session(
            id=uuid.uuid4(),
            user_id=user2.id,
            token="sample_token_2",
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(days=1)
        )
        session3 = Session(
            id=uuid.uuid4(),
            user_id=user3.id,
            token="sample_token_3",
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(days=1)
        )

        session.add_all([session1, session2, session3])
        session.commit()

    finally:
        session.close()

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    seed_database()