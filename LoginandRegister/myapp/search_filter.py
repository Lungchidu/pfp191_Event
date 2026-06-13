# search_filter.py
# Chi co 2 ham: search va filter_products
# Kieu: def, if/else, for, list, continue (giong mau bai tap)

products = [
    {
        "id": 1,
        "name": "Loa line array 12 inch",
        "description": "He thong loa cong suat cao, phu hop san khau",
        "price": 850000,
        "rating": 4.8,
        "location": "Ho Chi Minh",
        "category_id": 1,
        "is_flash": True,
        "tags": ["loa", "am thanh", "line array"],
    },
    {
        "id": 2,
        "name": "Den moving head beam 380",
        "description": "Den beam 380W, 16 mau",
        "price": 420000,
        "rating": 4.7,
        "location": "Ha Noi",
        "category_id": 2,
        "is_flash": True,
        "tags": ["den", "beam", "anh sang"],
    },
    {
        "id": 3,
        "name": "San khau 6x4m gap",
        "description": "San khau nhom gap gon, de lap dat",
        "price": 1200000,
        "rating": 4.6,
        "location": "Ho Chi Minh",
        "category_id": 3,
        "is_flash": False,
        "tags": ["san khau", "nhom"],
    },
    {
        "id": 4,
        "name": "Micro khong day Shure",
        "description": "Micro UHF cao cap",
        "price": 250000,
        "rating": 4.9,
        "location": "Da Nang",
        "category_id": 8,
        "is_flash": False,
        "tags": ["micro", "shure"],
    },
    {
        "id": 5,
        "name": "May phat dien 10KVA",
        "description": "May phat dien chay em",
        "price": 1500000,
        "rating": 4.5,
        "location": "Ho Chi Minh",
        "category_id": 9,
        "is_flash": True,
        "tags": ["may phat dien", "generator"],
    },
]


def search(products, keyword=None):
    """Tim san pham theo tu khoa (ten, mo ta, tags, dia diem)."""
    result = []

    if keyword is None or keyword.strip() == "":
        for product in products:
            result.append(product)
        return result

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


def filter_products(
    products,
    keyword=None,
    max_price=None,
    location=None,
    category_id=None,
    min_rating=None,
    flash_only=None,
    sort_by=None,
):
    """Loc san pham theo nhieu tieu chi."""
    result = []

    for product in products:

        if keyword is not None:
            if keyword.strip() != "":
                tu_khoa = keyword.strip().lower()
                text = product["name"] + " " + product["description"] + " "
                for tag in product["tags"]:
                    text = text + tag + " "
                text = text + product["location"]
                text = text.lower()
                if tu_khoa not in text:
                    continue

        if max_price is not None:
            if max_price != "":
                if product["price"] > int(max_price):
                    continue

        if location is not None:
            if location != "":
                if product["location"] != location:
                    continue

        if category_id is not None:
            if category_id != "":
                if "category_id" in product:
                    id_danh_muc = product["category_id"]
                else:
                    id_danh_muc = product["categoryId"]
                if id_danh_muc != int(category_id):
                    continue

        if min_rating is not None:
            if float(min_rating) > 0:
                if product["rating"] < float(min_rating):
                    continue

        if flash_only is not None:
            if flash_only == True or flash_only == "1" or flash_only == 1:
                la_flash = False
                if "is_flash" in product:
                    if product["is_flash"] == True:
                        la_flash = True
                else:
                    if product["isFlash"] == True:
                        la_flash = True
                if la_flash == False:
                    continue

        result.append(product)

    if sort_by == "price-asc":
        n = len(result)
        for i in range(n):
            for j in range(0, n - i - 1):
                if result[j]["price"] > result[j + 1]["price"]:
                    tam = result[j]
                    result[j] = result[j + 1]
                    result[j + 1] = tam

    elif sort_by == "price-desc":
        n = len(result)
        for i in range(n):
            for j in range(0, n - i - 1):
                if result[j]["price"] < result[j + 1]["price"]:
                    tam = result[j]
                    result[j] = result[j + 1]
                    result[j + 1] = tam

    elif sort_by == "rating":
        n = len(result)
        for i in range(n):
            for j in range(0, n - i - 1):
                if result[j]["rating"] < result[j + 1]["rating"]:
                    tam = result[j]
                    result[j] = result[j + 1]
                    result[j + 1] = tam

    return result


if __name__ == "__main__":
    print("SEARCH loa:", len(search(products, "loa")))
    print("FILTER HCM:", len(filter_products(products, location="Ho Chi Minh")))
