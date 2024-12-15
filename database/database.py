from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///checkPriceWB.db"  # Путь к вашей базе данных

engine = create_engine(DATABASE_URL)
Base = declarative_base()

class Feedback(Base):
    __tablename__ = 'feedback'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)  # ID пользователя Telegram
    message = Column(String)  # Отзыв пользователя

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True)  # ID пользователя Telegram (должен быть уникальным)
    name = Column(String)  # Имя пользователя
    age = Column(Integer)  # Возраст пользователя

# Создаем таблицы
Base.metadata.create_all(engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
