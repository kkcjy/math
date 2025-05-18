import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

T = 10                      # 总平均完成时间（分钟）
k = 8                       # 熟练程度系数
total_workers = 16          # 总工位数
simulation_times = 1000     # 仿真次数
total_time = 24 * 60        # 24小时（分钟）

# 生产线条数
N_options = [1, 2, 4, 8, 16]

results = {
    'N': [],
    'S': [],
    'mean_capacity': [],
    'std_capacity': [],
    'capacity_per_std': []
}

def simulate_capacity(N, S, T, k, total_time, simulations):
    capacities = []
    for _ in range(simulations):
        if S == 1:
            # 单元级CELL：每个工人独立完成产品
            worker_times = np.random.uniform(T - T/k, T + T/k, N)
            worker_capacities = np.floor(total_time / worker_times)
            total_capacity = np.sum(worker_capacities)
        else:
            # 混联型或直线型：每条生产线有S个工人串联
            line_capacities = []
            for _ in range(N):
                # 每个工序的时间
                step_times = np.random.uniform((T/S) - (T/S)/k, (T/S) + (T/S)/k, S)
                # 生产线节拍由最慢工序决定
                line_takt = np.max(step_times)
                line_capacity = np.floor(total_time / line_takt)
                line_capacities.append(line_capacity)
            total_capacity = np.sum(line_capacities)
        capacities.append(total_capacity)
    return np.mean(capacities), np.std(capacities)

for N in N_options:
    S = total_workers // N
    mean_cap, std_cap = simulate_capacity(N, S, T, k, total_time, simulation_times)
    cap_per_std = mean_cap / std_cap if std_cap > 0 else 0
    results['N'].append(N)
    results['S'].append(S)
    results['mean_capacity'].append(mean_cap)
    results['std_capacity'].append(std_cap)
    results['capacity_per_std'].append(cap_per_std)

print("仿真结果：")
for i in range(len(results['N'])):
    print(f"N={results['N'][i]}, S={results['S'][i]}: "
          f"平均产能={results['mean_capacity'][i]:.1f}, "
          f"标准差={results['std_capacity'][i]:.1f}, "
          f"单位波动产能={results['capacity_per_std'][i]:.2f}")

plt.figure(figsize=(14, 6))

plt.subplot(1, 2, 1)
plt.bar(results['N'], results['mean_capacity'], width=0.5, label='Average Capacity')
plt.errorbar(results['N'], results['mean_capacity'], yerr=results['std_capacity'], 
             fmt='o', color='red', label='Standard Deviation')
plt.xlabel('Number of Production Lines (N)')
plt.ylabel('Capacity (Products)')
plt.title('Average Capacity and Variability for Different N')
plt.legend()
plt.grid(True)

plt.subplot(1, 2, 2)
plt.plot(results['N'], results['capacity_per_std'], 'bo-', label='Capacity per Unit Variability')
plt.xlabel('Number of Production Lines (N)')
plt.ylabel('Capacity per Unit Variability (Capacity/Standard Deviation)')
plt.title('Capacity per Unit Variability for Different N')
plt.grid(True)
plt.legend()

plt.tight_layout()
plt.show()

optimal_idx = np.argmax(results['capacity_per_std'])
optimal_N = results['N'][optimal_idx]
optimal_S = results['S'][optimal_idx]
print(f"\n最优设计：N={optimal_N}, S={optimal_S}, "
      f"单位波动产能={results['capacity_per_std'][optimal_idx]:.2f}")