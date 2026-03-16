# HK Intelligent Trip Planner – Planner Agent

This module implements the **Planner Agent** for the HK Intelligent Trip Planner project.  
It generates a **multi-day travel itinerary for Hong Kong** using a **local Large Language Model (LLM)** and a predefined activity dataset.

The Planner Agent takes:

- a **user travel request**
- a **set of available activities**

and generates a structured **JSON itinerary** that can be used by other system components (e.g., Budget Tool, Critic Agent, Frontend).

---

# 1. Module Function

The Planner Agent workflow:

1. **Load activity dataset** (`hk_activities.json`)
2. **Select a subset of activities**
3. **Build a prompt** combining:
   - user request
   - activity dataset
   - JSON schema instructions
4. **Send the prompt to a local LLM**
5. **Extract JSON from model output**
6. **Validate the itinerary structure**
7. Return the itinerary JSON

Example output format:

```json
{
  "destination": "Hong Kong",
  "days": 2,
  "total_estimated_cost_hkd": 492,
  "budget_limit_hkd": 800,
  "within_budget": true,
  "itinerary": [...],
  "planning_summary": "..."
}
````

---

# 2. Model Used

The Planner Agent uses a **local LLM instead of a paid API**.

Model:

```
mistral:7b
```

Run via **Ollama**.

Advantages:

* Free
* No API key required
* Works offline
* Suitable for academic projects

---

# 3. Setup Instructions

## Install Ollama

Download from:

[https://ollama.com/download](https://ollama.com/download)

Verify installation:

```bash
ollama --version
```

---

## Download the model

Run:

```bash
ollama run mistral:7b
```

This downloads the model (~4GB).

Exit after download:

```
/exit
```

---

## Install Python dependencies

Inside the project directory:

```bash
pip install -r requirements.txt
```

---

## Run Planner Agent test

```bash
python -m planner_agent.test_planner
```

Expected log output:

```
[1] Building prompt...
[2] Sending prompt to Ollama...
[3] Raw output received...
[4] JSON extracted.
[5] Output validated.
```

This indicates successful itinerary generation.

---

# 4. Activity Dataset

The dataset is stored in:

```
data/hk_activities.json
```

The dataset contains **43 activities in Hong Kong**, covering categories such as:

* sightseeing
* museums
* nature
* food
* nightlife
* shopping
* family-friendly
* local experiences

Each activity includes fields such as:

* name
* category
* area
* best_time
* duration_hours
* cost_hkd
* indoor
* tags

---

# 5. Random Activity Sampling (Important)

To keep the prompt length manageable for a local LLM, the Planner Agent **does not send all 43 activities to the model at once**.

Instead, **10 activities are randomly sampled each time the planner runs.**

Example implementation:

```python
import random

activities = load_activities("data/hk_activities.json")
activities = random.sample(activities, 10)
```

### Why this is done

Local LLMs such as **Mistral 7B** can become unstable with very long prompts.

Using all 43 activities may cause:

* incomplete JSON outputs
* formatting errors
* the model ignoring schema constraints

Random sampling ensures:

* prompt length stays manageable
* better generation stability
* itinerary diversity across runs

Each run of the planner may therefore produce **different travel plans**.

---

# 6. Project Structure (Relevant Files)

```
planner_agent/
│
├── planner.py
│   Main Planner Agent logic
│
├── prompt_builder.py
│   Builds the LLM prompt
│
├── ollama_client.py
│   Handles communication with Ollama
│
├── load_data.py
│   Loads activity dataset
│
├── schemas.py
│   Defines data structures
│
└── test_planner.py
    Script for testing the Planner Agent
```

---

# 7. Debug Logging

The Planner Agent prints debug logs to help diagnose issues:

```
[1] Building prompt...
[2] Sending prompt to Ollama...
[3] Raw output received...
[4] JSON extracted.
[5] Output validated.
```

These logs help detect:

* prompt issues
* LLM formatting errors
* JSON extraction failures

---

# 8. Known Limitations

Current limitations include:

* Output quality depends on the local LLM.
* Local models are less reliable than large cloud models.

Possible improvements:

* stronger prompt engineering
* critic agent for itinerary review
* budget optimization module

---