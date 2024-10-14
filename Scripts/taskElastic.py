from elasticsearch import Elasticsearch
import psycopg2
from sentence_transformers import SentenceTransformer

# Elasticsearch ve PostgreSQL bağlantı ayarları
ES_HOST = 'http://elastic:DkIedPPSCb@localhost:9200/'
PG_CONFIG = {
    'host': 'localhost',
    'database': 'LikeJira2',
    'user': 'postgres',
    'password': 'sifre0134'
}
INDEX_NAME = 'task'

# Elasticsearch ve model nesneleri
es = Elasticsearch(hosts=ES_HOST)
model = SentenceTransformer('all-mpnet-base-v2')

def get_pg_connection():
    """PostgreSQL bağlantısı oluşturur."""
    return psycopg2.connect(**PG_CONFIG)

def get_data():
    """PostgreSQL'den veri çeker."""
    conn = get_pg_connection()
    try:
        with conn.cursor() as cur:
            cur.execute('''
                SELECT 
                    t."taskId", 
                    t."taskName", 
                    t."taskDescription", 
                    k."kanbanName",
                    s."statusName", 
                    k."kanbanId"  
                FROM 
                    "task" t
                INNER JOIN 
                    "kanban" k ON t."kanbanId" = k."kanbanId"
                INNER JOIN 
                    "status" s ON t."statusId" = s."statusId";
            ''')
            return cur.fetchall()
    finally:
        conn.close()

def create_indexes():
    """Elasticsearch indeksini oluşturur veya günceller."""
    if es.indices.exists(index=INDEX_NAME):
        es.indices.delete(index=INDEX_NAME)
        print(f"{INDEX_NAME} indexi silindi")

    body = {
        "mappings": {
            "properties": {
                "taskId": {"type": "integer"},
                "taskName": {"type": "text"},
                "taskNameVector": {
                    "type": "dense_vector", 
                    "dims": 768, 
                    "index": True,
                    "similarity": "l2_norm" 
                },
                "taskDescription": {"type": "text"},
                "taskDescriptionVector": {
                    "type": "dense_vector", 
                    "dims": 768, 
                    "index": True,
                    "similarity": "l2_norm"  
                },
                "kanbanId": {"type": "integer"},
                "kanbanName": {"type": "text"},
                "kanbanNameVector": {
                    "type": "dense_vector", 
                    "dims": 768, 
                    "index": True,
                    "similarity": "l2_norm"  
                },
                "statusName": {"type": "text"},
                "statusNameVector": {
                    "type": "dense_vector", 
                    "dims": 768, 
                    "index": True,
                    "similarity": "l2_norm"
                },
            }
        }
    }
    es.indices.create(index=INDEX_NAME, body=body)
    print(f"{INDEX_NAME} indexi oluşturuldu")

def add_indexes(rows):
    """Veriyi Elasticsearch'e ekler."""
    for row in rows:
        task_name_vector = model.encode(row[1])
        description_vector = model.encode(row[2])
        kanban_name_vector = model.encode(row[3])
        status_name_vector = model.encode(row[4])
        doc = {
            'taskId': row[0],
            'taskName': row[1],
            'taskNameVector': task_name_vector.tolist(),
            'taskDescription': row[2],
            'taskDescriptionVector': description_vector.tolist(),
            'kanbanId': row[5],
            'kanbanName': row[3],
            'kanbanNameVector': kanban_name_vector.tolist(),
            'statusName': row[4],
            'statusNameVector': status_name_vector.tolist()
        }
        es.index(index=INDEX_NAME, id=row[0], document=doc)
    print("Veriler Elasticsearch'e eklendi")

def add_data_elastic():
    """Veriyi PostgreSQL'den alır ve Elasticsearch'e ekler."""
    rows = get_data()
    create_indexes()
    add_indexes(rows)

# Bu fonksiyonu doğrudan çağırarak veriyi işleyebilirsiniz
add_data_elastic()
