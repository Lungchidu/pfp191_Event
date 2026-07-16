import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

with open("results.json") as f:
    rows = json.load(f)

Ns = [r[0] for r in rows]
lin = [r[1] for r in rows]
idx = [r[2] for r in rows]
bub = [r[3] for r in rows]
tim = [r[4] for r in rows]

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

ax1 = axes[0]
ax1.plot(Ns, lin, marker='o', label='Linear scan (hiện tại)')
ax1.plot(Ns, idx, marker='s', label='Inverted index')
ax1.set_xlabel('Số lượng sản phẩm (N)')
ax1.set_ylabel('Thời gian (ms)')
ax1.set_title('Thời gian TÌM KIẾM theo N')
ax1.legend()
ax1.grid(alpha=0.3)

ax2 = axes[1]
ax2.plot(Ns, bub, marker='o', color='crimson', label='Bubble sort (hiện tại)')
ax2.plot(Ns, tim, marker='s', color='green', label='Python sorted() - Timsort')
ax2.set_xlabel('Số lượng sản phẩm (N)')
ax2.set_ylabel('Thời gian (ms) - thang log')
ax2.set_yscale('log')
ax2.set_title('Thời gian SẮP XẾP theo N (thang log)')
ax2.legend()
ax2.grid(alpha=0.3)

plt.tight_layout()
plt.savefig('benchmark_chart.png', dpi=150)
print("saved")
