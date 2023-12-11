from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models import AsyncSessionLocal, engine, init_db
from models import Base, SubscriptionPlan, User, PlanCreate
from models import Permission
from fastapi import Request

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from models import Base, SubscriptionPlan, User, engine
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from models import Base, SubscriptionPlan, User, engine, PlanCreate

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models import AsyncSessionLocal
from models import engine, init_db
from models import PermissionCreate

from fastapi.security import OAuth2PasswordBearer

from models import init_db  
from sqlalchemy.ext.asyncio import AsyncSession
from models import User, UserCreate
from passlib.context import CryptContext


import jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models import AsyncSessionLocal, engine, init_db, User, UserCreate, SubscriptionPlan, PlanCreate, PermissionCreate, Permission, Usage, APILimit
from passlib.context import CryptContext

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    await init_db(engine)

# Async Dependency to get the DB session
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@app.post("/users/")
async def create_user(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    existing_user = await db.execute(select(User).where(User.email == user_data.email))
    if existing_user.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = pwd_context.hash(user_data.password)
    new_user = User(name=user_data.name, email=user_data.email, password=hashed_password, role = user_data.role)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return {"message": "User created successfully"}

# Endpoint for user to login with password 
@app.post("/login")
async def login(email: str, password: str, db: AsyncSession = Depends(get_db)):
    user = await db.execute(select(User).where(User.email == email))
    user = user.scalar_one_or_none()
    if user and pwd_context.verify(password, user.password):
        return {"message": f"Welcome {user.name}!"}
    raise HTTPException(status_code=400, detail="Incorrect email or password")

def require_role(role: str):
    async def role_checker():
        user = User(name="john", email="1123", password="ddd", role="admin")
        if user.role != role:
            raise HTTPException(status_code=403, detail="Operation not permitted")
        return user  # Return the user if the role matches
    return role_checker


# Create Plan
@app.post("/plans/")
async def create_plan(plan: PlanCreate, db: AsyncSession = Depends(get_db), _=Depends(require_role("admin"))):
    db_plan = SubscriptionPlan(name=plan.name, description= plan.description, api_endpoint=plan.api_endpoint, usage_limits=plan.usage_limits)
    db.add(db_plan)
    await db.commit()
    await db.refresh(db_plan)
    return db_plan

# Modify Plan
@app.put("/plans/{plan_id}")
async def modify_plan(plan_id: int, plan_data: PlanCreate, db: AsyncSession = Depends(get_db),_=Depends(require_role("admin"))):
    result = await db.execute(select(SubscriptionPlan).where(SubscriptionPlan.id == plan_id))
    db_plan = result.scalar_one_or_none()
    if not db_plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    for var, value in vars(plan_data).items():
        setattr(db_plan, var, value) if value else None
    await db.commit()
    return db_plan

# Delete Plan
@app.delete("/plans/{plan_id}")
async def delete_plan(plan_id: int, db: AsyncSession = Depends(get_db), _=Depends(require_role("admin"))):
    result = await db.execute(select(SubscriptionPlan).where(SubscriptionPlan.id == plan_id))
    db_plan = result.scalar_one_or_none()
    if not db_plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    await db.delete(db_plan)
    await db.commit()
    return {"message": "Plan deleted"}

#add permissions
@app.post("/permissions")
async def add_permission(permission_data: PermissionCreate, db: AsyncSession = Depends(get_db), _=Depends(require_role("admin"))):
    existing_permission = await db.execute(select(Permission).where(Permission.api_endpoint == permission_data.api_endpoint))
    if existing_permission.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Permission with this API endpoint already exists")
    db_permission = Permission(name=permission_data.name, api_endpoint=permission_data.api_endpoint, description=permission_data.description)
    db.add(db_permission)
    await db.commit()
    await db.refresh(db_permission)
    return db_permission


# Modify Permission
@app.put("/permissions/{permission_id}")
async def modify_permission(permission_id: int, permission_data: PermissionCreate, db: AsyncSession = Depends(get_db), _=Depends(require_role("admin"))):
    result = await db.execute(select(Permission).where(Permission.id == permission_id))
    db_permission = result.scalar_one_or_none()
    if not db_permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    for var, value in vars(permission_data).items():
        setattr(db_permission, var, value) if value else None
    await db.commit()
    return db_permission

# Delete Permission
@app.delete("/permissions/{permission_id}")
async def delete_permission(permission_id: int, db: AsyncSession = Depends(get_db), _=Depends(require_role("admin"))):
    result = await db.execute(select(Permission).where(Permission.id == permission_id))
    db_permission = result.scalar_one_or_none()
    if not db_permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    await db.delete(db_permission)
    await db.commit()
    return {"message": "Permission deleted"}

# Modify Subscription
@app.post("/users/{user_id}/subscribe/{plan_id}")
async def modify_subscription(user_id: int, plan_id: int, db: AsyncSession = Depends(get_db), _=Depends(require_role("admin"))):
    # Retrieve the user and check if they exist
    db_user = await db.execute(select(User).where(User.id == user_id))
    user = db_user.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if the plan exists
    db_plan = await db.execute(select(SubscriptionPlan).where(SubscriptionPlan.id == plan_id))
    plan = db_plan.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    # Modify the user's subscription plan
    user.subscription_plan_id = plan_id
    await db.commit()
    return {"message": f"Subscription for user {user_id} updated to plan {plan_id}"}


# Increase the Usage count whenever an endpoint is accessed
@app.post("/usage/{user_id}/{api_name}")
async def track_usage(user_id: int, api_name: str, db: AsyncSession = Depends(get_db)):
    db_user = await get_user_or_404(user_id, db)
    result = await db.execute(select(Usage).where(Usage.user_id == user_id, Usage.api_name == api_name))
    db_usage = result.scalar_one_or_none()
    if db_usage:
        db_usage.count += 1
    else:
        db_usage = Usage(user_id=user_id, api_name=api_name, count=1)
        db.add(db_usage)
    await db.commit()
    return {"message": "Usage recorded"}


#track usage
@app.post("/track-usage/{user_id}/{api_name}")
async def track_api_usage(user_id: int, api_name: str, db: AsyncSession = Depends(get_db)):
    # Retrieve the user and their current plan
    user = await db.execute(select(User).where(User.id == user_id))
    user = user.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check the API limit for the user's subscription plan
    api_limit = await db.execute(select(APILimit).where(APILimit.subscription_plan_id == user.subscription_plan_id, APILimit.api_name == api_name))
    api_limit = api_limit.scalar_one_or_none()
    
    if api_limit:
        # Check current usage
        current_usage = await db.execute(select(Usage).where(Usage.user_id == user_id, Usage.api_name == api_name))
        current_usage = current_usage.scalar_one_or_none()

        if current_usage:
            # Increment usage count
            current_usage.count += 1
            if current_usage.count > api_limit.limit:
                raise HTTPException(status_code=429, detail="API usage limit exceeded")
        else:
            # Log first usage
            new_usage = Usage(user_id=user_id, api_name=api_name, count=1)
            db.add(new_usage)

        await db.commit()
        return {"message": "Usage tracked successfully"}
    else:
        raise HTTPException(status_code=403, detail="API access not permitted or not found in the plan")



#show usage
@app.get("/users/{user_id}/usageDisplay")
async def get_user_usage(user_id: int, db: AsyncSession = Depends(get_db)):
    user_usage = await db.execute(select(Usage).where(Usage.user_id == user_id))
    usage_list = user_usage.scalars().all()
    if not usage_list:
        raise HTTPException(status_code=404, detail="No usage data found for user")
    return {"user_id": user_id, "usage": [{"api_name": u.api_name, "count": u.count} for u in usage_list]}


# Read Subscription
@app.get("/users/subscription/{user_id}")
async def read_subscription(user_id: int, db: AsyncSession = Depends(get_db)):
    user_plan = await db.execute(select(User).where(User.id == user_id))
    user_plan = user_plan.scalar_one_or_none()
    if not user_plan:
        raise HTTPException(status_code=404, detail="user not found")
    
    return user_plan
  
# Check Access
@app.get("/access/{user_id}/{api_name}")
async def check_access(user_id: int, api_name: str, db: AsyncSession = Depends(get_db)):
    user_plan = await db.execute(select(User).where(User.id == user_id))
    user_plan = user_plan.scalar_one_or_none()
    if not user_plan:
        raise HTTPException(status_code=404, detail="Subscription plan not found")
    subscription = await db.execute(select(SubscriptionPlan).where(SubscriptionPlan.id == user_plan.subscription_plan_id))
    subscription = subscription.scalar_one_or_none()
    if not subscription:
        raise HTTPException(status_code=403, detail="No subscription plan")
    if subscription.api_endpoint!= api_name:
        raise HTTPException(status_code=403, detail="access denied")
    return {"message": "Access granted"}

# Helper Functions
async def get_user_or_404(user_id: int, db: AsyncSession) -> User:
    result = await db.execute(select(User).where(User.id == user_id))
    db_user = result.scalar_one_or_none()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

async def get_plan_or_404(plan_id: int, db: AsyncSession) -> SubscriptionPlan:
    result = await db.execute(select(SubscriptionPlan).where(SubscriptionPlan.id == plan_id))
    db_plan = result.scalar_one_or_none()
    if not db_plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return db_plan

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


