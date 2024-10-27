from celery import Celery
import random
from datetime import datetime, timedelta

celery = Celery('tasks', broker='redis://localhost:6379/0')

servers = [
    {"id": 1, "capacity": 100, "efficiency": 0.8},
    {"id": 2, "capacity": 150, "efficiency": 0.7},
    {"id": 3, "capacity": 200, "efficiency": 0.9},
]

@celery.task
def generate_usage_data():
    current_time = datetime.now()
    data = []
    for server in servers:
        usage = random.randint(0, server["capacity"])
        data.append({
            "server_id": server["id"],
            "timestamp": current_time.isoformat(),
            "usage": usage,
            "energy_consumption": usage / server["efficiency"]
        })
    return data

@celery.task
def optimize_load(total_load):
    optimized_distribution = []
    remaining_load = total_load

    sorted_servers = sorted(servers, key=lambda x: x["efficiency"], reverse=True)

    for server in sorted_servers:
        if remaining_load > 0:
            allocated_load = min(remaining_load, server["capacity"])
            optimized_distribution.append({
                "server_id": server["id"],
                "allocated_load": allocated_load,
                "energy_consumption": allocated_load / server["efficiency"]
            })
            remaining_load -= allocated_load
        else:
            optimized_distribution.append({
                "server_id": server["id"],
                "allocated_load": 0,
                "energy_consumption": 0
            })

    return optimized_distribution