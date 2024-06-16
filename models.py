import os

import datetime
from atexit import register

from sqlalchemy import create_engine, func, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker, DeclarativeBase, mapped_column, Mapped



POSTGRES_USER = os.getenv["POSTGRES_USER", "postgres"]
POSTGRES_PASSWORD = os.getenv["POSTGRES_PASSWORD", "postgres"]
POSTGRES_DB_NAME = os.getenv["POSTGRES_DB_NAME","flask_db"]
POSTGRES_HOST = os.getenv["POSTGRES_HOST", "127.0.0.1"]
POSTGRES_PORT = os.getenv["POSTGRES_PORT", "5431"]


engine = create_engine(f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}'
                       f'@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB_NAME}')
Session = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass

class Messages(Base):
    __tablename__ = 'messages'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    text: Mapped[str] = mapped_column(String(120), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())

    @property
    def json(self):
        return {
            'id': self.id,
            'title': self.title,
            'text': self.text,
            'name': self.name,
            'created_at': self.created_at.isoformat()
        }


Base.metadata.create_all(bind=engine)

register(engine.dispose)



