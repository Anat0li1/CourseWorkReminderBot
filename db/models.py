from sqlalchemy import BigInteger, String, ForeignKey, DateTime, Date, SmallInteger, Integer, Boolean
from sqlalchemy.ext.asyncio import create_async_engine, AsyncAttrs, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
import os
from dotenv import load_dotenv
import asyncio
import ssl

load_dotenv()

#For global
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = True
ssl_context.verify_mode = ssl.CERT_REQUIRED

engine = create_async_engine(os.getenv("DBURL"), 
                             connect_args={"ssl": ssl_context})

async_session = async_sessionmaker(engine)

class Base(AsyncAttrs, DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger)
    user_name: Mapped[str] = mapped_column(String(50))

class Event(Base):
    __tablename__ = "event"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.tg_id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(50))
    description: Mapped[str] = mapped_column(String(300), nullable=True)
    start_time: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)
    repeat_type: Mapped[int] = mapped_column(SmallInteger, nullable=True)
    start_repeat: Mapped[Date] = mapped_column(Date, nullable=True)
    repeat_indicator: Mapped[int] = mapped_column(SmallInteger, nullable=True)
    repeat_duration: Mapped[int] = mapped_column(Integer, nullable=True)
    end_repeat: Mapped[Date] = mapped_column(Date, nullable=True)
    remindings: Mapped[list["Reminding"]] = relationship(back_populates="event", cascade="all, delete-orphan")


class Reminding(Base):
    __tablename__ = "remindings"
    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("event.id", ondelete="CASCADE"))
    remind_before: Mapped[int] = mapped_column(Integer)
    remind_indicator: Mapped[int] = mapped_column(SmallInteger)
    next_rem: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)
    remind_end: Mapped[bool] = mapped_column(Boolean, default=False)
    event: Mapped["Event"] = relationship(back_populates="remindings")

async def db_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)




if __name__ == "__main__":
    asyncio.run(db_main())
