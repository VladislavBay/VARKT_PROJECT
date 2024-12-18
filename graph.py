import numpy as npimport matplotlib.pyplot as plt

# Константы
H = 5000  # мF_1 = 1428 * 1000  # Н
F_0 = 324 * 1000   # Нd_F = F_1 - F_0
m_0 = 53 * 10**3n = 39.77      # кг
g = 9.8beta_1 = np.pi / (9 * 135)
beta_2 = 7 * np.pi / (18 * 150)  # м/с²p_0 = 1  # начальное давление

# Давление как функция времени
p = lambda t: p_0 * np.exp(-g * t**2 / (2 * H))

# Временные интервалыt_1 = np.linspace(0, 135, 1000)  # для x_1, y_1
t_2 = np.linspace(0, 150, 1000)  # для x_2, y_2

# Ускорение для первого участкаdef acceleration_1(t):
    F = F_1 + d_F * p(t)    a_x = 0 if t <= 30 else (F * np.cos(np.pi / 2 - beta_1 * t)) / (m_0 - n * t)
    a_y = (F if t <= 30 else (F * np.sin(np.pi / 2 - beta_1 * t))) / (m_0 - n * t) - g    return a_x, a_y
m_01 = m_0 - n * 135
phi_1 = np.pi / 2 - beta_1 * 135

# Ускорение для второго участкаdef acceleration_2(t):
    F = F_0 + d_F * p(t)    a_x = (F * np.cos(phi_1 - beta_2 * t)) / (m_01 - n * t)
    a_y = (F * np.sin(phi_1 - beta_2 * t)) / (m_01 - n * t) - g    return a_x, a_y

# Численное интегрирование для первого участка
x_1, y_1 = [0], [0]v_x1, v_y1 = 0, 0
dt_1 = t_1[1] - t_1[0]
for t in t_1:
    a_x, a_y = acceleration_1(t)    v_x1 += a_x * dt_1
    v_y1 += a_y * dt_1    x_1.append(x_1[-1] + v_x1 * dt_1)
    y_1.append(y_1[-1] + v_y1 * dt_1)

# Убираем первый элемент (дублирование начальных значений)x_1, y_1 = x_1[1:], y_1[1:]
# Численное интегрирование для второго участка
x_2, y_2 = [x_1[-1]], [y_1[-1]]
v_x2, v_y2 = v_x1, v_y1  # начальные скорости из конца первого участкаdt_2 = t_2[1] - t_2[0]
for t in t_2:
    a_x, a_y = acceleration_2(t)    v_x2 += a_x * dt_2
    v_y2 += a_y * dt_2    x_2.append(x_2[-1] + v_x2 * dt_2)
    y_2.append(y_2[-1] + v_y2 * dt_2)

# Построение общего графикаplt.figure(figsize=(12, 8))  # Увеличенный масштаб графика
plt.plot(np.array(x_1) / 1000, np.array(y_1) / 1000, label='$y_1(x_1)$', color='blue')  # Конвертация в километрыplt.plot(np.array(x_2) / 1000, np.array(y_2) / 1000, label='$y_2(x_2)$', color='red')  # Конвертация в километры
plt.xlabel('$x$ (км)', fontsize=14)plt.ylabel('$y$ (км)', fontsize=14)
plt.title('График зависимости $y$ от $x$', fontsize=16)plt.xlim(-50, max(np.array(x_2) / 1000) - 150)  # Увеличенные пределы для оси x
plt.ylim(-50, max(np.array(y_2) / 1000) - 150)  # Увеличенные пределы для оси yplt.legend(fontsize=12)
plt.grid()plt.show()
