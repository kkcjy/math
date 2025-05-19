import numpy as np
import pandas as pd
from scipy.stats import uniform
import matplotlib.pyplot as plt

def simulate_production_capacity(N, s, T, k, total_time, num_simulations=10000):
    """
    N -- 生产线数量
    s -- 每条生产线的工位数
    T -- 产品总平均完成时间(min)
    k -- 熟练程度系数
    total_time -- 总生产时间(min)
    num_simulations -- 仿真次数
    """
    # 每个工序的理论平均时间
    t_mean = T / s
    
    # S = (t_mean/k)^2
    # 对于 U(a,b)，S = (b-a)^2/12
    # (b-a)^2/12 = (t_mean/k)^2 => (b-a) = 2*sqrt(3)*t_mean/k
    c = np.sqrt(3) * t_mean / k     # 半宽
    low = t_mean - c
    high = t_mean + c
    
    # 工位时间
    process_times = np.random.uniform(low, high, size=(num_simulations, N, s))
    
    # 每条生产线的节拍(最慢工位时间)
    cycle_times = np.max(process_times, axis=2) 
    
    # 每条生产线的产能
    line_capacities = total_time / cycle_times 
    
    # 总产能
    total_capacities = np.sum(line_capacities, axis=1) 
    
    return {
        'mean': np.mean(total_capacities),
        'std': np.std(total_capacities),
        'min': np.min(total_capacities),
        'max': np.max(total_capacities),
        'median': np.median(total_capacities),
        '5th_percentile': np.percentile(total_capacities, 5),
        '95th_percentile': np.percentile(total_capacities, 95),
        'distribution_params': {'low': low, 'high': high, 'mean': t_mean}
    }

def plot_results(df):
    plt.figure(figsize=(15, 8))
    
    for i, struct in enumerate(df['结构类型'].unique(), 1):
        plt.subplot(1, 3, i)
        subset = df[df['结构类型'] == struct]
        
        for T in subset['T(min)'].unique():
            data = subset[subset['T(min)'] == T]
            plt.bar(f'T={T}', data['平均产能(件/天)'], 
                   yerr=data['产能标准差'],
                   label=f'T={T}min',
                   alpha=0.7)
        
        plt.title(f'{struct} Capacity Analysis')
        plt.ylabel('Mean Capacity (units/day)')
        plt.xlabel('Product Type (T value)')
        plt.legend()
        plt.grid(True, linestyle='--', alpha=0.6)
    
    plt.tight_layout()
    plt.savefig('production_capacity_analysis.png')
    plt.show()


if __name__ == '__main__':
    # 此处我们固定随机种子以供评委老师复现
    np.random.seed(42)
    
    num_simulations = 10000         # 仿真次数
    total_time = 24 * 60            # 总时间(min)
    k = 8                           # 熟练程度系数
    
    # 生产结构 (N: 生产线数量, s: 每条生产线的工序数)
    structures = {
        "Unit CELL": {'N': 6, 's': 1},   
        "Hybrid CELL": {'N': 2, 's': 3}, 
        "Line CELL": {'N': 1, 's': 6}    
    }

    # 不同产品的总平均完成时间(min)
    Ts = [10, 5, 1] 
    
    results = []
    
    for struct_name, params in structures.items():
        for T in Ts:
            N, s = params['N'], params['s']
            stats = simulate_production_capacity(N, s, T, k, total_time, num_simulations)
            
            results.append({
                '结构类型': struct_name,
                'T(min)': T,
                '生产线数量(N)': N,
                '工序数(s)': s,
                '平均产能(件/天)': stats['mean'],
                '产能标准差': stats['std'],
                '最小产能': stats['min'],
                '最大产能': stats['max'],
                '中位数产能': stats['median'],
                '5%分位数': stats['5th_percentile'],
                '95%分位数': stats['95th_percentile']
            })
    
    df_results = pd.DataFrame(results)
    
    print("产能仿真结果汇总:")
    print(f"结构类型\u3000\u3000\u3000\u3000 T(min)\u3000\u3000 平均产能(件/天)\u3000\u3000 产能标准差\u3000\u3000")
    print(f"－－－－－－－－－－－－－－－－－－－－－－－－－－－－－")
    for _, row in df_results.iterrows():
        print(f"{row['结构类型']:<15} {row['T(min)']:>8d} {row['平均产能(件/天)']:>16.2f} {row['产能标准差']:>16.4f}")
    
    plot_results(df_results)