import matplotlib.pyplot as plt
import numpy as np
import time

# Импорт функций физической модели
from graph import solve_ivp, equations, R

# Импорт автопилота
from autopilot import main as run_autopilot, time_data, mass_data, speed_data, high_data

# Выполняем автопилот
run_autopilot()

# Данные из физической модели
t_eval = np.linspace(0, 220, 1000)
solution = solve_ivp(equations, (0, 220), [0, R, 0, 0, np.radians(90)], t_eval=t_eval)
time_phys = solution.t
x, y, vx, vy, _ = solution.y
mass_phys = [equations(t, state)[-1] for t, state in zip(time_phys, solution.y.T)]
speed_phys = np.sqrt(vx**2 + vy**2)
height_phys = (y - R) / 1000

# Данные из автопилота
time_auto = time_data
mass_auto = mass_data
speed_auto = speed_data
height_auto = [h / 1000 for h in high_data]

# Построение графиков
fig, axs = plt.subplots(3, 1, figsize=(10, 15))

# График скорости
axs[1].plot(time_phys, speed_phys, label="Физическая модель", color="red")
axs[1].plot(time_auto, speed_auto, label="Автопилот", color="blue", linewidth=2)
#axs[1].set_title("График скорости")
axs[1].set_xlabel("Время (с)")
axs[1].set_ylabel("Скорость (м/с)")
axs[1].legend()
axs[1].grid()

# График высоты
axs[2].plot(time_phys, height_phys, label="Физическая модель", color="green")
axs[2].plot(time_auto, height_auto, label="Автопилот", color="violet", linewidth=2)
#axs[2].set_title("График высоты")
axs[2].set_xlabel("Время (с)")
axs[2].set_ylabel("Высота (км)")
axs[2].legend()
axs[2].grid()

plt.tight_layout()
plt.show()