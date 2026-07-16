import random, time, statistics
random.seed(42)

CATEGORIES = ["loa", "den", "san khau", "micro", "may phat dien", "man hinh led", "ban ghe", "trang tri"]
LOCATIONS = ["Ho Chi Minh", "Ha Noi", "Da Nang", "Can Tho", "Hai Phong"]
ADJ = ["cao cap", "gia re", "chuyen nghiep", "mini", "khong day", "cong suat lon", "gap gon", "sieu sang"]

def make_products(n):
    prods = []
    for i in range(1, n + 1):
        prods.append({
            "id": i,
            "name": f"{random.choice(CATEGORIES)} {random.choice(ADJ)} model {i}",
            "description": " ".join(random.choices(ADJ + CATEGORIES, k=6)),
            "price": random.randint(50000, 5000000),
            "rating": round(random.uniform(3.0, 5.0), 1),
            "location": random.choice(LOCATIONS),
            "tags": random.sample(CATEGORIES, 2),
        })
    prods[-1]["name"] = "loa sieu tram dac biet X9000"
    return prods

def linear_search(products, keyword):
    result = []
    tu_khoa = keyword.strip().lower()
    for product in products:
        text = product["name"] + " " + product["description"] + " "
        for tag in product["tags"]:
            text += tag + " "
        text += product["location"]
        text = text.lower()
        if tu_khoa in text:
            result.append(product)
    return result

def build_inverted_index(products):
    index, id_map = {}, {}
    for p in products:
        id_map[p["id"]] = p
        text = (p["name"] + " " + p["description"] + " " + " ".join(p["tags"]) + " " + p["location"]).lower()
        for w in set(text.split()):
            index.setdefault(w, set()).add(p["id"])
    return index, id_map

def indexed_search(inv_index, id_map, keyword):
    tokens = keyword.strip().lower().split()
    result_ids = None
    for tok in tokens:
        m = set()
        for w, ids in inv_index.items():
            if tok in w:
                m |= ids
        result_ids = m if result_ids is None else result_ids & m
        if not result_ids:
            break
    return [id_map[i] for i in (result_ids or set())]

def bubble_sort_price(items):
    result = items[:]
    n = len(result)
    for i in range(n):
        for j in range(0, n - i - 1):
            if result[j]["price"] > result[j + 1]["price"]:
                result[j], result[j + 1] = result[j + 1], result[j]
    return result

def builtin_sort_price(items):
    return sorted(items, key=lambda p: p["price"])

def time_ms(fn, repeat=5):
    ts = []
    for _ in range(repeat):
        t0 = time.perf_counter(); fn(); t1 = time.perf_counter()
        ts.append((t1 - t0) * 1000)
    return statistics.mean(ts)

Ns = [100, 500, 1000, 2000, 5000, 10000]
KEYWORD = "sieu tram dac biet X9000"

rows = []
for n in Ns:
    products = make_products(n)
    lin_ms = time_ms(lambda: linear_search(products, KEYWORD), repeat=5)
    inv_index, id_map = build_inverted_index(products)
    idx_ms = time_ms(lambda: indexed_search(inv_index, id_map, KEYWORD), repeat=5)
    bubble_repeat = 5 if n <= 2000 else 1
    bub_ms = time_ms(lambda: bubble_sort_price(products), repeat=bubble_repeat)
    tim_ms_ = time_ms(lambda: builtin_sort_price(products), repeat=10)
    rows.append((n, lin_ms, idx_ms, bub_ms, tim_ms_))
    print(f"N={n:6d} | linear_search={lin_ms:9.3f}ms | indexed_search={idx_ms:8.3f}ms | bubble_sort={bub_ms:12.3f}ms | timsort={tim_ms_:7.3f}ms")

import json
with open("results.json", "w") as f:
    json.dump(rows, f)
