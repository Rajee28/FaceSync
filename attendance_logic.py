<<<<<<< HEAD
from datetime import datetime, time, timedelta
import config


def check_in_status(punch_time, current_counters):
    """
    Determine status and updates for counters based on In-Punch time.

    Args:
        punch_time (datetime.time): The time of punch in.
        current_counters (dict): {'grace': int, 'late': int, 'permission': int}

    Returns:
        dict: {
            'status': str,
            'updates': {'grace': int, 'late': int, 'permission': int} (deltas)
        }
    """
    updates = {"grace": 0, "late": 0, "permission": 0}
    status = "Present"

    # Parse times from config
    time_start = time.fromisoformat(config.TIME_START)
    time_grace_end = time.fromisoformat(config.TIME_GRACE_END)
    time_late_end = time.fromisoformat(config.TIME_LATE_END)
    time_permission_end = time.fromisoformat(config.TIME_PERMISSION_END)
    time_halfday_fn_end = time.fromisoformat(config.TIME_HALFDAY_FN_END)

    # 7:00 - 8:00
    if time_start <= punch_time <= time(8, 0):
        status = "Present"

    # 8:01 - 8:05 (Grace)
    elif time(8, 1) <= punch_time <= time_grace_end:
        if current_counters["grace"] < config.MAX_GRACE:
            updates["grace"] = 1
            status = "Present (Grace)"
        else:
            # Grace exhausted -> Late
            if current_counters["late"] < config.MAX_LATE:
                updates["late"] = 1
                status = "Late"
            else:
                # Late exhausted -> Permission
                if current_counters["permission"] < config.MAX_PERMISSION:
                    updates["permission"] = 1
                    status = "Permission"
                else:
                    status = "Half Day Leave - Forenoon"

    # 8:06 - 8:10 (Late)
    elif time(8, 6) <= punch_time <= time_late_end:
        if current_counters["late"] < config.MAX_LATE:
            updates["late"] = 1
            status = "Late"
        else:
            if current_counters["permission"] < config.MAX_PERMISSION:
                updates["permission"] = 1
                status = "Permission"
            else:
                status = "Half Day Leave - Forenoon"

    # 8:11 - 9:00 (Permission)
    elif time(8, 11) <= punch_time <= time_permission_end:
        if current_counters["permission"] < config.MAX_PERMISSION:
            updates["permission"] = 1
            status = "Permission"
        else:
            status = "Half Day Leave - Forenoon"

    # 9:01 - 10:30 (Half Day FN)
    elif time(9, 1) <= punch_time <= time_halfday_fn_end:
        status = "Half Day Leave - Forenoon"

    else:
        # After 10:30 AM
        status = "Half Day Leave - Forenoon"  # Or Full Day Absent based on context, but usually leads to loss of FN.

    return {"status": status, "updates": updates}


def check_out_status(punch_time):
    """
    Determine status based on Out-Punch time.
    """
    time_halfday_an_end = time.fromisoformat(config.TIME_HALFDAY_AN_END)

    # 10:30 AM - 12:29 PM
    if time(10, 30) <= punch_time <= time_halfday_an_end:
        return "Half Day Leave - Afternoon"

    # 12:30 PM - 3:00 PM
    elif (
        time(12, 30) <= punch_time
    ):  # No upper bound specified strictly, assuming <= End of day operation
        return "Present"

    return "Early Leave"
=======
from datetime import datetime, time, timedelta
import config


def check_in_status(punch_time, current_counters):
    """
    Determine status and updates for counters based on In-Punch time.

    Args:
        punch_time (datetime.time): The time of punch in.
        current_counters (dict): {'grace': int, 'late': int, 'permission': int}

    Returns:
        dict: {
            'status': str,
            'updates': {'grace': int, 'late': int, 'permission': int} (deltas)
        }
    """
    updates = {"grace": 0, "late": 0, "permission": 0}
    status = "Present"

    # Parse times from config
    time_start = time.fromisoformat(config.TIME_START)
    time_grace_end = time.fromisoformat(config.TIME_GRACE_END)
    time_late_end = time.fromisoformat(config.TIME_LATE_END)
    time_permission_end = time.fromisoformat(config.TIME_PERMISSION_END)
    time_halfday_fn_end = time.fromisoformat(config.TIME_HALFDAY_FN_END)

    # 7:00 - 8:00
    if time_start <= punch_time <= time(8, 0):
        status = "Present"

    # 8:01 - 8:05 (Grace)
    elif time(8, 1) <= punch_time <= time_grace_end:
        if current_counters["grace"] < config.MAX_GRACE:
            updates["grace"] = 1
            status = "Present (Grace)"
        else:
            # Grace exhausted -> Late
            if current_counters["late"] < config.MAX_LATE:
                updates["late"] = 1
                status = "Late"
            else:
                # Late exhausted -> Permission
                if current_counters["permission"] < config.MAX_PERMISSION:
                    updates["permission"] = 1
                    status = "Permission"
                else:
                    status = "Half Day Leave - Forenoon"

    # 8:06 - 8:10 (Late)
    elif time(8, 6) <= punch_time <= time_late_end:
        if current_counters["late"] < config.MAX_LATE:
            updates["late"] = 1
            status = "Late"
        else:
            if current_counters["permission"] < config.MAX_PERMISSION:
                updates["permission"] = 1
                status = "Permission"
            else:
                status = "Half Day Leave - Forenoon"

    # 8:11 - 9:00 (Permission)
    elif time(8, 11) <= punch_time <= time_permission_end:
        if current_counters["permission"] < config.MAX_PERMISSION:
            updates["permission"] = 1
            status = "Permission"
        else:
            status = "Half Day Leave - Forenoon"

    # 9:01 - 10:30 (Half Day FN)
    elif time(9, 1) <= punch_time <= time_halfday_fn_end:
        status = "Half Day Leave - Forenoon"

    else:
        # After 10:30 AM
        status = "Half Day Leave - Forenoon"  # Or Full Day Absent based on context, but usually leads to loss of FN.

    return {"status": status, "updates": updates}


def check_out_status(punch_time):
    """
    Determine status based on Out-Punch time.
    """
    time_halfday_an_end = time.fromisoformat(config.TIME_HALFDAY_AN_END)

    # 10:30 AM - 12:29 PM
    if time(10, 30) <= punch_time <= time_halfday_an_end:
        return "Half Day Leave - Afternoon"

    # 12:30 PM - 3:00 PM
    elif (
        time(12, 30) <= punch_time
    ):  # No upper bound specified strictly, assuming <= End of day operation
        return "Present"

    return "Early Leave"
>>>>>>> f56354bff23c57e9dbb309990488effecb6c4ad5
