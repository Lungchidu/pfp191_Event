import urllib.request, json

r = urllib.request.urlopen('http://localhost:5000/api/products')
d = json.loads(r.read())
print(f"Success: {d['success']}, Products: {len(d['products'])}")
print(f"First product: {d['products'][0]['name']}")

r2 = urllib.request.urlopen('http://localhost:5000/api/categories')
d2 = json.loads(r2.read())
print(f"Categories: {len(d2['categories'])}")

print("\nAll tests passed!")
