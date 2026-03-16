````markdown
# Planner Agent 接口说明文档  
（HK Intelligent Trip Planner 项目）

本文件用于说明 **Planner Agent 模块的输入、输出、调用方式以及运行环境约定**，确保后续组员在开发 **Critic Agent、Budget Tool、Frontend 或系统集成模块** 时能够正确对接 Planner Agent。

---

# 1. 模块作用

Planner Agent 的作用是：

根据 **用户旅行需求** 和 **活动数据集（hk_activities.json）**，使用 **本地大语言模型（LLM）** 自动生成一个 **多天香港旅行行程（itinerary）**。

输出结果为 **结构化 JSON 数据**，后续模块可以直接读取该 JSON 数据进行：

- 行程评估（Critic Agent）
- 预算计算（Budget Tool）
- 前端展示（Frontend）

---

# 2. 模块调用入口

Planner Agent 的唯一正式调用接口为：

```python
PlannerAgent.plan(user_request, activities)
````

示例调用方式：

```python
from planner_agent.load_data import load_activities
from planner_agent.schemas import UserRequest
from planner_agent.planner import PlannerAgent
import random

activities = load_activities("data/hk_activities.json")

# 为控制 prompt 长度，每次随机抽取 10 条活动
activities = random.sample(activities, 10)

user_request = UserRequest(
    destination="Hong Kong",
    days=2,
    total_budget_hkd=800,
    preferences=["sightseeing", "food", "budget"],
    pace="moderate",
    must_include=["Star Ferry Tsim Sha Tsui to Central"],
    avoid=["hiking"],
)

planner = PlannerAgent(model_name="mistral:7b")

result = planner.plan(user_request, activities)

print(result)
```

返回结果为 **Python 字典（dict）**，结构符合 itinerary JSON schema。

---

# 3. 输入接口说明

Planner Agent 有两个主要输入：

1️⃣ `UserRequest`
2️⃣ `Activity` 列表

---

# 3.1 UserRequest（用户请求）

UserRequest 定义在：

```
planner_agent/schemas.py
```

结构如下：

```python
UserRequest(
    destination: str,
    days: int,
    total_budget_hkd: float,
    preferences: List[str],
    pace: str = "moderate",
    must_include: Optional[List[str]] = None,
    avoid: Optional[List[str]] = None,
)
```

字段说明：

| 字段               | 含义                           |
| ---------------- | ---------------------------- |
| destination      | 旅行目的地，目前默认为 Hong Kong        |
| days             | 旅行天数                         |
| total_budget_hkd | 总预算（港币）                      |
| preferences      | 用户偏好，例如 sightseeing / food   |
| pace             | 行程节奏（slow / moderate / fast） |
| must_include     | 必须包含的活动                      |
| avoid            | 不希望出现的活动或类型                  |

---

# 3.2 Activity（活动数据）

Activity 数据来自：

```
data/hk_activities.json
```

结构定义在：

```
planner_agent/schemas.py
```

每条活动包含：

```python
Activity(
    name: str,
    category: str,
    area: str,
    best_time: str,
    duration_hours: float,
    cost_hkd: float,
    indoor: bool,
    tags: List[str],
)
```

字段说明：

| 字段             | 含义     |
| -------------- | ------ |
| name           | 活动名称   |
| category       | 活动类别   |
| area           | 地区     |
| best_time      | 推荐时间   |
| duration_hours | 活动时长   |
| cost_hkd       | 费用     |
| indoor         | 是否室内活动 |
| tags           | 标签     |

⚠️ **注意：**

后续模块如果使用 Activity 数据，请不要修改字段名称，否则会导致：

* `load_data.py` 出错
* `prompt_builder.py` 无法正常工作

---

# 4. Activity 随机抽样机制（重要）

完整数据集包含：

```
43 个活动
```

但 Planner Agent **不会一次性把所有活动发送给 LLM**。

当前实现方式：

```python
activities = load_activities("data/hk_activities.json")
activities = random.sample(activities, 10)
```

也就是说：

* 每次运行只随机选择 **10 条活动**
* LLM 只基于这 10 条活动生成 itinerary

这样做的原因是：

本项目使用 **本地模型 Mistral 7B**，如果 prompt 过长可能会出现：

* JSON 输出不完整
* 输出格式错误
* 模型忽略 schema

因此采用：

```
随机抽样 10 条活动
```

来保证 prompt 长度可控。

⚠️ 这意味着：

相同用户请求在不同运行中，可能会生成 **不同的 itinerary**。

---

# 5. 输出接口说明（JSON Schema）

Planner Agent 返回的结果为：

```
Python dict
```

结构如下：

```json
{
  "destination": "Hong Kong",
  "days": 2,
  "total_estimated_cost_hkd": 0,
  "budget_limit_hkd": 800,
  "within_budget": true,
  "itinerary": [
    {
      "day": 1,
      "morning": {
        "activity_name": "string",
        "area": "string",
        "category": "string",
        "estimated_cost_hkd": 0,
        "duration_hours": 0,
        "reason": "string"
      },
      "afternoon": {
        "activity_name": "string",
        "area": "string",
        "category": "string",
        "estimated_cost_hkd": 0,
        "duration_hours": 0,
        "reason": "string"
      },
      "evening": {
        "activity_name": "string",
        "area": "string",
        "category": "string",
        "estimated_cost_hkd": 0,
        "duration_hours": 0,
        "reason": "string"
      },
      "daily_cost_hkd": 0,
      "notes": "string"
    }
  ],
  "planning_summary": "string"
}
```

---

# 6. 输出字段说明

## 顶层字段

| 字段                       | 含义     |
| ------------------------ | ------ |
| destination              | 旅行目的地  |
| days                     | 旅行天数   |
| total_estimated_cost_hkd | 总花费    |
| budget_limit_hkd         | 用户预算   |
| within_budget            | 是否在预算内 |
| itinerary                | 每日行程   |
| planning_summary         | 行程总结   |

---

## 每日行程结构

每一天必须包含：

```
morning
afternoon
evening
```

每个 slot 包含：

| 字段                 | 含义   |
| ------------------ | ---- |
| activity_name      | 活动名称 |
| area               | 地区   |
| category           | 类型   |
| estimated_cost_hkd | 活动费用 |
| duration_hours     | 活动时长 |
| reason             | 推荐原因 |

⚠️ **这些字段名不能更改**，否则后续模块无法正确解析。

---

# 7. 运行环境

Planner Agent 使用本地 LLM：

```
mistral:7b
```

运行方式：

```
Ollama
```

模型调用参数：

```
temperature = 0.0
top_p = 0.8
```

运行前需安装：

```
Ollama
```

并下载模型：

```bash
ollama run mistral:7b
```

---

# 8. 错误处理机制

Planner Agent 内部会对 LLM 输出进行验证。

如果 JSON 不符合 schema，会抛出：

```
ValueError
```

常见原因包括：

* JSON 不完整
* 缺少字段
* slot 内容为空
* 行程天数不匹配

这是一种 **保护机制**，防止错误数据进入后续模块。

---

# 9. 推荐的模块使用方式

后续模块可以这样使用 Planner Agent 输出：

### Budget Tool

读取字段：

```
estimated_cost_hkd
daily_cost_hkd
total_estimated_cost_hkd
```

---

### Critic Agent

分析字段：

```
itinerary
area
duration_hours
reason
planning_summary
```

---

### Frontend

展示字段：

```
destination
days
itinerary
daily_cost_hkd
planning_summary
```

