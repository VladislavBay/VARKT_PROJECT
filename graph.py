import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

# Константы Кербина
R = 600000  # Радиус Кербина (м)
M = 5.2915158e22  # Масса Кербина (кг)
G = 6.67430e-11  # Гравитационная постоянная (м^3/кг/с^2)
g0 = 9.81  # Ускорение свободного падения (м/с^2)
H = 5000  # Высота масштаба атмосферы (м)
p0 = 1.225  # Плотность воздуха на уровне моря (кг/м^3)

# Ракетные параметры
T_stage1 = 1404000  # Тяга первой ступени (Н)
T_stage2 = 328000  # Тяга второй ступени (Н)
Isp1 = 293  # Удельный импульс первой ступени (с)
Isp2 = 298  # Удельный импульс второй ступени (с)
m0 = 53000  # Начальная масса ракеты (кг)
m_stage1 = 32000  # Масса первой ступени (кг)
Cd = 0.2  # Коэффициент лобового сопротивления
A = 42  # Площадь поперечного сечения ракеты (м^2)
alpha = np.radians(0.0184)  # Угловое ускорение (рад/км)

# Высоты событий
stage_separation_height = 60500  # Высота отделения первой ступени (м)
start_pitch_over_height = 30000  # Высота начала изменения угла (м)

# Орбитальные параметры
apoapsis_target = 930000  # Апоцентр орбиты (м)

# Функции
def rho(h):
    """Плотность атмосферы."""
    return p0 * np.exp(-h / H)

def g(h):
    """Ускорение свободного падения."""
    return G * M / (R + h)**2

def thrust(h):
    """Тяга ракеты."""
    return T_stage1 if h < stage_separation_height else T_stage2

def mass(t, h):
    if h < stage_separation_height:
        mdot = T_stage1 / (Isp1 * g0)
        m = m0 - mdot * t
    else:
        time_after_stage2_separation = t - (stage_separation_height / (T_stage1 / (Isp1 * g0)))
        mdot = T_stage2 / (Isp2 * g0)
        m = m0 - m_stage1 - mdot * time_after_stage2_separation
    print(f"Mass: {m}, Thrust: {thrust(h)}")  # Вывод для диагностики
    return m

def equations(t, state):
    """Система уравнений."""
    x, y, vx, vy, theta = state
    v = np.sqrt(vx**2 + vy**2)
    h = y - R

    if h < 0:
        h = 0

    m = mass(t, h)
    if m <= 0:
        return [0, 0, 0, 0, 0]

    T = thrust(h)
    if h >= 9000:
       T *= 0.78
    if v >= 2500:
        T = 0
        C_d = 0
    alpha_s = h * alpha
    if h >= start_pitch_over_height:
        theta = max(theta - alpha_s, 0)

    # Вывод для диагностики
    print(f"Time: {t}, h: {h}, m: {m}, Thrust: {T}, Speed: {v}")

    ax = (T * np.cos(theta) - 0.5 * Cd * rho(h) * A * vx**2) / m
    ay = (T * np.sin(theta) - 0.5 * Cd * rho(h) * A * vy**2) / m - g(h)

    return [vx, vy, ax, ay, -alpha if theta > 0 else 0]

# Начальные условия
x0, y0 = 0, R
vx0, vy0 = 0, 0
theta0 = np.radians(90)
state0 = [x0, y0, vx0, vy0, theta0]

# Решение системы
t_span = (0, 260)
t_eval = np.linspace(t_span[0], t_span[1], 1000)

def terminate_event(t, state):
    h = state[1] - R
    return h - apoapsis_target
terminate_event.terminal = True
terminate_event.direction = 1

solution = solve_ivp(equations, t_span, state0, t_eval=t_eval, events=terminate_event)

# Результаты
t = solution.t
x, y, vx, vy, theta = solution.y

# Графики
plt.figure(figsize=(10, 6))
plt.plot(x / 1000, (y - R) / 1000, label="Траектория")
plt.xlabel("Горизонтальное расстояние (км)")
plt.ylabel("Высота (км)")
plt.legend()
plt.grid()
#plt.show()

# График высоты от времени
plt.figure(figsize=(10, 6))
plt.plot(t, (y - R) / 1000, label="Высота от времени", color="blue", linewidth=2)
plt.xlabel("Время (с)")
plt.ylabel("Высота (км)")
plt.title("График высоты от времени")
plt.legend()
plt.grid()
plt.show()

speed = np.sqrt(vx**2 + vy**2)  # Общая скорость в каждый момент времени

plt.figure(figsize=(10, 6))
plt.plot(t, speed, label="Скорость от времени", color="green", linewidth=2)
plt.xlabel("Время (с)")
plt.ylabel("Скорость (м/с)")
plt.title("График общей скорости от времени")
plt.legend()
plt.grid()
plt.show()
