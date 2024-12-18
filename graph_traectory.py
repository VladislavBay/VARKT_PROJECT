import numpy as np
import matplotlib.pyplot as plt

# Константы
H = 5000  # м
F_1 = 1474 * 1000  # Н
F_0 = 274 * 1000   # Н
d_F = F_1 - F_0
m_0 = 53*10**3
n = 39.77      # кг
g = 9.8
beta_1 = np.pi / (9 * 55 ** 2 ) # м/с²
beta_2 = 7 * np.pi / (18 * 95 ** 2)  # рад/с
p_0 = 1              # начальное давление

# Давление как функция времени
p = lambda t: p_0 * np.exp(-g * t ** 2 / (2 * H))

# Временные интервалы
t_1 = np.linspace(0, 55, 1000)   # для x_1, y_1
t_2 = np.linspace(55, 150, 1000)  # для x_2, y_2

# Ускорение для первого участка (30 км вертикальной траектории)
def acceleration_1(t):
    F = F_1 + (F_1 - 1320*10**3) * p(t)
    a_x = 0  # Ускорение по оси X равно 0 (движение вертикально)
    a_y = (F * np.sin(np.pi / 2 - beta_1 * t ** 2)) / (m_0 - n * t) - g  # Ускорение по оси Y
    return a_x, a_y

m_01 = m_0 - n * 55

# Ускорение для второго участка
def acceleration_2(t):
    F = F_0 + (F_0 - 307*10**3) * p(t)
    a_x = (F * np.cos(7 * np.pi / 18 - beta_2 * t ** 2)) / (m_01 - n*t)
    a_y = (F * np.sin(7 * np.pi / 18 - beta_2 * t ** 2)) / (m_01 - n*t) - g
    return a_x, a_y

# Численное интегрирование для первого участка
x_1, y_1 = [0], [0]
v_x1, v_y1 = 0, 0
dt_1 = t_1[1] - t_1[0]

# В течение первых 30 км (первые 55 секунд) движение только по вертикали
for t in t_1:
    a_x, a_y = acceleration_1(t)
    v_x1 += a_x * dt_1
    v_y1 += a_y * dt_1
    x_1.append(x_1[-1] + v_x1 * dt_1)  # x остается 0
    y_1.append(y_1[-1] + v_y1 * dt_1)

# Убираем первый элемент (дублирование начальных значений)
x_1, y_1 = x_1[1:], y_1[1:]

# Численное интегрирование для второго участка
x_2, y_2 = [x_1[-1]], [y_1[-1]]
v_x2, v_y2 = v_x1, v_y1  # начальные скорости из конца первого участка
dt_2 = t_2[1] - t_2[0]

# Для второго участка продолжаем движение ракеты
for t in t_2:
    a_x, a_y = acceleration_2(t)
    v_x2 += a_x * dt_2
    v_y2 += a_y * dt_2
    x_2.append(x_2[-1] + v_x2 * dt_2)
    y_2.append(y_2[-1] + v_y2 * dt_2)

# Построение общего графика
plt.figure(figsize=(10, 6))
plt.plot(np.array(x_1) / 1000, np.array(y_1) / 1000, label='$y_1(x_1)$', color='blue')  # Конвертация в километры
plt.plot(np.array(x_2) / 1000, np.array(y_2) / 1000, label='$y_2(x_2)$', color='red')  # Конвертация в километры
plt.xlabel('$x$ (км)')
plt.ylabel('$y$ (км)')
plt.title('График зависимости $y$ от $x$')
plt.legend()
plt.grid()
plt.show()
