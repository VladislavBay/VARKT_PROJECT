import matplotlib.pyplot as plt
import numpy as np
import krpc
import time

# Установка соединения с kRPC
connection = krpc.connect(name="Sputnik-1 launch")
vessel = connection.space_center.active_vessel
ap = vessel.auto_pilot
controls = vessel.control
initial_mass = vessel.mass

# Потоки данных
altitude_stream = connection.add_stream(getattr, vessel.flight(), "mean_altitude")
apoapsis_stream = connection.add_stream(getattr, vessel.orbit, "apoapsis_altitude")
periapsis_stream = connection.add_stream(getattr, vessel.orbit, "periapsis_altitude")
velocity_stream = connection.add_stream(getattr, vessel.flight(vessel.orbit.body.reference_frame), "velocity")

# Поиск ресурсов и частей
fuel_tank = next(part for part in vessel.parts.all if "fuel" in part.tags)
liquid_fuel = next(resource for resource in fuel_tank.resources if resource.name == "LiquidFuel")

# Инициализация данных для графиков
metrics = {
    "time": [],
    "speed": [],
    "altitude": [],
    "mass": []
}

# Функции для работы с данными
def log_data(current_time):
    velocity = velocity_stream()
    speed = np.linalg.norm(velocity)
    metrics["time"].append(current_time)
    metrics["speed"].append(speed)
    metrics["altitude"].append(altitude_stream())
    metrics["mass"].append(vessel.mass)


def display_info(stage_time):
    print(f"Time: {stage_time} sec")
    print(f"Speed: {metrics['speed'][-1]:.2f} m/s")
    print(f"Altitude: {metrics['altitude'][-1]:.2f} m")
    print(f"Mass: {metrics['mass'][-1]:.2f} kg\n")

# Начало миссии
controls.throttle = 1
controls.sas = True
print("Launching in:")
for countdown in range(3, 0, -1):
    print(countdown, "...")
    time.sleep(1)
controls.activate_next_stage()

start_time = time.time()
log_data(0)
print("\nLaunch successful!")

# Основной цикл управления полетом
pitch_adjusted = False
throttle_reduced = False
while True:
    elapsed_time = round(time.time() - start_time)
    log_data(elapsed_time)

    # Отображение данных в определенные моменты
    if elapsed_time in [15, 35, 60]:
        display_info(elapsed_time)

    # Уменьшение тяги
    if not throttle_reduced and metrics["speed"][-1] > 500:
        controls.throttle = 0.55
        print("Throttle reduced to 55%")
        throttle_reduced = True

    # Изменение угла тангажа
    if not pitch_adjusted and metrics["altitude"][-1] > 30000:
        print("Adjusting pitch for gravity turn")
        controls.pitch = -1
        time.sleep(2)
        controls.pitch = 0
        pitch_adjusted = True

    # Выход на орбиту
    if metrics["altitude"][-1] > 60000 or liquid_fuel.amount < 7:
        print("Stage separation")
        controls.activate_next_stage()
        break

# Построение графиков
fig, ax = plt.subplots(3, 1, figsize=(6, 12))

# График массы
ax[0].plot(metrics["time"], metrics["mass"], color="blue", label="Mass")
ax[0].set_title("Mass Over Time")
ax[0].set_xlabel("Time (s)")
ax[0].set_ylabel("Mass (kg)")
ax[0].legend()
ax[0].grid(True)

# График скорости
ax[1].plot(metrics["time"], metrics["speed"], color="red", label="Speed")
ax[1].set_title("Speed Over Time")
ax[1].set_xlabel("Time (s)")
ax[1].set_ylabel("Speed (m/s)")
ax[1].legend()
ax[1].grid(True)

plt.tight_layout()
plt.show()

# Построение траектории y от x
planet_radius = vessel.orbit.body.equatorial_radius
latitude_stream = connection.add_stream(getattr, vessel.flight(), "latitude")
longitude_stream = connection.add_stream(getattr, vessel.flight(), "longitude")

# Сбор данных координат
x_coords = []
y_coords = []
while metrics["altitude"][-1] < 60000:
    latitude = latitude_stream()
    longitude = longitude_stream()
    x_coords.append(planet_radius * np.radians(longitude))
    y_coords.append(planet_radius * np.radians(latitude))
    time.sleep(0.1)

# Построение графика
plt.figure(figsize=(8, 6))
plt.plot(x_coords, y_coords, color="purple", linewidth=2, label="Trajectory")
plt.title("Rocket Trajectory: y(x)")
plt.xlabel("x (km)")
plt.ylabel("y (km)")
plt.grid(True)
plt.legend()
plt.show()
