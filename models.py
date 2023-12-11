from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession,AsyncEngine
from sqlalchemy.orm import sessionmaker


DATABASE_URL = "postgresql+asyncpg://pradhatrivemula:password@localhost/mydatabase"

engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()



# Initialize database asynchronously
async def init_db(engine: AsyncEngine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)



# Subscription Plan model
class SubscriptionPlan(Base):
    __tablename__ = "subscription_plans"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(String)
    api_endpoint = Column(String)
    usage_limits= Column(String)

# User model
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email= Column(String)
    password= Column(String)
    role = Column(String)
    usages = relationship("Usage", back_populates="user")

    subscription_plan_id = Column(Integer, ForeignKey("subscription_plans.id"))
    subscription_plan = relationship("SubscriptionPlan")

# Permissions model
class Permission(Base):
    __tablename__ = "permissions"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    api_endpoint = Column(String)
    description = Column(String)


#  SQLAlchemy models...

class UserCreate(BaseModel):
    name: str
    email: str  # You can add validation like EmailStr from pydantic
    password: str  # Ensure this is hashed before storing in the database
    role: str


class PlanCreate(BaseModel):
    name: str
    description: str
    api_endpoint: str
    usage_limits: str


class PermissionCreate(BaseModel):
    name: str
    api_endpoint: str
    description: str

class Usage(Base):
    __tablename__ = "usages"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    api_name = Column(String, index=True)
    count = Column(Integer)

    user = relationship("User", back_populates="usages")

User.usages = relationship("Usage", order_by=Usage.id, back_populates="user")


class APILimit(Base):
    __tablename__ = "api_limits"
    id = Column(Integer, primary_key=True, index=True)
    subscription_plan_id = Column(Integer, ForeignKey("subscription_plans.id"))
    api_name = Column(String, index=True)
    limit = Column(Integer)

    subscription_plan = relationship("SubscriptionPlan", back_populates="api_limits")

SubscriptionPlan.api_limits = relationship("APILimit", order_by=APILimit.id, back_populates="subscription_plan")


