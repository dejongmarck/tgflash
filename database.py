from datetime import datetime, timezone
from sqlalchemy import BigInteger, DateTime, Integer, String, Float, Text, select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from config import settings

engine = create_async_engine(settings.database_url, pool_pre_ping=True)
Session = async_sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase): pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)  # Telegram user ID
    language: Mapped[str] = mapped_column(String(2), default="en")
    referral_code: Mapped[str] = mapped_column(String(40), unique=True)
    referred_by: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    provider_order_id: Mapped[str] = mapped_column(String(120), unique=True)
    product_id: Mapped[str] = mapped_column(String(120))
    product_name: Mapped[str] = mapped_column(String(200))
    network: Mapped[str] = mapped_column(String(120))
    amount: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(40), default="waiting")
    payment_status: Mapped[str] = mapped_column(String(40), default="waiting")
    payment_url: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_user(user_id: int):
    async with Session() as s:
        return await s.get(User, user_id)

async def save_user(user_id: int, lang="en", referrer=None):
    async with Session() as s:
        user = await s.get(User, user_id)
        if not user:
            user = User(id=user_id, language=lang, referral_code=f"u{user_id}")
            if referrer and referrer != user_id and await s.get(User, referrer):
                user.referred_by = referrer
            s.add(user)
        await s.commit()
        return user

async def set_language(user_id: int, lang: str):
    async with Session() as s:
        user = await s.get(User, user_id)
        if user:
            user.language = lang
            await s.commit()

async def add_order(**kwargs):
    async with Session() as s:
        order = Order(**kwargs)
        s.add(order)
        await s.commit()
        return order

async def list_orders(user_id: int, limit=10):
    async with Session() as s:
        result = await s.execute(select(Order).where(Order.telegram_user_id == user_id).order_by(Order.id.desc()).limit(limit))
        return list(result.scalars())

async def pending_orders():
    async with Session() as s:
        result = await s.execute(select(Order).where(Order.status.notin_(["completed","cancelled","expired"])))
        return list(result.scalars())

async def update_order(provider_id: str, status: str, payment_status: str):
    async with Session() as s:
        result = await s.execute(select(Order).where(Order.provider_order_id == provider_id))
        order = result.scalar_one_or_none()
        if order:
            order.status, order.payment_status = status, payment_status
            await s.commit()
            return order
