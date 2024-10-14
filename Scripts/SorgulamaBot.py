import json
from fastapi import FastAPI, Request, Depends
from sqlalchemy.orm import Session
from sentence_transformers import SentenceTransformer
import joblib
import os
import warnings
from elasticsearch import Elasticsearch
import psycopg2


import redis
rd = redis.Redis(host='localhost', port=6379, decode_responses=True)
EX_TIME = 120

# TensorFlow uyarılarını bastırmak için
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=DeprecationWarning)

# FastAPI uygulamasını başlatıyoruz
app = FastAPI()

# Elasticsearch bağlantısı
es = Elasticsearch(hosts='http://elastic:DkIedPPSCb@localhost:9200/')

# Modelleri yüklüyoruz
model = joblib.load("C:/Users/LENOVO/Desktop/project/app/Model_Vector/logistic_regression_model.pkl")
vectorizer = joblib.load("C:/Users/LENOVO/Desktop/project/app/Model_Vector/tfidf_vectorizer.pkl")

# Cümle gömme modelini yüklüyoruz
embedding_model = SentenceTransformer('all-mpnet-base-v2')

# Veritabanı bağımlılığı (şimdilik bir yer tutucu)
def get_db():
    # Kendi veritabanı oturumunuzu burada tanımlayın
    db = Session()
    try:
        yield db
    finally:
        db.close()

# Alan eşlemesi (modelin çıkış etiketlerine göre ayarlayın)
field_mapping = {
    0: "taskName",
    1: "taskDescription",
    2: "kanbanName",
    3: "statusName"
}

# Görev detaylarını formatlamak için fonksiyon
def format_task_details(task_name, task_description, kanban_name, status_name, kanban_id):
    return {
        "task_name": task_name,
        "task_description": task_description,
        "kanban_name": kanban_name,
        "status_name": status_name,
        "kanban_id": kanban_id
    }

# Chatbot yanıtı için ana fonksiyon
def chatbot_response2(user_input: str, userId: int, db: Session):
    veri = []

    # Kullanıcının tüm kanban ID'lerini alıyoruz
    kanbanIDs = all_kanban_id(userId)

    test_sentence = user_input.lower()
    test_sentence_vectorized = vectorizer.transform([test_sentence])  # Girdi cümlesini vektörize ediyoruz

    # Modeli kullanarak tahmin yapıyoruz
    predictions = model.predict(test_sentence_vectorized)
    predicted_field = field_mapping[predictions[0]]  # Tek girdi için tahmin edilen alanı alıyoruz

    # Eğer tahmin edilen alan taskName veya taskDescription ise k değeri 1, diğer durumlarda 10 oluyor
    if predictions[0] == 0 or predictions[0] == 1:
        k = 1
    else:
        k = 10

    # Girdi cümlesinin vektörünü oluşturuyoruz
    vector_of_input_text = embedding_model.encode(test_sentence)

    # Elasticsearch sorgusunu oluşturuyoruz
    query = {
        "knn": {
            "field": f"{predicted_field}Vector",
            "query_vector": vector_of_input_text.tolist(),
            "k": k,
            "num_candidates": 500
        }
    }

    # Elasticsearch'te arama yapıyoruz
    res = es.search(index="task", body=query, _source=["taskId", "taskName", "taskDescription", "kanbanName", "statusName", "KanbanId"])
    
    # Sadece kullanıcının kanbanlarına ait olan sonuçları işliyoruz
    for hit in res['hits']['hits']:
        if hit['_score'] >= 0.40:
            task_name = hit['_source'].get('taskName', 'N/A')
            task_description = hit['_source'].get('taskDescription', 'N/A')
            kanban_name = hit['_source'].get('kanbanName', 'N/A')
            status_name = hit['_source'].get('statusName', 'N/A')
            kanban_id = hit['_source'].get('kanbanId', 'N/A')
            if kanban_id in kanbanIDs:
                veri.append(format_task_details(task_name, task_description, kanban_name, status_name, kanban_id))

    # Eğer sonuçlar varsa, bunları formatlayarak döndürüyoruz, aksi takdirde ilgili görev bulunamadı mesajı veriyoruz
    if veri:
        return formated_veri(veri)
    else:
        return "İlgili görev bulunamadı."

# Sonuçları formatlamak için fonksiyon
def formated_veri(veri):
    formatted_str = ""
    for item in veri:
        formatted_str += (f"\n\nGörev Adı: {item['task_name']}\n"
                          f"Açıklama: {item['task_description']}\n"
                          f"Kanban Adı: {item['kanban_name']}\n"
                          f"Durum: {item['status_name']}\n"
                          f"Kanban ID: {item['kanban_id']}\n"
                          f"{'-'*60}\n")
    return formatted_str

# Kullanıcının sahip olduğu tüm kanban ID'lerini almak için fonksiyon
def all_kanban_id(userId):
    user_key = f"user:{userId}:kanban_ids"
    
    if rd.exists(user_key):
        degerler = [int(x) for x in rd.lrange(user_key, 0, -1)]
        print(degerler)
        return degerler

    else:
        query = '''
            SELECT 
                "kanban_id"  
            FROM 
                "kanban_users"
            WHERE 
                %s = "user_id"
        '''
        
        connection = None
        
        try:
            connection = psycopg2.connect( 
                host='localhost', 
                database='LikeJira2', 
                user='postgres', 
                password='sifre0134'
            )

            cursor = connection.cursor()

            cursor.execute(query, (userId,))

            kanban_ids = [row[0] for row in cursor.fetchall()]

            if kanban_ids:
                rd.rpush(user_key, *map(str, kanban_ids))
                rd.expire(user_key, EX_TIME)
                print(f"Stored in Redis: {kanban_ids}")

            return kanban_ids

        except (Exception, psycopg2.Error) as error:
            print("Hata:", error)
            return []

        finally:
            if connection:
                cursor.close()
                connection.close()
