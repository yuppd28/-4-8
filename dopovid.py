import simpy
import random
import matplotlib.pyplot as plt

# Параметри системи
service_rate = 1 / 300  # обслуговування в секундах (5 хв)
max_wait = 300  # максимум очікування (сек)
entity_out = 0 # Лічильник втрачених дзвінків
N_entity = 0  # Загальна кількість дзвінків

# Статистика
waiting_times = [] # Час очікування в черзі
servicing_times = []  # Час обслуговування
all_times = []           # Повний час у системі
length_queue = []        # Довжина черги
length_system = []       # Кількість дзвінків у системі
rejected_calls = []      # Список відхилених дзвінків
time_stamps = []         # Часові мітки

# Форматування часу для виводу в консоль (год:хв:сек)
def format_hms(seconds):
    hours = int(seconds // 3600)
    mins = int((seconds % 3600) % 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{mins:02d}:{secs:02d}"
# Залежність інтенсивності дзвінків від часу доби (секунди -> годинник)
def format_mins_secs(seconds):
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins} хв {secs} сек"

def get_arrival_rate(current_second):
    hour = int(current_second / 3600) % 24
    if 0 <= hour < 6:
        return 8 / 3600
    elif 6 <= hour < 8:
        return 18 / 3600
    elif 8 <= hour < 11:
        return 25 / 3600
    elif 11 <= hour < 13:
        return 40 / 3600
    elif 13 <= hour < 14:
        return 50 / 3600
    elif 14 <= hour < 17:
        return 40 / 3600
    elif 17 <= hour < 22:
        return 30 / 3600
    else:
        return 10 / 3600

server = None
server_capacity = 2
# Динамічна зміна кількості операторів у залежності від часу доби
def adjust_servers(env):
    global server, server_capacity
    while True:
        current_hour = env.now / 3600
        if 0 <= current_hour <= 6:
            new_capacity = 1
        elif 10 <= current_hour <= 14 or 17 <= current_hour <= 21:
            new_capacity = 11
        else:
            new_capacity = 3
        if new_capacity != server_capacity:
            print(f"[{format_hms(env.now)}] Зміна кількості серверів: {server_capacity} → {new_capacity}")
            server_capacity = new_capacity
            server = simpy.Resource(env, capacity=server_capacity)
        yield env.timeout(900)  # кожні 15 хв
# Обробка дзвінка
def entity(env, name, server):
    global N_entity, entity_out
    arrival_time = env.now
    N_entity += 1
    print(f"Дзвінок {name} прибув в {format_hms(arrival_time)}")

    with server.request() as request:
        result = yield env.timeout(max_wait) | request

        if request not in result:
            print(f"{name} не дочекався, пішов в {format_hms(env.now)} (чекав {format_mins_secs(env.now - arrival_time)})")
            entity_out += 1
            rejected_calls.append(name)
            return

        yield request
        wait_time = env.now - arrival_time
        waiting_times.append(wait_time)
        print(f"Дзвінок {name} обробляється в {format_hms(env.now)}, очікував {format_mins_secs(wait_time)}, операторів: {server.capacity}")

        service_time = random.expovariate(service_rate)
        yield env.timeout(service_time)
        servicing_times.append(service_time)
        total_time = env.now - arrival_time
        all_times.append(total_time)
        print(f"Дзвінок {name} завершився в {format_hms(env.now)}, обробка тривала {format_mins_secs(service_time)}")

        length_system.append(len(server.queue))
        time_stamps.append(env.now / 3600)  # час у годинах
        length_queue.append(int(max(len(server.queue) - server.capacity, 0)))

def arrival_generator(env):
    entity_id = 0
    while True:
        rate = get_arrival_rate(env.now)
        interval = random.expovariate(rate)
        yield env.timeout(interval)
        entity_id += 1
        env.process(entity(env, entity_id, server))

# Генерація дзвінків
env = simpy.Environment()
server = simpy.Resource(env, capacity=server_capacity)
env.process(arrival_generator(env))
env.process(adjust_servers(env))
env.run(until=24 * 60 * 60)

# Результати
print("\n--- Результати моделювання ---")
def safe_avg(data): return sum(data) / len(data) if data else 0
print(f"Середній час очікування: {format_mins_secs(safe_avg(waiting_times))}")
print(f"Середній час обробки: {format_mins_secs(safe_avg(servicing_times))}")
print(f"Середній час у системі: {format_mins_secs(safe_avg(all_times))}")
print(f"Середня довжина черги: {safe_avg(length_queue):.2f}")
print(f"Середня кількість у системі: {safe_avg(length_system):.2f}")
print(f"Втрачені дзвінки: {entity_out}")
print(f"Усього дзвінків: {N_entity}")

# Графік (X — цілі години)
plt.figure(figsize=(12, 6))
plt.plot(time_stamps, length_queue, label='Довжина черги')
plt.xlabel('Час (години)')
plt.ylabel('Довжина черги')
plt.title('Зміна довжини черги протягом доби')
plt.grid(True)
plt.xticks(range(0, 25))  # тільки цілі години
plt.legend()
plt.tight_layout()
plt.show()
