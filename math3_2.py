import itertools
from typing import Tuple, Dict
import matplotlib.pyplot as plt
import numpy as np

# 单元级CELL详细计算过程
def cell_unit_optimization(max_workers: int = 48) -> Tuple[float, Dict]:
    workload = {
        'A1': {'assembly': 100*96, 'test': 100*64, 'packaging': 100*64},
        'A2': {'assembly': 500*32, 'test': 500*21, 'packaging': 500*24}
    }
    min_total_time = float('inf')
    best_config = {}
    
    print("\n=== 单元级CELL计算过程 ===")
    for a1 in range(1, max_workers-4):
        for a2 in range(1, max_workers-a1-3):
            # 组装阶段计算
            t_a1_assembly = workload['A1']['assembly'] / a1
            t_a2_assembly = workload['A2']['assembly'] / a2
            t_assembly = max(t_a1_assembly, t_a2_assembly)
            
            for b1 in range(1, max_workers-a1-a2-2):
                for b2 in range(1, max_workers-a1-a2-b1-1):
                    # 测试阶段计算
                    t_a1_test = workload['A1']['test'] / b1
                    t_a2_test = workload['A2']['test'] / b2
                    t_test = max(t_a1_test, t_a2_test)
                    
                    for c1 in range(1, max_workers-a1-a2-b1-b2):
                        c2 = max_workers - a1 - a2 - b1 - b2 - c1
                        if c2 < 1: continue
                        
                        # 包装阶段计算
                        t_a1_pack = workload['A1']['packaging'] / c1
                        t_a2_pack = workload['A2']['packaging'] / c2
                        t_packaging = max(t_a1_pack, t_a2_pack)
                        
                        total_time = max(t_assembly, t_test, t_packaging)
                        
                        if total_time < min_total_time:
                            min_total_time = total_time
                            best_config = {
                                'assembly': {'A1':a1, 'A2':a2, 
                                             'time_A1':t_a1_assembly, 'time_A2':t_a2_assembly},
                                'test': {'A1':b1, 'A2':b2, 
                                         'time_A1':t_a1_test, 'time_A2':t_a2_test},
                                'packaging': {'A1':c1, 'A2':c2, 
                                              'time_A1':t_a1_pack, 'time_A2':t_a2_pack},
                                'total_time': total_time
                            }
                            print(f"发现更优解: 总时间={total_time:.2f}分钟")
                            print(f"  组装: A1={a1}人({t_a1_assembly:.2f}min), A2={a2}人({t_a2_assembly:.2f}min)")
                            print(f"  测试: A1={b1}人({t_a1_test:.2f}min), A2={b2}人({t_a2_test:.2f}min)")
                            print(f"  包装: A1={c1}人({t_a1_pack:.2f}min), A2={c2}人({t_a2_pack:.2f}min)")
                            print(f"  总工人数={a1+a2+b1+b2+c1+c2}")
    
    return min_total_time, best_config

# 直线型CELL详细计算过程
def cell_series_optimization(max_workers: int = 48) -> Tuple[float, Dict]:
    total_workload = {
        'assembly': 100*96+500*32,
        'test': 100*64+500*21,
        'packaging': 100*64+500*24
    }
    min_total_time = float('inf')
    best_config = {}
    
    print("\n=== 直线型CELL计算过程 ===")
    for a in range(1, max_workers-1):
        for b in range(1, max_workers-a):
            c = max_workers - a - b
            if c < 1: continue
            
            t_assembly = total_workload['assembly'] / a
            t_test = total_workload['test'] / b
            t_packaging = total_workload['packaging'] / c
            total_time = max(t_assembly, t_test, t_packaging)
            
            if total_time < min_total_time:
                min_total_time = total_time
                best_config = {
                    'assembly': a, 'test': b, 'packaging': c,
                    'times': (t_assembly, t_test, t_packaging),
                    'total_time': total_time
                }
                print(f"发现更优解: 总时间={total_time:.2f}分钟")
                print(f"  组装={a}人({t_assembly:.2f}min), 测试={b}人({t_test:.2f}min), 包装={c}人({t_packaging:.2f}min)")
                print(f"  总工人数={a+b+c}")
    
    return min_total_time, best_config

# 混联型CELL详细计算过程
def cell_parallel_optimization(max_workers: int = 48, min_processes: int = 2) -> Tuple[float, Dict]:
    total_workload = {
        'assembly': 100*96+500*32,
        'test': 100*64+500*21,
        'packaging': 100*64+500*24
    }
    min_total_time = float('inf')
    best_config = {}
    
    print("\n=== 混联型CELL计算过程 ===")
    for a in range(1, max_workers-1):
        a_combinations = [(n, a//n) for n in range(1, a+1) if a%n==0 and (a//n)>=min_processes]
        if not a_combinations: continue
        
        for n_a, s_a in a_combinations:
            for b in range(1, max_workers-a):
                b_combinations = [(n, b//n) for n in range(1, b+1) if b%n==0 and (b//n)>=min_processes]
                if not b_combinations: continue
                
                for n_b, s_b in b_combinations:
                    c = max_workers - a - b
                    if c < min_processes: continue  
                    
                    c_combinations = [(n, c//n) for n in range(1, c+1) if c%n==0 and (c//n)>=min_processes]
                    if not c_combinations: continue
                    
                    for n_c, s_c in c_combinations:
                        t_assembly = total_workload['assembly'] / (n_a * s_a)
                        t_test = total_workload['test'] / (n_b * s_b)
                        t_packaging = total_workload['packaging'] / (n_c * s_c)
                        total_time = max(t_assembly, t_test, t_packaging)
                        
                        if total_time < min_total_time:
                            min_total_time = total_time
                            best_config = {
                                'assembly': (n_a, s_a), 'test': (n_b, s_b), 'packaging': (n_c, s_c),
                                'times': (t_assembly, t_test, t_packaging),
                                'total_time': total_time
                            }
                            print(f"发现更优解: 总时间={total_time:.2f}分钟")
                            print(f"  组装: {n_a}条线×{s_a}工序({a}人) → {t_assembly:.2f}min")
                            print(f"  测试: {n_b}条线×{s_b}工序({b}人) → {t_test:.2f}min")
                            print(f"  包装: {n_c}条线×{s_c}工序({c}人) → {t_packaging:.2f}min")
                            print(f"  总工人数={a+b+c}")
    
    return min_total_time, best_config

def print_detailed_result(structure: str, data: Dict):
    print(f"\n=== {structure} 详细结果 ===")
    
    stage_names = {"assembly": "组装", "test": "测试", "packaging": "包装"}
    stage_keys = {v: k for k, v in stage_names.items()}  
    
    if structure != '单元级CELL':
        bottleneck = ['组装', '测试', '包装'][data['times'].index(max(data['times']))]
        print(f"总时间: {data['total_time']:.2f}分钟（瓶颈阶段: {bottleneck}）")
    else:
        print(f"总时间: {data['total_time']:.2f}分钟")
    
    if structure == '单元级CELL':
        print("阶段           A1人数/时间         A2人数/时间            阶段总时间")
        print("──────────────────────────────────────────────────────────────────────")
        for stage_key, stage_name in stage_names.items():
            s = data[stage_key]
            a1_info = f"{s['A1']}人/{s['time_A1']:.2f}分钟"
            a2_info = f"{s['A2']}人/{s['time_A2']:.2f}分钟"
            total_time = f"{max(s['time_A1'], s['time_A2']):.2f}分钟"
            print(f"{stage_name:<8} {a1_info:>16} {a2_info:>16} {total_time:>16}")
    else:
        print("阶段       工人数    工序配置        阶段耗时")
        print("─────────────────────────────────────────────────")
        for stage in ['组装', '测试', '包装']:
            if structure == '直线型CELL':
                workers = data[stage_keys[stage]]
                process = "整体拆分"
                time = data['times'][['组装', '测试', '包装'].index(stage)]
            else:
                n, s = data[stage_keys[stage]]
                workers = n * s
                process = f"{n}条×{s}序"
                time = data['times'][['组装', '测试', '包装'].index(stage)]
            
            print(f"{stage:<8} {workers:>3}人    {process:<12} {time:>8.2f}分钟")

def visualize_results(unit_data, series_data, parallel_data):
    fig, axs = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle("Visual Comparison of Production Line Optimization Results", fontsize=16)

    axs[0, 0].bar(['Unit CELL', 'Series CELL', 'Parallel CELL'],
                 [unit_data['total_time'], series_data['total_time'], parallel_data['total_time']],
                 color=['#FF9999', '#66B2FF', '#99FF99'])
    axs[0, 0].set_title("Total Production Time Comparison")
    axs[0, 0].set_ylabel("Time (minutes)")
    axs[0, 0].grid(axis='y', linestyle='--', alpha=0.7)

    stages = ['Assembly', 'Test', 'Packaging']
    unit_times = [
        max(unit_data['assembly']['time_A1'], unit_data['assembly']['time_A2']),
        max(unit_data['test']['time_A1'], unit_data['test']['time_A2']),
        max(unit_data['packaging']['time_A1'], unit_data['packaging']['time_A2'])
    ]
    series_times = series_data['times']
    parallel_times = parallel_data['times']

    bar_width = 0.25
    x = np.arange(len(stages))
    axs[0, 1].bar(x - bar_width, unit_times, width=bar_width, label='Unit CELL', color='#FF9999')
    axs[0, 1].bar(x, series_times, width=bar_width, label='Series CELL', color='#66B2FF')
    axs[0, 1].bar(x + bar_width, parallel_times, width=bar_width, label='Parallel CELL', color='#99FF99')
    axs[0, 1].set_title("Stage-wise Time Distribution")
    axs[0, 1].set_ylabel("Time (minutes)")
    axs[0, 1].set_xticks(x, stages)
    axs[0, 1].legend()

    def get_worker_distribution(data, structure):
        if structure == 'Unit CELL':
            return [
                data['assembly']['A1'] + data['assembly']['A2'],
                data['test']['A1'] + data['test']['A2'],
                data['packaging']['A1'] + data['packaging']['A2']
            ]
        else:
            return [data['assembly'], data['test'], data['packaging']] if structure == 'Series CELL' \
                else [data['assembly'][0]*data['assembly'][1], data['test'][0]*data['test'][1], data['packaging'][0]*data['packaging'][1]]

    unit_workers = get_worker_distribution(unit_data, 'Unit CELL')
    series_workers = get_worker_distribution(series_data, 'Series CELL')
    parallel_workers = get_worker_distribution(parallel_data, 'Parallel CELL')

    axs[1, 0].pie(series_workers, labels=stages, autopct='%1.1f%%', startangle=90, colors=['#66B2FF', '#FF9999', '#99FF99'])
    axs[1, 0].set_title("Worker Distribution - Series CELL")

    axs[1, 1].pie(parallel_workers, labels=stages, autopct='%1.1f%%', startangle=90, colors=['#66B2FF', '#FF9999', '#99FF99'])
    axs[1, 1].set_title("Worker Distribution - Parallel CELL")

    plt.tight_layout()
    plt.subplots_adjust(top=0.92)
    plt.show()
    
if __name__ == "__main__":
    unit_time, unit_data = cell_unit_optimization()
    series_time, series_data = cell_series_optimization()
    parallel_time, parallel_data = cell_parallel_optimization()

    print_detailed_result('单元级CELL', unit_data)
    print_detailed_result('直线型CELL', series_data)
    print_detailed_result('混联型CELL', parallel_data)

    visualize_results(unit_data, series_data, parallel_data)

    best_structure = '直线型CELL' if series_time <= parallel_time else '混联型CELL'
    best_time = min(series_time, parallel_time, unit_time)
    
    print(f"\n===== 最终推荐方案 =====")
    print(f"最优结构: {best_structure}")
    print(f"总生产时间: {best_time:.2f}分钟")
    print(f"总工人数利用: 48人")
    print(f"效率指标(设备利用率): {(60900/(best_time*48))*100:.2f}%")