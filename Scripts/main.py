from fastapi import Depends, FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List
from models import Base, Kanban, User, Task, Status
from schema import KanbanCreate, KanbanUpdate, KanbanGet, UserCreate, UserUpdate, UserGet, TaskCreate, TaskUpdate, StatusCreate, TaskBase, StatusBase, UserLogin
from database import engine, SessionLocal
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from SorgulamaBot import chatbot_response2
from taskElastic import add_data_elastic

app = FastAPI()

# CORS middleware ekliyoruz. Bu, farklı kaynaklardan gelen isteklere izin vermek için gerekli.
# Burada '*' ile belirtiyoruz, bu da tüm domainlere izin verileceği anlamına geliyor.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Gerekirse belirli bir domaini burada belirtebilirsiniz.
    allow_credentials=True,
    allow_methods=["*"],  # Gerekirse belirli HTTP metodlarına izin verebilirsiniz.
    allow_headers=["*"],  # Gerekirse belirli başlıklara izin verebilirsiniz.
)

# Statik dosyaları servis etmek için bir mount noktası oluşturuyoruz.
app.mount("/static", StaticFiles(directory="C:\\Users\\LENOVO\\Desktop\\project\\app\\static"), name="static")
# Jinja2 template motorunu kullanarak HTML dosyalarını render etmek için bir yol oluşturuyoruz.
templates = Jinja2Templates(directory="C:\\Users\\LENOVO\\Desktop\\project\\app\\templates")

# Veritabanı tablolarını oluşturuyoruz. Eğer tablolar zaten varsa, bu işlem bir şey yapmaz.
Base.metadata.create_all(bind=engine)

# Her istekte yeni bir veritabanı oturumu oluşturmak için bir bağımlılık tanımlıyoruz.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

dp_dependency = Depends(get_db)  # Bağımlılığı tek bir yerde saklıyoruz.

# Kanban ile ilgili API endpointleri
@app.post("/projects", response_model=KanbanGet)
def create_kanban(kanban: KanbanCreate, db: Session = dp_dependency):
    # Yeni bir Kanban oluşturuyoruz.
    db_kanban = Kanban(kanbanName=kanban.kanbanName)
    db.add(db_kanban)
    db.commit()
    db.refresh(db_kanban)  # Veritabanında saklanan Kanban'ı yeniliyoruz.
    return db_kanban

@app.get("/projects/{kanbanId}", response_model=KanbanGet)
def read_kanban(kanbanId: int, db: Session = dp_dependency):
    # Kanban'ı ID'sine göre sorguluyoruz.
    db_kanban = db.query(Kanban).filter(Kanban.kanbanId == kanbanId).first()
    if db_kanban is None:
        # Kanban bulunamazsa 404 hata döndürüyoruz.
        raise HTTPException(status_code=404, detail="Kanban not found")
    return db_kanban

@app.put("/projects/{kanbanId}", response_model=KanbanGet)
def update_kanban(kanbanId: int, kanban: KanbanUpdate, db: Session = dp_dependency):
    # Güncellenmek istenen Kanban'ı ID'sine göre buluyoruz.
    db_kanban = db.query(Kanban).filter(Kanban.kanbanId == kanbanId).first()
    if db_kanban is None:
        # Eğer Kanban yoksa 404 hata döndürüyoruz.
        raise HTTPException(status_code=404, detail="Kanban not found")
    if kanban.kanbanName is not None:
        # Eğer yeni bir isim verilmişse, bu ismi güncelliyoruz.
        db_kanban.kanbanName = kanban.kanbanName
    db.commit()
    db.refresh(db_kanban)
    return db_kanban

@app.delete("/projects/{kanbanId}")
def delete_kanban(kanbanId: int, db: Session = dp_dependency):
    # Silinmek istenen Kanban'ı ID'sine göre buluyoruz.
    db_kanban = db.query(Kanban).filter(Kanban.kanbanId == kanbanId).first()
    if db_kanban is None:
        # Eğer Kanban bulunamazsa 404 hata döndürüyoruz.
        raise HTTPException(status_code=404, detail="Kanban not found")
    db.delete(db_kanban)
    db.commit()
    return {"message": "Kanban deleted"}

# Kullanıcılar ile ilgili API endpointleri
@app.post("/users", response_model=UserGet)
def create_user(user: UserCreate, db: Session = dp_dependency):
    # Yeni bir kullanıcı oluşturuyoruz.
    db_user = User(userName=user.userName, userEmail=user.userEmail, userPasswordHashed=user.userPasswordHashed)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/users/{userId}", response_model=UserGet)
def read_user(userId: int, db: Session = dp_dependency):
    # Kullanıcıyı ID'sine göre sorguluyoruz.
    db_user = db.query(User).filter(User.userId == userId).first()
    if db_user is None:
        # Eğer kullanıcı bulunamazsa 404 hata döndürüyoruz.
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.put("/users/{userId}", response_model=UserGet)
def update_user(userId: int, user: UserUpdate, db: Session = dp_dependency):
    # Güncellenmek istenen kullanıcıyı ID'sine göre buluyoruz.
    db_user = db.query(User).filter(User.userId == userId).first()
    if db_user is None:
        # Eğer kullanıcı yoksa 404 hata döndürüyoruz.
        raise HTTPException(status_code=404, detail="User not found")
    # Kullanıcı bilgilerini güncelliyoruz.
    if user.userName is not None:
        db_user.userName = user.userName
    if user.userEmail is not None:
        db_user.userEmail = user.userEmail
    if user.userPasswordHashed is not None:
        db_user.userPasswordHashed = user.userPasswordHashed
    db.commit()
    db.refresh(db_user)
    return db_user

@app.delete("/users/{userId}")
def delete_user(userId: int, db: Session = dp_dependency):
    # Silinmek istenen kullanıcıyı ID'sine göre buluyoruz.
    db_user = db.query(User).filter(User.userId == userId).first()
    if db_user is None:
        # Eğer kullanıcı bulunamazsa 404 hata döndürüyoruz.
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(db_user)
    db.commit()
    return {"message": "User deleted"}

# Görevler ile ilgili API endpointleri
@app.post("/tasks", response_model=TaskBase)
def create_task(task: TaskCreate, db: Session = dp_dependency):
    # Yeni bir görev oluşturuyoruz.
    db_task = Task(
        taskName=task.taskName,
        taskDescription=task.taskDescription,
        kanbanId=task.kanbanId,
        assignedToUser=task.assignedToUser,
        statusId=task.statusId,
        taskCreatedAt=task.taskCreatedAt,
        taskUpdatedAt=task.taskUpdatedAt
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@app.get("/tasks/{kanbanId}")
def get_all_tasks(kanbanId: int, db: Session = dp_dependency):
    # Belirli bir Kanban'a ait tüm görevleri sorguluyoruz.
    tasks = db.query(Task).filter(Task.kanbanId == kanbanId).all()
    return tasks

@app.get("/tasks/{taskId}", response_model=TaskBase)
def read_task(taskId: int, db: Session = dp_dependency):
    # Görevi ID'sine göre sorguluyoruz.
    db_task = db.query(Task).filter(Task.taskId == taskId).first()
    if db_task is None:
        # Eğer görev bulunamazsa 404 hata döndürüyoruz.
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task

@app.put("/tasks/{taskId}", response_model=TaskBase)
def update_task(taskId: int, task: TaskUpdate, db: Session = dp_dependency):
    # Güncellenmek istenen görevi ID'sine göre buluyoruz.
    db_task = db.query(Task).filter(Task.taskId == taskId).first()
    if db_task is None:
        # Eğer görev yoksa 404 hata döndürüyoruz.
        raise HTTPException(status_code=404, detail="Task not found")
    # Görev bilgilerini güncelliyoruz.
    for key, value in task.dict(exclude_unset=True).items():
        setattr(db_task, key, value)
    db.commit()
    db.refresh(db_task)
    return db_task

@app.delete("/tasks/{taskId}")
def delete_task(taskId: int, db: Session = dp_dependency):
    # Silinmek istenen görevi ID'sine göre buluyoruz.
    db_task = db.query(Task).filter(Task.taskId == taskId).first()
    if db_task is None:
        # Eğer görev bulunamazsa 404 hata döndürüyoruz.
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(db_task)
    db.commit()
    return {"message": "Task deleted"}

# Kullanıcı girişi için endpoint
@app.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    # Kullanıcının email'ine göre sorgulama yapıyoruz.
    db_user = db.query(User).filter(User.userEmail == user.userEmail).first()
    if not db_user or db_user.userPasswordHashed != user.userPasswordHashed:
        # Eğer kullanıcı yoksa veya şifre hatalıysa 401 hata döndürüyoruz.
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return {"userId": db_user.userId}

# Kullanıcıya ait projeleri sorgulamak için endpoint
@app.get("/users/{userId}/project", response_model=List[KanbanGet])
def read_kanbans(userId: int, db: Session = Depends(get_db)):
    # Kullanıcıyı ID'sine göre sorguluyoruz.
    db_user = db.query(User).filter(User.userId == userId).first()
    if db_user is None:
        # Eğer kullanıcı bulunamazsa 404 hata döndürüyoruz.
        raise HTTPException(status_code=404, detail="User not found")
    kanbans = db_user.kanbans  # Kullanıcının tüm projelerini getiriyoruz.
    return kanbans

# Belirli bir kullanıcıya yeni proje (Kanban) eklemek için endpoint
@app.post("/users/{userId}/project", response_model=KanbanGet)
def create_kanban(userId: int, kanban: KanbanCreate, db: Session = Depends(get_db)):
    # Kullanıcıyı ID'sine göre sorguluyoruz.
    db_user = db.query(User).filter(User.userId == userId).first()
    if db_user is None:
        # Eğer kullanıcı bulunamazsa 404 hata döndürüyoruz.
        raise HTTPException(status_code=404, detail="User not found")
    
    new_kanban = Kanban(kanbanName=kanban.kanbanName)  # Yeni Kanban oluşturuyoruz.
    db.add(new_kanban)
    db.commit()
    db.refresh(new_kanban)
    
    # Yeni kanbanı kullanıcının projelerine ekliyoruz.
    db_user.kanbans.append(new_kanban)
    db.commit()
    
    return new_kanban

# Kullanıcının belirli bir projesini silmek için endpoint
@app.delete("/users/{userId}/project/{kanbanId}", response_model=KanbanGet)
def delete_kanban(userId: int, kanbanId: int, db: Session = Depends(get_db)):
    # Kullanıcıyı ID'sine göre sorguluyoruz.
    db_user = db.query(User).filter(User.userId == userId).first()
    if db_user is None:
        # Eğer kullanıcı bulunamazsa 404 hata döndürüyoruz.
        raise HTTPException(status_code=404, detail="User not found")
    
    kanban = db.query(Kanban).filter(Kanban.kanbanId == kanbanId, Kanban.users.any(userId=userId)).first()
    if kanban is None:
        # Eğer Kanban bulunamazsa 404 hata döndürüyoruz.
        raise HTTPException(status_code=404, detail="Kanban not found")

    db.delete(kanban)
    db.commit()
    return kanban

# Kullanıcının belirli bir projesinin detaylarını almak için endpoint
@app.get("/users/{userId}/project/kanban/{kanbanId}", response_model=KanbanGet)
def read_kanban_details(userId: int, kanbanId: int, db: Session = Depends(get_db)):
    # Kullanıcıyı ID'sine göre sorguluyoruz.
    db_user = db.query(User).filter(User.userId == userId).first()
    if db_user is None:
        # Eğer kullanıcı bulunamazsa 404 hata döndürüyoruz.
        raise HTTPException(status_code=404, detail="User not found")

    kanban = db.query(Kanban).filter(Kanban.kanbanId == kanbanId, Kanban.users.any(userId=userId)).first()
    if kanban is None:
        # Eğer Kanban bulunamazsa 404 hata döndürüyoruz.
        raise HTTPException(status_code=404, detail="Kanban not found")

    tasks = db.query(Task).filter(Task.kanbanId == kanbanId).all()  # Kanban'a ait tüm görevleri alıyoruz.

    if tasks is None:
        tasks = []  # Eğer görevler boşsa, boş bir liste döndürüyoruz.

    # Görevleri TaskBase modeline dönüştürüyoruz.
    tasks_list = [TaskBase(
        taskId=task.taskId,
        taskName=task.taskName,
        taskDescription=task.taskDescription,
        kanbanId=task.kanbanId,
        assignedToUser=task.assignedToUser,
        statusId=task.statusId,
        taskCreatedAt=task.taskCreatedAt,
        taskUpdatedAt=task.taskUpdatedAt
    ) for task in tasks]

    return KanbanGet(
        kanbanId=kanban.kanbanId,
        kanbanName=kanban.kanbanName,
        kanbanCreatedAt=kanban.kanbanCreatedAt,
        kanbanUpdatedAt=kanban.kanbanUpdatedAt,
        tasks=tasks_list  # Görevleri Kanban modeline ekliyoruz.
    )

# Kullanıcının belirli bir projesini güncellemek için endpoint
@app.put("/users/{userId}/project/kanban/{kanbanId}", response_model=KanbanGet)
def update_kanban_details(userId: int, kanbanId: int, taskId: int, db: Session = Depends(get_db)):
    # Kullanıcıyı ID'sine göre sorguluyoruz.
    db_user = db.query(User).filter(User.userId == userId).first()
    if db_user is None:
        # Eğer kullanıcı bulunamazsa 404 hata döndürüyoruz.
        raise HTTPException(status_code=404, detail="User not found")

    kanban = db.query(Kanban).filter(Kanban.kanbanId == kanbanId, Kanban.users.any(userId=userId)).first()
    if kanban is None:
        # Eğer Kanban bulunamazsa 404 hata döndürüyoruz.
        raise HTTPException(status_code=404, detail="Kanban not found")

    # Burada Kanban'ın güncellenmesi işlemi yapılacak. Ancak bu kısım eksik kalmış, detaylar eklenmeli.

# Chatbot ile iletişim kurmak için endpoint
@app.get("/chatbot")
async def chat_with_bot_get(user_input: str, userId: int, db: Session = Depends(get_db)):
    # Chatbot'a kullanıcı girişi ve veritabanı oturumu ile cevap alıyoruz.
    response = chatbot_response2(user_input, userId, db)
    return {"message": response}  # Yanıtı her zaman bir JSON nesnesi olarak döndürüyoruz.

@app.post("/run-script")
def run_script(background_tasks: BackgroundTasks):
    background_tasks.add_task(add_data_elastic)
    return {"message": "Script arka planda çalışıyor"}