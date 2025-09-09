# 数学基准任务详细拆分文档

本文档对math_bench.md中提出的AI推理能力基准进行详细拆分，每个子任务都作为独立模块进行描述和实现方法说明。

## 目录

1. [群论任务系列](#群论任务系列)
2. [自动机理论任务系列](#自动机理论任务系列)
3. [计算拓扑学任务系列](#计算拓扑学任务系列)
4. [数理逻辑任务系列](#数理逻辑任务系列)

---

## 群论任务系列

### 任务1.1: IsSimple - 判断单群

#### 详细描述
判断一个有限群是否为单群（Simple Group）。单群是指除了平凡群{e}和自身外，没有其他正规子群的群。

#### 数学背景
- **定义**: 群G是单群当且仅当其正规子群只有{e}和G本身
- **重要性**: 单群是群论的"原子"，所有有限群都可由单群通过扩张构建
- **相关定理**: 有限单群分类定理（CFSG）

#### 实现方法
```python
def is_simple(group_representation):
    """
    判断群是否为单群
    
    输入:
    - group_representation: 群的表示（凯莱表或置换生成元）
    
    输出:
    - bool: True表示是单群，False表示不是
    
    算法步骤:
    1. 构建群的所有元素
    2. 枚举所有可能的子群
    3. 对每个子群检查是否为正规子群
    4. 如果存在非平凡正规子群，返回False
    5. 否则返回True
    """
    pass
```

#### 测试用例示例
```json
{
  "input": {
    "type": "permutation_generators",
    "domain_size": 5,
    "generators": [
      [1, 2, 3, 4, 0],  // 5-循环
      [1, 0, 3, 2, 4]   // (0 1)(2 3)
    ]
  },
  "expected_output": true,
  "explanation": "这是A₅（五次交替群），是最小的非交换单群"
}
```

---

### 任务1.2: IsAbelian - 判断交换群

#### 详细描述
判断一个有限群是否为阿贝尔群（Abelian Group），即群中所有元素都满足交换律。

#### 数学背景
- **定义**: 群G是阿贝尔群当且仅当对所有a,b∈G，有ab=ba
- **重要性**: 阿贝尔群的结构理论相对简单，有限阿贝尔群基本定理给出了完整分类
- **应用**: 密码学、编码理论中广泛使用

#### 实现方法
```python
def is_abelian(group_representation):
    """
    判断群是否为阿贝尔群
    
    输入:
    - group_representation: 群的表示
    
    输出:
    - bool: True表示是阿贝尔群，False表示不是
    
    算法步骤:
    1. 如果是凯莱表形式：
       - 检查表是否关于主对角线对称
    2. 如果是生成元形式：
       - 检查所有生成元两两是否交换
       - 或构建完整的群表后检查
    """
    pass
```

#### 测试用例示例
```json
{
  "input": {
    "type": "cayley_table",
    "table": [
      [0, 1, 2, 3],
      [1, 0, 3, 2],
      [2, 3, 0, 1],
      [3, 2, 1, 0]
    ]
  },
  "expected_output": true,
  "explanation": "这是Klein四元群V₄，是阿贝尔群"
}
```

---

### 任务1.3: IsCyclic - 判断循环群

#### 详细描述
判断一个有限群是否为循环群（Cyclic Group），即是否存在一个元素能生成整个群。

#### 数学背景
- **定义**: 群G是循环群当且仅当存在g∈G使得G=⟨g⟩
- **性质**: 所有循环群都是阿贝尔群
- **分类**: n阶循环群同构于Z/nZ

#### 实现方法
```python
def is_cyclic(group_representation):
    """
    判断群是否为循环群
    
    输入:
    - group_representation: 群的表示
    
    输出:
    - bool: True表示是循环群，False表示不是
    
    算法步骤:
    1. 获取群的阶数n
    2. 对每个元素g：
       a. 计算g的阶（最小正整数k使得g^k=e）
       b. 如果某个元素的阶等于n，返回True
    3. 如果没有找到生成元，返回False
    """
    pass
```

#### 测试用例示例
```json
{
  "input": {
    "type": "permutation_generators",
    "domain_size": 6,
    "generators": [
      [1, 2, 3, 4, 5, 0]  // 6-循环
    ]
  },
  "expected_output": true,
  "explanation": "由单个6-循环生成的群是6阶循环群"
}
```

---

### 任务1.4: Center - 计算群的中心

#### 详细描述
计算群的中心（Center），即与群中所有元素都交换的元素构成的集合。

#### 数学背景
- **定义**: Z(G) = {z∈G | ∀g∈G, zg=gz}
- **性质**: 中心是G的正规子群，且是阿贝尔群
- **应用**: 中心在群的结构理论中起重要作用

#### 实现方法
```python
def compute_center(group_representation):
    """
    计算群的中心
    
    输入:
    - group_representation: 群的表示
    
    输出:
    - list: 中心元素的索引列表
    
    算法步骤:
    1. 初始化中心为空集
    2. 对每个元素z：
       a. 检查z是否与所有元素交换
       b. 如果是，将z加入中心
    3. 返回中心元素列表
    """
    pass
```

#### 测试用例示例
```json
{
  "input": {
    "type": "cayley_table",
    "table": [
      [0, 1, 2],
      [1, 2, 0],
      [2, 0, 1]
    ]
  },
  "expected_output": [0, 1, 2],
  "explanation": "3阶循环群是阿贝尔群，中心是整个群"
}
```

---

## 自动机理论任务系列

### 任务2.1: IsEmpty - 判断语言空性

#### 详细描述
判断有限自动机（DFA/NFA）接受的语言是否为空集，即是否存在至少一个被接受的字符串。

#### 数学背景
- **定义**: L(A) = ∅ 当且仅当不存在从初始状态到任何接受状态的路径
- **复杂度**: 可在O(|Q|+|δ|)时间内判定（图可达性）
- **应用**: 编译器优化、正则表达式分析

#### 实现方法
```python
def is_empty(automaton):
    """
    判断自动机接受的语言是否为空
    
    输入:
    - automaton: DFA/NFA的JSON表示
    
    输出:
    - bool: True表示语言为空，False表示非空
    
    算法步骤:
    1. 从初始状态开始进行BFS/DFS
    2. 标记所有可达状态
    3. 检查是否有接受状态被标记
    4. 如果有，返回False；否则返回True
    """
    pass
```

#### 测试用例示例
```json
{
  "input": {
    "states": ["q0", "q1", "q2"],
    "alphabet": ["a", "b"],
    "transitions": {
      "q0": {"a": "q1"},
      "q1": {"b": "q2"},
      "q2": {}
    },
    "start_state": "q0",
    "accept_states": ["q2"]
  },
  "expected_output": false,
  "explanation": "字符串'ab'被接受，语言非空"
}
```

---

### 任务2.2: IsUniversal - 判断语言全集性

#### 详细描述
判断DFA是否接受字母表上的所有可能字符串，即L(A) = Σ*。

#### 数学背景
- **等价条件**: L(A) = Σ* ⟺ L(Ā) = ∅（补自动机语言为空）
- **复杂度**: PSPACE完全（对NFA），多项式时间（对DFA）
- **技巧**: 构造补DFA并检查空性

#### 实现方法
```python
def is_universal(dfa):
    """
    判断DFA是否接受所有字符串
    
    输入:
    - dfa: DFA的JSON表示
    
    输出:
    - bool: True表示接受所有字符串，False表示不是
    
    算法步骤:
    1. 构造补DFA（交换接受状态和非接受状态）
    2. 检查补DFA的语言是否为空
    3. 如果补DFA语言为空，返回True
    4. 否则返回False
    """
    pass
```

#### 测试用例示例
```json
{
  "input": {
    "states": ["q0"],
    "alphabet": ["a", "b"],
    "transitions": {
      "q0": {"a": "q0", "b": "q0"}
    },
    "start_state": "q0",
    "accept_states": ["q0"]
  },
  "expected_output": true,
  "explanation": "只有一个状态且是接受状态，接受所有字符串"
}
```

---

### 任务2.3: IsEquivalent - 判断语言等价性

#### 详细描述
判断两个DFA是否接受相同的语言，即L(A₁) = L(A₂)。

#### 数学背景
- **等价条件**: L(A₁) = L(A₂) ⟺ L(A₁⊕A₂) = ∅（对称差为空）
- **Hopcroft算法**: 基于等价类的高效算法
- **应用**: 编译器优化、验证等价变换

#### 实现方法
```python
def is_equivalent(dfa1, dfa2):
    """
    判断两个DFA是否等价
    
    输入:
    - dfa1, dfa2: 两个DFA的JSON表示
    
    输出:
    - bool: True表示等价，False表示不等价
    
    算法步骤:
    方法1（对称差）:
    1. 构造A₁∩Ā₂（A₁接受但A₂不接受）
    2. 构造Ā₁∩A₂（A₂接受但A₁不接受）
    3. 检查两个交集是否都为空
    
    方法2（Hopcroft）:
    1. 构造乘积自动机
    2. 使用等价类算法判定
    """
    pass
```

#### 测试用例示例
```json
{
  "input": {
    "dfa1": {
      "states": ["p0", "p1"],
      "alphabet": ["a"],
      "transitions": {
        "p0": {"a": "p1"},
        "p1": {"a": "p0"}
      },
      "start_state": "p0",
      "accept_states": ["p0"]
    },
    "dfa2": {
      "states": ["q0", "q1"],
      "alphabet": ["a"],
      "transitions": {
        "q0": {"a": "q1"},
        "q1": {"a": "q0"}
      },
      "start_state": "q0",
      "accept_states": ["q0"]
    }
  },
  "expected_output": true,
  "explanation": "两个DFA都接受偶数个'a'的字符串"
}
```

---

## 计算拓扑学任务系列

### 任务3.1: BettiNumbers - 计算贝蒂数

#### 详细描述
从单纯复形计算各维度的贝蒂数，它们刻画了空间中不同维度"洞"的数量。

#### 数学背景
- **定义**: bₖ = rank(Hₖ)，第k个同调群的秩
- **直观意义**: 
  - b₀: 连通分量数
  - b₁: 一维洞（环）的数量
  - b₂: 二维空腔的数量
- **计算**: 通过边界矩阵的秩计算

#### 实现方法
```python
def compute_betti_numbers(simplicial_complex):
    """
    计算单纯复形的贝蒂数
    
    输入:
    - simplicial_complex: 单纯形列表
    
    输出:
    - list: 贝蒂数序列[b₀, b₁, b₂, ...]
    
    算法步骤:
    1. 构建各维度的链群Cₖ
    2. 计算边界算子∂ₖ的矩阵表示
    3. 对每个维度k：
       a. 计算Zₖ = ker(∂ₖ)的维数
       b. 计算Bₖ = im(∂ₖ₊₁)的维数
       c. bₖ = dim(Zₖ) - dim(Bₖ)
    4. 返回贝蒂数序列
    """
    pass
```

#### 测试用例示例
```json
{
  "input": {
    "simplicial_complex": [
      [0], [1], [2], [3],           // 顶点
      [0, 1], [1, 2], [2, 3], [3, 0], // 边
      [0, 2]                         // 对角线
    ]
  },
  "expected_output": [1, 0, 0],
  "explanation": "带对角线的正方形，连通且无洞"
}
```

---

### 任务3.2: EulerCharacteristic - 计算欧拉示性数

#### 详细描述
计算单纯复形的欧拉示性数，这是一个重要的拓扑不变量。

#### 数学背景
- **定义**: χ = Σ(-1)ᵏ·fₖ，其中fₖ是k维单纯形的数量
- **欧拉-庞加莱公式**: χ = Σ(-1)ᵏ·bₖ
- **例子**: 球面χ=2，环面χ=0

#### 实现方法
```python
def compute_euler_characteristic(simplicial_complex):
    """
    计算欧拉示性数
    
    输入:
    - simplicial_complex: 单纯形列表
    
    输出:
    - int: 欧拉示性数
    
    算法步骤:
    方法1（组合）:
    1. 统计各维度单纯形数量fₖ
    2. 计算χ = f₀ - f₁ + f₂ - f₃ + ...
    
    方法2（同调）:
    1. 计算贝蒂数bₖ
    2. 计算χ = b₀ - b₁ + b₂ - b₃ + ...
    """
    pass
```

#### 测试用例示例
```json
{
  "input": {
    "simplicial_complex": [
      [0], [1], [2], [3],              // 4个顶点
      [0, 1], [0, 2], [0, 3],          // 6条边
      [1, 2], [1, 3], [2, 3],
      [0, 1, 2], [0, 1, 3],            // 4个三角形
      [0, 2, 3], [1, 2, 3],
      [0, 1, 2, 3]                     // 1个四面体（实心）
    ]
  },
  "expected_output": 1,
  "explanation": "实心四面体，拓扑等价于三维球，χ=4-6+4-1=1"
}
```

---

## 数理逻辑任务系列

### 任务4.1: SAT - 布尔可满足性判定

#### 详细描述
判断合取范式（CNF）形式的命题逻辑公式是否存在使其为真的变量赋值。

#### 数学背景
- **Cook-Levin定理**: SAT是第一个被证明的NP完全问题
- **应用**: 电路验证、AI规划、密码分析
- **算法**: DPLL、CDCL、局部搜索

#### 实现方法
```python
def solve_sat(cnf_formula):
    """
    判断CNF公式的可满足性
    
    输入:
    - cnf_formula: 子句列表，每个子句是文字列表
    
    输出:
    - dict: {"satisfiable": bool, "assignment": dict或None}
    
    算法步骤（DPLL）:
    1. 单元传播：如果存在单子句，固定其值
    2. 纯文字消除：如果变量只以一种极性出现，赋相应值
    3. 选择未赋值变量，递归尝试两种赋值
    4. 如果找到满足赋值，返回True和赋值
    5. 如果所有分支都失败，返回False
    """
    pass
```

#### 测试用例示例
```json
{
  "input": {
    "cnf_formula": [
      [1, 2, -3],     // (x₁ ∨ x₂ ∨ ¬x₃)
      [-1, 3],        // (¬x₁ ∨ x₃)
      [-2, -3],       // (¬x₂ ∨ ¬x₃)
      [1, -2]         // (x₁ ∨ ¬x₂)
    ]
  },
  "expected_output": {
    "satisfiable": true,
    "assignment": {"1": true, "2": false, "3": true}
  },
  "explanation": "赋值x₁=T, x₂=F, x₃=T满足所有子句"
}
```

---

### 任务4.2: Tautology - 永真式判定

#### 详细描述
判断一个命题逻辑公式是否在所有可能的变量赋值下都为真。

#### 数学背景
- **定义**: φ是永真式 ⟺ ¬φ不可满足
- **复杂度**: co-NP完全
- **例子**: (p ∨ ¬p)是永真式

#### 实现方法
```python
def is_tautology(formula):
    """
    判断公式是否为永真式
    
    输入:
    - formula: S表达式形式的公式字符串
    
    输出:
    - bool: True表示是永真式，False表示不是
    
    算法步骤:
    1. 解析公式为语法树
    2. 计算公式的否定¬φ
    3. 将¬φ转换为CNF形式
    4. 对CNF调用SAT求解器
    5. 如果¬φ不可满足，返回True（φ是永真式）
    6. 否则返回False
    """
    pass
```

#### 测试用例示例
```json
{
  "input": {
    "formula": "(or (and p q) (and (not p) r) (and (not q) (not r)))"
  },
  "expected_output": false,
  "explanation": "当p=F, q=F, r=F时公式为假，不是永真式"
}
```

---

### 任务4.3: ModelCheck - 模型检验

#### 详细描述
给定一个有限的一阶逻辑模型和一个逻辑句子，判断该句子在模型中是否为真。

#### 数学背景
- **模型**: M = (D, I)，其中D是论域，I是解释函数
- **语义**: 递归定义的满足关系M ⊨ φ
- **应用**: 软件验证、数据库查询

#### 实现方法
```python
def model_check(model, sentence):
    """
    检验句子在模型中的真值
    
    输入:
    - model: 包含domain和interpretations的字典
    - sentence: 一阶逻辑句子（S表达式）
    
    输出:
    - bool: True表示句子在模型中为真
    
    算法步骤:
    1. 解析句子为语法树
    2. 递归求值：
       a. 原子公式：查表
       b. 连接词：递归计算子公式
       c. 量词：遍历论域元素
    3. 返回最终真值
    """
    pass
```

#### 测试用例示例
```json
{
  "input": {
    "model": {
      "domain": [1, 2, 3],
      "relations": {
        "Less": [[1, 2], [1, 3], [2, 3]]
      },
      "functions": {},
      "constants": {"a": 1, "b": 3}
    },
    "sentence": "(forall x (exists y (Less x y)))"
  },
  "expected_output": false,
  "explanation": "并非所有元素都有更大的元素（3没有）"
}
```

---

## 实现框架

### 统一接口设计

```python
class MathBenchmarkTask:
    """所有数学基准任务的基类"""
    
    def __init__(self, task_name, domain):
        self.task_name = task_name
        self.domain = domain
    
    def generate_instance(self, difficulty_params):
        """生成问题实例"""
        raise NotImplementedError
    
    def solve(self, instance):
        """使用权威算法求解"""
        raise NotImplementedError
    
    def format_for_ai(self, instance, solution):
        """格式化为AI友好的形式"""
        raise NotImplementedError
    
    def validate_answer(self, instance, answer):
        """验证答案正确性"""
        raise NotImplementedError
```

### 批量生成流程

```python
def generate_benchmark_dataset(task_class, num_instances, difficulty_range):
    """
    批量生成基准数据集
    
    参数:
    - task_class: 任务类
    - num_instances: 生成实例数量
    - difficulty_range: 难度参数范围
    
    返回:
    - dataset: 包含问题和答案的数据集
    """
    dataset = []
    for i in range(num_instances):
        # 随机选择难度参数
        difficulty = random.choice(difficulty_range)
        
        # 生成实例
        instance = task_class.generate_instance(difficulty)
        
        # 求解
        solution = task_class.solve(instance)
        
        # 格式化
        formatted = task_class.format_for_ai(instance, solution)
        
        dataset.append(formatted)
    
    return dataset
```

### 评测框架

```python
def evaluate_ai_on_benchmark(ai_model, benchmark_dataset):
    """
    评测AI模型在基准上的表现
    
    参数:
    - ai_model: AI模型接口
    - benchmark_dataset: 基准数据集
    
    返回:
    - metrics: 评测指标字典
    """
    correct = 0
    total = len(benchmark_dataset)
    
    for item in benchmark_dataset:
        # AI生成答案
        ai_answer = ai_model.generate_answer(item['problem'])
        
        # 验证答案
        is_correct = item['task'].validate_answer(
            item['instance'], 
            ai_answer
        )
        
        if is_correct:
            correct += 1
    
    return {
        'accuracy': correct / total,
        'correct': correct,
        'total': total
    }
```

## 总结

本文档详细拆分了math_bench.md中提出的12个核心数学任务，每个任务都包含：

1. **详细描述**: 任务的具体要求和目标
2. **数学背景**: 相关的数学理论和概念
3. **实现方法**: 算法步骤和伪代码
4. **测试用例**: 具体的输入输出示例

这些任务涵盖了群论、自动机理论、计算拓扑学和数理逻辑四个重要的数学分支，可以全面评测AI系统的：
- 抽象结构理解能力
- 符号推理能力
- 算法执行能力
- 逻辑演绎能力

通过统一的生成框架和评测框架，这些任务可以批量生成大规模数据集，为AI的训练和评测提供高质量的基准。