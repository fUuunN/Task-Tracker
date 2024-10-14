from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Table, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

# Many-to-Many ilişkiyi temsil eden bağlantı tablosu
kanban_users = Table(
    'kanban_users',
    Base.metadata,
    Column('kanban_id', Integer, ForeignKey('kanban.kanbanId'), primary_key=True),
    Column('user_id', Integer, ForeignKey('users.userId'), primary_key=True)
)

class Kanban(Base):
    __tablename__ = "kanban"

    kanbanId = Column(Integer, primary_key=True, index=True)
    kanbanName = Column(String, nullable=False)
    kanbanCreatedAt = Column(DateTime, default=datetime.now)
    kanbanUpdatedAt = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    users = relationship('User', secondary=kanban_users, back_populates='kanbans')
    tasks = relationship('Task', back_populates='kanban')

class User(Base):
    __tablename__ = "users"

    userId = Column(Integer, primary_key=True, index=True)
    userName = Column(String, nullable=False)
    userEmail = Column(String, nullable=False, unique=True)
    userPasswordHashed = Column(String, nullable=False)
    
    kanbans = relationship('Kanban', secondary=kanban_users, back_populates='users')
    tasks = relationship('Task', back_populates='assigned_user')

class Status(Base): 
    __tablename__ = "status"
    
    statusId = Column(Integer, primary_key=True, index=True)
    statusName = Column(String, nullable=False, unique=True)

class Task(Base):
    __tablename__ = "task"

    taskId = Column(Integer, primary_key=True, index=True)
    taskName = Column(String, nullable=False)
    taskDescription = Column(String, nullable=True)
    kanbanId = Column(Integer, ForeignKey('kanban.kanbanId'))
    assignedToUser = Column(Integer, ForeignKey('users.userId'))
    statusId = Column(Integer, ForeignKey('status.statusId'))
    taskCreatedAt = Column(DateTime, default=datetime.now)
    taskUpdatedAt = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    kanban = relationship('Kanban', back_populates='tasks')
    assigned_user = relationship('User', back_populates='tasks')
    status = relationship('Status')
