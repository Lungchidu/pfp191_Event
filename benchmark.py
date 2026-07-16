import random
import sqlite3
import time
import string
import statistics

random.seed(42)

N = 10000

CATEGORIES = ["loa", "den", "san khau", "micro", "may phat dien", "man hinh led", "ban ghe", "trang tri"]
LOCATIONS = ["Ho Chi Minh", "Ha Noi", "Da Nang", "Can Tho", "Hai Phong"]
ADJ = ["cao cap", "gia re", "chuyen nghiep", "mini", "khong day", "cong suat lon", "gap gon", "sieu sang"]

def rand_name(i):
    return f"{random.choice(CATEGORIES)} {random.choice(ADJ)} model {i}"

def rand_desc():
    return " ".join(random.choices(ADJ + CATEGORIES, k=6))

products = []
for i in range(1, N + 1):
    products.append({
        "id": i,
        "name": rand_name(i),
        "description": rand_desc(),
        "price": random.randint(50000, 5000000),
        "rating": round(random.uniform(3.0, 5.0), 1),
        "location": random.choice(LOCATIONS),
        "category_id": random.randint(1, 8),
        "is_flash": random.random() < 0.2,
        "tags": random.sample(CATEGORIES, 2),
    })

# Insert one known target near the end so worst-case linear scan is meaningful
products[-1]["name"] = "loa sieu tram dac biet X9000"

KEYWORD = "sieu tram dac biet X9000"

# ---------- Method 1: Linear scan (current search_filter.py implementation) ----------
def linear_search(products, keyword):
    result = []
    tu_khoa = keyword.strip().lower()
    for product in products:
        text = product["name"] + " " + product["description"] + " "
        for tag in product["tags"]:
            text = text + tag + " "
        text = text + product["location"]
        text = text.lower()
        if tu_khoa in text:
            result.append(product)
    return result

# ---------- Method 2: SQLite LIKE query ----------
conn = sqlite3.connect(":memory:")
conn.execute("""
CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    name TEXT, description TEXT, tags TEXT, location TEXT
)
""")
conn.executemany(
    "INSERT INTO products VALUES (?,?,?,?,?)",
    [(p["id"], p["name"], p["description"], " ".join(p["tags"]), p["location"]) for p in products]
)
conn.commit()
# index to make LIKE search realistic best-case for DB (still LIKE '%..%' can't use btree index well,
# but we test both with and without index)
def sqlite_search_noidex(keyword):
    kw = f"%{keyword.lower()}%"
    cur = conn.execute(
        "SELECT * FROM products WHERE lower(name||' '||description||' '||tags||' '||location) LIKE ?",
        (kw,)
    )
    return cur.fetchall()

# ---------- Method 3: Inverted index (precomputed dict word -> set of ids) ----------
def build_inverted_index(products):
    index = {}
    id_map = {}
    for p in products:
        id_map[p["id"]] = p
        text = (p["name"] + " " + p["description"] + " " + " ".join(p["tags"]) + " " + p["location"]).lower()
        words = set(text.replace(",", " ").split())
        for w in words:
            index.setdefault(w, set()).add(p["id"])
    return index, id_map

inv_index, id_map = build_inverted_index(products)

def indexed_search(keyword):
    # tach tu khoa thanh cac token, moi token tim trong index (substring tren index keys,
    # so luong index keys << N nen van nhanh hon nhieu so voi quet toan bo N san pham),
    # sau do giao (AND) cac tap ket qua de tim san pham chua DU tat ca token.
    tokens = keyword.strip().lower().split()
    result_ids = None
    for tok in tokens:
        matched_for_tok = set()
        for word, ids in inv_index.items():
            if tok in word:
                matched_for_tok |= ids
        result_ids = matched_for_tok if result_ids is None else (result_ids & matched_for_tok)
        if not result_ids:
            break
    return [id_map[i] for i in (result_ids or set())]

def timeit_ms(fn, repeat=7):
    times = []
    for _ in range(repeat):
        t0 = time.perf_counter()
        res = fn()
        t1 = time.perf_counter()
        times.append((t1 - t0) * 1000)
    return statistics.mean(times), statistics.stdev(times), len(res)

print(f"So luong san pham (N) = {N}")
print(f"Tu khoa tim kiem = '{KEYWORD}'")
print("-" * 70)

for label, fn in [
    ("Linear scan (list, current impl)", lambda: linear_search(products, KEYWORD)),
    ("SQLite LIKE %..% (full scan)", lambda: sqlite_search_noidex(KEYWORD)),
    ("Inverted index (precomputed dict)", lambda: indexed_search(KEYWORD)),
]:
    mean_ms, std_ms, n_result = timeit_ms(fn)
    print(f"{label:38s} | avg {mean_ms:8.3f} ms | std {std_ms:6.3f} | ket qua: {n_result}")

print("-" * 70)
print("Ghi chu: 'Inverted index' KHONG tinh thoi gian build index (build 1 lan, o duoi).")
t0 = time.perf_counter()
build_inverted_index(products)
t1 = time.perf_counter()
print(f"Thoi gian build inverted index 1 lan cho {N} san pham: {(t1-t0)*1000:.3f} ms")

print()
print("=" * 70)
print("BENCHMARK SAP XEP (SORT) THEO GIA - filter_products(sort_by='price-asc')")
print("=" * 70)

def bubble_sort_price(items):
    result = items[:]  # copy, giong logic trong search_filter.py
    n = len(result)
    for i in range(n):
        for j in range(0, n - i - 1):
            if result[j]["price"] > result[j + 1]["price"]:
                tam = result[j]
                result[j] = result[j + 1]
                result[j + 1] = tam
    return result

def builtin_sort_price(items):
    return sorted(items, key=lambda p: p["price"])

for label, fn, repeat in [
    ("Bubble sort (code hien tai, O(n^2))", lambda: bubble_sort_price(products), 3),
    ("Python sorted() - Timsort O(n log n)", lambda: builtin_sort_price(products), 20),
]:
    mean_ms, std_ms, n_result = timeit_ms(fn, repeat=repeat)
    print(f"{label:40s} | avg {mean_ms:10.3f} ms | std {std_ms:6.3f} | n={n_result}")
