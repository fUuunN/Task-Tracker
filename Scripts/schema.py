from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

# Task Modelleri
class TaskBase(BaseModel):
    taskId: int
    taskName: Optional[str] = None
    taskDescription: Optional[str] = None
    kanbanId: int
    assignedToUser: Optional[int] = None
    statusId: int
    taskCreatedAt: datetime
    taskUpdatedAt: datetime

# Kanban Modelleri
class KanbanBase(BaseModel):
    kanbanId: int
    kanbanName: str
    kanbanCreatedAt: datetime
    kanbanUpdatedAt: datetime

class KanbanCreate(BaseModel):
    kanbanName: str

class KanbanUpdate(BaseModel):
    kanbanName: Optional[str] = None
    kanbanUpdatedAt: Optional[datetime] = None

class KanbanGet(BaseModel):
    kanbanId: int
    kanbanName: str
    kanbanCreatedAt: datetime
    kanbanUpdatedAt: datetime
    tasks: List[TaskBase]  # Task yerine TaskBase kullanıyoruz

# User Modelleri
class UserBase(BaseModel):
    userId: int
    userName: str
    userEmail: str
    userPasswordHashed: str

class UserCreate(BaseModel):
    userName: str
    userEmail: str
    userPasswordHashed: str

class UserGet(BaseModel):
    userId: int
    userName: str  
    userEmail: str

class UserUpdate(BaseModel):
    userName: Optional[str] = None
    userEmail: Optional[str] = None
    userPasswordHashed: Optional[str] = None

# Status Modelleri
class StatusBase(BaseModel):
    statusId: int
    statusName: str

class StatusCreate(BaseModel):
    statusName: str

# Task Modelleri
class TaskCreate(BaseModel):
    taskName: str
    taskDescription: str
    kanbanId: int
    assignedToUser: Optional[int] = None
    statusId: int
    taskCreatedAt: datetime
    taskUpdatedAt: datetime

class TaskUpdate(BaseModel):
    taskName: Optional[str] = None
    taskDescription: Optional[str] = None
    assignedToUser: Optional[int] = None
    statusId: Optional[int] = None
    taskUpdatedAt: Optional[datetime] = None

class UserLogin(BaseModel):
    userEmail: str
    userPasswordHashed: str