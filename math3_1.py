import matplotlib.pyplot as plt
import numpy as np

# Constants
total_time = 24 * 60    # 每天总工作分钟数
beat_A1 = [96, 64, 64]  # 组装、测试、包装节拍时间(分钟/件)
max_workers = 48        # 最大可用工人数


k = max_workers // (3 + 2 + 2)  # 3:2:2比例，7k ≤ 48
n1_opt = 3 * k                  # 组装工人数
n2_opt = 2 * k                  # 测试工人数
n3_opt = 2 * k                  # 包装工人数

# 产能
capacity1 = n1_opt * total_time / beat_A1[0]
capacity2 = n2_opt * total_time / beat_A1[1]
capacity3 = n3_opt * total_time / beat_A1[2]
total_capacity = min(capacity1, capacity2, capacity3)
efficiency = total_capacity / (n1_opt + n2_opt + n3_opt)

print("最优工人分配(3:2:2比例方法):")
print(f"  组装工人: {n1_opt}")
print(f"  测试工人: {n2_opt}")
print(f"  包装工人: {n3_opt}")
print(f"  总工人数: {n1_opt + n2_opt + n3_opt}")
print(f"  日产能: {total_capacity:.0f} 件")
print(f"  效率: {efficiency:.2f} 件/工人/天")


worker_range = range(1, max_workers)
allocations = []
efficiencies = []
capacities = []

for n1 in worker_range:
    for n2 in worker_range:
        n3 = max_workers - n1 - n2
        if n3 < 1:
            continue
        
        c1 = n1 * total_time / beat_A1[0]
        c2 = n2 * total_time / beat_A1[1]
        c3 = n3 * total_time / beat_A1[2]
        total_cap = min(c1, c2, c3)
        eff = total_cap / (n1 + n2 + n3)
        
        allocations.append((n1, n2, n3))
        efficiencies.append(eff)
        capacities.append((c1, c2, c3))

plt.figure(figsize=(18, 12))

plt.subplot(2, 2, 1)
n1_values = [a[0] for a in allocations]
n2_values = [a[1] for a in allocations]
sc = plt.scatter(n1_values, n2_values, c=efficiencies, cmap='viridis', alpha=0.7)
plt.colorbar(sc, label='Efficiency (units/worker/day)')
plt.plot(n1_opt, n2_opt, 'ro', markersize=10, label='Optimal (3:2:2 ratio)')
plt.xlabel('Assembly Workers (n1)')
plt.ylabel('Testing Workers (n2)')
plt.title('Worker Allocation Efficiency Map\n(Color shows efficiency)')
plt.legend()
plt.grid(True)

plt.subplot(2, 2, 2)
plt.plot([c[0] for c in capacities], label='Assembly Capacity', alpha=0.7)
plt.plot([c[1] for c in capacities], label='Testing Capacity', alpha=0.7)
plt.plot([c[2] for c in capacities], label='Packaging Capacity', alpha=0.7)
plt.axhline(y=total_capacity, color='r', linestyle='--', 
            label=f'Optimal Capacity: {total_capacity:.0f}')
plt.xlabel('Allocation Scheme Index')
plt.ylabel('Daily Capacity (units)')
plt.title('Capacity Comparison Across Stages')
plt.legend()
plt.grid(True)

plt.subplot(2, 2, 3)
stages = ['Assembly', 'Testing', 'Packaging']
workers = [n1_opt, n2_opt, n3_opt]
opt_capacities = [capacity1, capacity2, capacity3]

bars = plt.bar(stages, workers, alpha=0.6, label='Workers')
plt.xlabel('Production Stage')
plt.ylabel('Number of Workers')
plt.title('Optimal Worker Allocation (3:2:2 Ratio)')

for i, bar in enumerate(bars):
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height,
             f'{workers[i]} workers\n{opt_capacities[i]:.0f} units',
             ha='center', va='bottom')

plt.grid(True, axis='y')

plt.subplot(2, 2, 4)
plt.hist(efficiencies, bins=30, edgecolor='black', alpha=0.7)
plt.axvline(efficiency, color='r', linestyle='dashed', linewidth=2,
            label=f'Optimal: {efficiency:.2f}')
plt.xlabel('Efficiency (units/worker/day)')
plt.ylabel('Number of Allocation Schemes')
plt.title('Efficiency Distribution of All Possible Allocations')
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.show()