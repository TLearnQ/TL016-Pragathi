def classify_day(total_revenue, total_cost):
    profit = total_revenue - total_cost
    if total_revenue == 0:
        margin = 0
    else:
        margin = profit / total_revenue

    if profit < 0:
        return "Loss"
    elif profit >= 0 and margin < 0.1:
        return "Low Margin"
    elif margin < 0.3:
        return "Healthy"
    else:
        return "Peak"


def label_days(day_rows):
    labels = []
    for day in day_rows:
        name = day.get("day")
        revenue = day.get("revenue", 0)
        cost = day.get("cost", 0)
        label = classify_day(revenue, cost)
        labels.append({"day": name, "label": label})
    return labels



f = classify_day(24, 67)
print(f)
