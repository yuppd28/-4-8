import simpy
import random
import matplotlib.pyplot as plt
import datetime


# Параметри системи
arrival_rate = 2  # Лямбда (інтенсивність надходження)
service_rate = 1/5  # частота обслуговування
max_wait = 5 # максимальний час очікуввання
entity_out = 0
N_entity = 0
#N_entity = 1000 # кількість сутностей

# Список для збереження даних
waiting_times = [] # час очікування
servicing_times = [] # час обслуговування
all_times= [] # час в системі
length_queue = [] # довжина черги
length_system = [] # кількість сутностей в системі
time_stamps = []  # Часові відмітки для графіка
rejected_calls=[] # відмова в обслуговуванні

def format_time(minutes):
    hours = int(minutes // 60)
    mins = int(minutes % 60)
    return f"{hours:02d}:{mins:02d}"

def get_arrival_rate(current_minute):
    hour = int(current_minute / 60) % 24
    #hour=env.now/60
    if 0<=hour<6:
        return 8/60
    elif 6<=hour<8:
        return 18/60
    elif 8<=hour<11:
        return 25/60
    elif 11<=hour<13:
        return 40/60
    elif 13<=hour<14:
        return 50/60
    elif 14<=hour<17:
        return 40/60 
    elif 17<=hour<22:
        return 30/60
    else:       
        return 10/60
server=None
server_capacity = 2    
def adjust_servers(env):
    #nonlocal server, server_capacity
    global server, server_capacity
    while True:
        current_hour = env.now / 60  # час у годинах
        if 0 <= current_hour <= 6:
            new_capacity = 1  # ранкова зміна
        else: 
            if 10 <= current_hour <= 14 or 17 <= current_hour<=21:
               new_capacity = 11  # денні зміни
            else:
                new_capacity = 3
        if new_capacity != server_capacity:
            print(f"[{format_time(env.now)}] Зміна кількості серверів: {server_capacity} → {new_capacity}")
            server_capacity = new_capacity
            server = simpy.Resource(env, capacity=server_capacity)           
        yield env.timeout(15)            

# Функція для моделювання однієї сутності
def entity(env, name, server):
   global N_entity
   arrival_time = env.now # час прибуття сутності до системи
   N_entity +=1
   print(f"Сутність {name} прибула в {format_time(arrival_time)} ")
 
 
   with server.request() as request: # створення події запиту на ресурс
       global entity_out 
       result = yield env.timeout(max_wait) | request

       if request not in result:
            # Відмова через перевищення часу очікування
            print(f"{name} не дочекався  пішов в  {format_time(env.now)} (чекав {env.now - arrival_time:.2f} хв)")
            entity_out +=1
            rejected_calls.append(name)
            return       

       yield request     # очікування доступу до ресурсу
       wait_time = env.now - arrival_time # визначення часу очікування
       waiting_times.append(wait_time)
       print(f"Сутність {name} обробляється в {format_time(env.now)}, очікувала {wait_time:.2f} хвилин, серверів {server.capacity:.2f}")
        
       # Час обробки
       service_time = random.expovariate(service_rate) # визначення часу обробки сутності
       yield env.timeout(service_time) # затримка часу на обслуговування
       servicing_times.append(service_time) # збирання даних про час обслуговування
       all_time=env.now-arrival_time # визначення загального часу перебування системі
       all_times.append(all_time) # збирання даних про загальний час перебування в системі
       print(f"Сутність {name} завершила обробку в {format_time(env.now)}, час обробки {service_time:.2f} хвилин.")
       length_system.append(len(server.queue)) # визначення довжини черги
       time_stamps.append(env.now/60)
       if len(server.queue)==0:
            length_queue.append(len(server.queue))
       else:
            length_queue.append(len(server.queue)-server_capacity)    



    
        
# Функція для генерації прибуттів сутностей
def arrival_generator(env):
    entity_id = 0 # початкове значення лічильника кількостей сутностей
    
   
    while True:
        arrival_rate = get_arrival_rate(env.now)  
        interval = random.expovariate(arrival_rate)
        print(f"Генерація {arrival_rate:.2f} ")
        yield env.timeout(interval)  
        #yield env.timeout(random.expovariate(arrival_rate)) # затримка часу в симуляції (визначення часу, коли прибуває наступна сутність)
        entity_id += 1
        env.process(entity(env, entity_id, server))  # ініціалізація функції для генерації процесу обслуговування

# Моделювання

env = simpy.Environment()  #Створення середовища
server = simpy.Resource(env, capacity=server_capacity)  # ресурс з одним сервером для обробки сутності
env.process(arrival_generator(env)) # ініціалізація функції для генерації прибуттів сутностей 
env.process(adjust_servers(env)) 
env.run(until=24*60)


# Аналіз результатів
print("\n--- Результати моделювання ---")
average_waiting_time = sum(waiting_times) / len(waiting_times) if waiting_times else 0
print(f"Середній час очікування сутності: {average_waiting_time:.2f} хвилин")
average_servicing_time = sum(servicing_times) / len(servicing_times) if servicing_times else 0
print(f"Середній час обробки сутності: {average_servicing_time:.2f} хвилин")
average_all_time = sum(all_times) / len(all_times) if all_times else 0
print(f"Середній час перебування в системі сутності: {average_all_time:.2f} хвилин")
average_length_queue = sum(length_queue) / len(length_queue) if length_queue else 0
print(f"Середня довжина черги: {average_length_queue:.2f} ")
average_length_system = sum(length_system) / len(length_system) if length_system else 0
print(f"Середня кількість сутностей в системі: {average_length_system:.2f} ")
print(f"Кількість втрачених дзвінків: {entity_out:.2f} ")
print(f"Кількість вcсього дзвінків: {N_entity:.2f} ")




#Побудова графіка довжини черги
plt.figure(figsize=(10, 5))
plt.plot(time_stamps, length_queue, label='Довжина черги')
plt.xlabel('Час ([години])')
plt.ylabel('Довжина черги')
plt.title('Зміна довжини черги')
plt.legend()
plt.grid()
plt.show()
