
# HK 智能行程规划系统（HK Intelligent Trip Planner）

本项目实现了一个基于本地大语言模型（LLM）的**香港旅行规划系统**，能够根据用户需求自动生成多日行程，并进行预算校验与质量评估。

---

好的，这是**仅流程图部分（可直接替换）**👇

```markdown
# 🧠 当前系统架构（核心流程）

```

┌──────────────────────────────┐
│  User Request（用户输入）     │
└──────────────┬───────────────┘
↓
┌──────────────────────────────┐
│  Budget Tool                 │
│  估算固定成本（住宿/餐饮/交通）│
└──────────────┬───────────────┘
↓
┌──────────────────────────────┐
│  Activity Budget             │
│  计算活动预算（剩余预算）     │
└──────────────┬───────────────┘
↓
┌──────────────────────────────┐
│  Planner Agent（LLM）        │
│  只选择活动名称              │
└──────────────┬───────────────┘
↓
┌──────────────────────────────┐
│  Resolver / Normalizer       │
│  回填真实数据 + 计算费用     │
└──────────────┬───────────────┘
↓
┌──────────────────────────────┐
│  Budget Tool                 │
│  最终预算核算                │
└──────────────┬───────────────┘
↓
┌──────────────────────────────┐
│  Critic Agent               │
│  行程质量评估               │
└──────────────┬───────────────┘
↓
┌──────────────────────────────┐
│  Final Output               │
│  最终结果输出               │
└──────────────────────────────┘

```
```


# 📌 核心设计思想（非常重要）

本系统采用以下关键设计原则：

### ✅ 1. LLM 只负责“选择”，不负责“计算”

* LLM **只输出活动名称 + 简短理由**
* 不负责：

  * 成本计算
  * 时长计算
  * 预算汇总
* 所有数值由代码生成（避免 hallucination）

---

### ✅ 2. 预算逻辑完全解耦

用户输入的是：

```
TOTAL TRIP BUDGET（整趟旅行总预算）
```

系统流程：

```
总预算 → 固定成本估算 → 剩余活动预算 → 行程生成 → 最终预算校验
```

---

### ✅ 3. 不信任 LLM 的数值

所有以下字段：

* cost
* duration
* daily_cost
* total_cost

👉 **全部由代码从 dataset 回填**

---

### ✅ 4. 强约束：只能使用数据集中的活动

LLM 被严格限制：

* ❌ 不允许编造活动
* ❌ 不允许输出 dataset 外的内容
* ❌ 若无匹配偏好 → 忽略，不编造

---

# 🧩 模块说明

## 1. Budget Tool（预算模块）

负责：

* 推断预算风格（economy / standard / premium）
* 估算固定成本：

  * 住宿
  * 餐饮
  * 交通
  * 杂项
* 计算活动预算（activity budget）

---

## 2. Planner Agent（行程生成）

输入：

* 用户请求
* 活动数据集
* 活动预算 cap

输出：

* 每天 morning / afternoon / evening 的活动名称
* 简短理由

⚠️ 不输出任何预算数值

---

## 3. Resolver / Normalizer（关键模块）

负责：

* 根据 activity_name 查 dataset
* 补全真实字段：

  * area
  * category
  * cost_hkd
  * duration_hours
* 计算：

  * daily_cost
  * total_cost

👉 **这是系统稳定的关键**

---

## 4. Budget Tool（二次使用）

再次计算：

* 活动总费用
* 总旅行费用
* 是否超预算

---

## 5. Critic Agent（评估模块）

评估：

* 预算合理性
* 行程节奏
* 偏好匹配
* 跨区问题
* 时间合理性

输出：

* score（评分）
* issues（问题）
* suggestions（建议）

---

# 🔁 当前完整流程

1. 读取活动数据（hk_activities.json）
2. Budget Tool 估算固定成本
3. 得到 activity_budget_hkd
4. 构建 prompt（包含预算约束）
5. LLM 选择活动
6. 提取 JSON
7. 结构校验
8. Resolver 回填真实数据
9. Budget Tool 计算最终预算
10. Critic Agent 评估质量
11. 输出最终结果

---

# 📊 示例输出结构

```json
{
  "destination": "Hong Kong",
  "days": 2,
  "activity_budget_hkd": 3750,
  "total_estimated_activity_cost_hkd": 406,
  "activities_within_budget": true,
  "itinerary": [
    {
      "day": 1,
      "morning": {...},
      "afternoon": {...},
      "evening": {...},
      "daily_cost_hkd": 180
    }
  ],
  "planning_summary": "...",
  "budget_context": {...}
}
```

---

# 🤖 使用模型

本项目使用：

```
mistral:7b (via Ollama)
```

优势：

* 免费
* 本地运行
* 无 API key
* 适合课程项目

---

# ⚙️ 运行方式

```bash
python -m planner_agent.test_planner
```

或：

```bash
python -m critic_agent.test_critic
```

---

# 🧪 重要设计：活动采样

```python
activities = random.sample(activities, 10)
```

原因：

* 控制 prompt 长度
* 避免 LLM 输出崩溃（JSON截断）

---

# 🛑 已解决的关键问题

| 问题              | 当前状态   |
| --------------- | ------ |
| LLM 编造活动        | ✅ 已解决  |
| 预算不一致           | ✅ 已解决  |
| summary 与真实值冲突  | ✅ 已解决  |
| must_include 失效 | ✅ 已修复  |
| JSON 不稳定        | ✅ 大幅改善 |

---

# ⚠️ 已知限制

* 本地 LLM 仍可能：

  * JSON 截断
  * 忽略部分约束（概率性）
* 预算为启发式估算
* 数据集规模有限

---

# 🚀 可选优化方向

* 引入 replan（基于 critic feedback）
* 提升预算利用率
* 更精细的区域聚类
* 多用户支持
* 前端界面

---

# 🧑‍💻 开发注意事项

⚠️ 不要破坏以下原则：

* 不要让 LLM 计算预算
* 不要信任 LLM 的 cost
* 必须通过 dataset 回填数据
* JSON schema 必须严格一致

---

# 📎 数据集

路径：

```
data/hk_activities.json
```

包含约 40+ 香港活动：

* sightseeing
* food
* culture
* shopping
* nightlife
* museum

