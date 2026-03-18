from typing import Dict, List
import json

# ================== 固定成本表（2026 香港真實參考，中檔）==================
DAILY_FIXED_COSTS = {
    "accommodation_per_person": 800,   # 中檔酒店/民宿（可後續改成 400/1200）
    "meals_per_day": 250,              # 茶餐廳 + 晚餐
    "transport_per_day": 80,           # MTR + 八達通
    "misc_per_day": 100                # 飲料、零食、小紀念品
}


def estimate_budget(planner_output: Dict) -> Dict:
    if not planner_output or "itinerary" not in planner_output:
        raise ValueError("輸入必須是 Planner Agent 的輸出 dict")

    days = planner_output.get("days", 1)
    user_budget = planner_output.get("budget_limit_hkd", 800)

    # 1. 計算活動總費用（優先用每日加總，更準確）
    activity_total = 0
    for day in planner_output.get("itinerary", []):
        activity_total += day.get("daily_cost_hkd", 0)

    # 2. 固定開支
    accommodation = DAILY_FIXED_COSTS["accommodation_per_person"] * days
    food = DAILY_FIXED_COSTS["meals_per_day"] * days
    transport = DAILY_FIXED_COSTS["transport_per_day"] * days
    misc = DAILY_FIXED_COSTS["misc_per_day"] * days

    grand_total = activity_total + accommodation + food + transport + misc

    # 3. 判斷與建議
    within_budget = grand_total <= user_budget
    over_by = max(0, grand_total - user_budget)

    suggestions = []
    if over_by > 0:
        suggestions.append(f"超支 {over_by} HKD，建議減少高價活動（如迪士尼、昂坪纜車）")
        suggestions.append("可改住九龍區（住宿降至 500-600/晚）或多用 MTR")
    else:
        suggestions.append("預算足夠，可考慮增加購物或夜景活動")

    result = {
        "total_estimated_cost_hkd": round(grand_total),
        "budget_limit_hkd": user_budget,
        "within_budget": within_budget,
        "over_budget_by": over_by,
        "breakdown": {
            "activities": round(activity_total),
            "accommodation": round(accommodation),
            "food": round(food),
            "transport": round(transport),
            "misc": round(misc)
        },
        "suggestions": suggestions
    }

    return result


# ================== quick test ==================
if __name__ == "__main__":
    sample_planner_output = {
        "destination": "Hong Kong",
        "days": 1,  # 注意改成 1
        "total_estimated_cost_hkd": 645,
        "budget_limit_hkd": 800,
        "within_budget": True,
        "itinerary": [
            {
                "day": 1,
                "daily_cost_hkd": 760
            }
        ],
        "planning_summary": "Day 1: Sightseeing, shopping, and nightlife with a harbour view."
    }

    budget_result = estimate_budget(sample_planner_output)
    print(json.dumps(budget_result, indent=2, ensure_ascii=False))