from pydantic import BaseModel

class StrategyBase(BaseModel):
    name: str
    description: str

class StrategyCreate(StrategyBase):
    pass

class Strategy(StrategyBase):
    id: int
    class Config:
        orm_mode = True