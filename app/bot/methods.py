



from app.bot.models import User
from app.database import SessionLocal


def save_user_to_db(name, phone_number, user_type):
    db = SessionLocal()
    try:
        # Check if the user already exists
        existing_user = User.query.filter_by(phone_number = phone_number).first()
        if existing_user:
            return

        # Create a new user
        new_user = User(name=name, phone_number=phone_number, user_type=user_type)
        db.add(new_user)
        db.commit()
        
        return {
            "id": new_user.id,
            "name": new_user.name,
            "phone_number": new_user.phone_number,
            "user_type": new_user.user_type.value,
        }
    except Exception as e:
        db.rollback()
        print(f"Error saving user to the database: {e}")
    finally:
        db.close()