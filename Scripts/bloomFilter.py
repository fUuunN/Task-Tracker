import hashlib

def calculateAndAppendVectorInt(value:int, bit_vector, space):
    sha1_pika_mod = value % space
    sha256_pika_mod = (value * 2) % space  # Örnek olarak, integer değerin iki katı ile çalışabiliriz.

    appendVector(sha1_pika_mod, sha256_pika_mod, bit_vector)

    return sha1_pika_mod, sha256_pika_mod

def calculateVectorInt(value:int,space):
    sha1_pika_mod = value % space
    sha256_pika_mod = (value * 2) % space  # Örnek olarak, integer değerin iki katı ile çalışabiliriz.

    return sha1_pika_mod, sha256_pika_mod

def calculateAndAppendVector(dizi,bit_vector,space):
    sha1_pika = hashlib.sha1(dizi.encode()).hexdigest()
    sha256_pika = hashlib.sha256(dizi.encode()).hexdigest()
    
    sha1_pika_mod = int(sha1_pika, 16) % space
    sha256_pika_mod = int(sha256_pika, 16) % space

    appendVector(sha1_pika_mod,sha256_pika_mod,bit_vector)

    return sha1_pika_mod, sha256_pika_mod

def calculateVector(dizi,space):
    sha1_pika = hashlib.sha1(dizi.encode()).hexdigest()
    sha256_pika = hashlib.sha256(dizi.encode()).hexdigest()
    
    sha1_pika_mod = int(sha1_pika, 16) % space
    sha256_pika_mod = int(sha256_pika, 16) % space

    return sha1_pika_mod, sha256_pika_mod

def appendVector(sha1,sha256,bit_vector):
    bit_vector[sha1] += 1
    bit_vector[sha256] += 1

def printVector(bit_vector):
    print(bit_vector)

def isAbsent (sha1,sha256,bit_vector):
    if bit_vector[sha1] == 0 and bit_vector[sha256] == 0:
        print("Bulunmuyor FONKSİYON")
    else : 
        print("Bulunuyor FONKSİYON")

def reduceVector (sha1,sha256,bit_vector):
    if bit_vector[sha1] != 0 and bit_vector[sha256] != 0:
        print(f"Bulunuyor Eski değeri {bit_vector[sha1]}")
        bit_vector[sha1] -= 1
        bit_vector[sha256] -= 1
        print(f"Bulunuyor Yeni değeri {bit_vector[sha1]}")
    else : 
        print("Bulunmuyor azaltma işlemi gerçekleştirilemez")

