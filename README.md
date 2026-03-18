# HK Intelligent Trip Planner

This module implements the **Planner Agent** for the HK Intelligent Trip Planner project.  
It generates a **multi-day travel itinerary for Hong Kong** using a **local Large Language Model (LLM)** and a predefined activity dataset.

目前系统设计说明：
本系统将用户输入的预算定义为**整趟旅行的总预算（total trip budget）**，并通过模块化设计将预算处理与行程生成解耦。首先，由 **Budget Tool** 根据旅行天数、人数、节奏（pace）以及预算档位（**budget_style**）对固定成本进行启发式估算。`budget_style` 表示旅行消费水平（如 *economy / standard / premium*），可以由用户显式指定，或根据用户偏好（如 “budget”“luxury”）以及人均日预算自动推断，不同档位对应不同的住宿、餐饮和交通成本水平。在此基础上，系统计算出固定成本（accommodation、food、transport、misc），并从总预算中扣除，得到剩余可用于活动的预算（activity budget）。随后，**Planner Agent** 仅基于该活动预算和活动数据集生成多日行程（itinerary），不涉及任何固定成本的计算。为保证结果可靠，Planner 会对模型输出进行结构校验与费用重算，而不直接信任 LLM 的预算判断。最后，再由 **Budget Tool** 将活动成本与固定成本合并进行整体预算核算，判断活动是否超出活动预算，以及整趟旅行是否超出总预算。通过这种“预算分配 → 行程生成 → 预算校验”的流程，并结合 `budget_style` 的动态成本估计机制，系统能够在保证灵活性的同时提供更符合真实旅行情境的规划结果。


⚠️ **IMPORTANT UPDATE (Architecture Change)**  
The system now includes a **Budget Tool module**.  
The Planner Agent is **no longer responsible for total budget calculation**.

---

# 1. Module Function

The Planner Agent generates a structured **JSON itinerary** based on:

- a **user travel request**
- a **set of available activities**
- an **activity budget (provided by Budget Tool)**

---

## Updated Workflow

1. Load activity dataset (`hk_activities.json`)
2. Call **Budget Tool** to estimate:
   - fixed travel costs (住宿 / 餐饮 / 交通 / 杂项)
   - remaining **activity budget**
3. Build prompt using:
   - user request
   - activity dataset
   - activity budget constraint
4. Send prompt to local LLM
5. Extract JSON from model output
6. Validate itinerary structure
7. Recalculate costs (do not trust model)
8. Return final itinerary JSON

---

# 2. System Architecture (Updated)

The system is now modular:

```

User Request
↓
Budget Tool (estimate_fixed_costs)
↓
Planner Agent (generate itinerary)
↓
Budget Tool (estimate_budget)
↓
Critic Agent (future)
↓
Frontend

```

---

## Responsibility Separation

| Component | Responsibility |
|----------|--------------|
| Budget Tool | Estimate fixed costs & validate total budget |
| Planner Agent | Generate itinerary using activity budget |
| Critic Agent | Evaluate plan quality (future work) |
| Frontend | Display results |

---

# 3. Budget Handling Logic (Core Design)

The user-provided budget is interpreted as:

```

TOTAL TRIP BUDGET

```

The system computes:

```

activity_budget = total_budget - fixed_cost_estimate

````

---

## Important Rules

Planner Agent must:

- ONLY use `activity_budget_hkd`
- NOT include:
  - accommodation
  - meals
  - transport
  - misc costs
- ONLY select activities from dataset

---

# 4. Example Output (Updated Schema)

```json
{
  "destination": "Hong Kong",
  "days": 2,
  "activity_budget_hkd": 1200,
  "total_estimated_activity_cost_hkd": 980,
  "activities_within_budget": true,
  "itinerary": [
    {
      "day": 1,
      "morning": {...},
      "afternoon": {...},
      "evening": {...},
      "daily_cost_hkd": 0,
      "notes": "..."
    }
  ],
  "planning_summary": "...",
  "budget_context": {
    "total_budget_hkd": 3000,
    "fixed_cost_estimate_hkd": 1800,
    "activity_budget_hkd": 1200
  }
}
````

---

# 5. Model Used

The Planner Agent uses a **local LLM**:

```
mistral:7b
```

Run via:

```
Ollama
```

---

## Advantages

* Free
* No API key required
* Works offline
* Suitable for coursework

---

# 6. Setup Instructions

## Install Ollama

Download from:

[https://ollama.com/download](https://ollama.com/download)

Verify installation:

```bash
ollama --version
```

---

## Download Model

```bash
ollama run mistral:7b
```

Exit after download:

```
/exit
```

---

## Install Python Dependencies

```bash
pip install -r requirements.txt
```

---

# 7. Run Full System Test

```bash
python -m planner_agent.test_planner
```

---

## Expected Logs

```
[1] Estimating fixed costs and activity budget...
[2] Building prompt...
[3] Sending prompt to Ollama...
[4] Raw output received...
[5] JSON extracted.
[6] Output validated.
[7] Output normalized.
```

---

# 8. Activity Dataset

Location:

```
data/hk_activities.json
```

Contains ~43 Hong Kong activities.

Categories include:

* sightseeing
* museums
* nature
* food
* shopping
* nightlife
* family-friendly

---

# 9. Activity Sampling (Important)

To control prompt length:

```python
activities = random.sample(activities, 10)
```

---

## Why Sampling Is Used

Local LLMs (e.g., Mistral 7B) may fail with long prompts:

* incomplete JSON
* schema violations
* ignored constraints

---

## Recommended Range

```
10 ~ 25 activities
```

⚠️ Too few activities may cause:

* missing days
* repeated activities
* invalid itinerary

---

# 10. Debug Logging

Planner Agent prints logs:

```
[1] Estimating fixed costs
[2] Building prompt
[3] Sending prompt
[4] JSON extracted
[5] Output validated
[6] Output normalized
```

---

# 11. Key Design Principles

## 1. Do NOT trust LLM output

All costs are:

* recalculated in code
* validated strictly

---

## 2. Separate concerns

* Planner → itinerary
* Budget Tool → money
* Critic → quality

---

## 3. Enforce strict JSON schema

Planner output must always:

* match required keys
* match day count
* include all time slots

---

# 12. Known Limitations

* Local LLM may:

  * skip days
  * break JSON
  * ignore constraints
* Budget estimation is heuristic
* Activity sampling affects quality

---

# 13. Future Improvements

* Add Critic Agent
* Improve budget estimation
* Multi-user support
* Frontend UI
* Retry mechanism for LLM failures

---

# 14. Notes for Developers

⚠️ When extending the system:

* Do NOT move budget logic back into Planner
* Always use Budget Tool for cost calculations
* Keep JSON schema consistent across modules

---

```
```
