activities = { }

def add_activity(name, time):
    if name in activities:
        activities[name].append(time)
    else:
        activities[name] = [time]

def get_time(name):
    if name in activities:
        return sum(activities[name])
    else:
        return "Nie ma takiej aktywności"

def get_top_activities():
    if len(activities) == 0:
        return "Brak aktywności"

    sums_per_activity = {name: sum(times) for name, times in activities.items()}

    top_activities = sorted(sums_per_activity.items(), key=lambda x: x[1], reverse=True)

    return top_activities
