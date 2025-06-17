from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.models import User, Strategy
from app.schemas.strategy import Strategy as StrategySchema, StrategyCreate
from app.core.deps import get_db, get_current_active_user

router = APIRouter(prefix="/strategies", tags=["strategies"])

@router.post("/", response_model=StrategySchema)
def create_strategy(strategy: StrategyCreate, db: Session = Depends(get_db)):
    db_strategy = Strategy(name=strategy.name, description=strategy.description)
    db.add(db_strategy)
    db.commit()
    db.refresh(db_strategy)
    return db_strategy

@router.post("/{strategy_id}/subscribe")
def subscribe_strategy(strategy_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_active_user)):
    strategy = db.query(Strategy).get(strategy_id)
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    if strategy not in user.strategies:
        user.strategies.append(strategy)
        db.commit()
    return {"msg": "Subscribed"}

@router.get("/", response_model=list[StrategySchema])
def list_strategies(db: Session = Depends(get_db)):
    return db.query(Strategy).all()

@router.get("/my", response_model=list[StrategySchema])
def get_my_strategies(db: Session = Depends(get_db), user: User = Depends(get_current_active_user)):
    return user.strategies