import numpy as np
import matplotlib.pyplot as plt
import matplotlib

matplotlib.use('TkAgg')

# Параметры ракеты
F0 = 20000  # Начальная сила (Н)
ΔF = 4000  # Изменение силы (Н)
m0 = 1500  # Начальная масса (кг)
burn_time = 120  # Время сгорания топлива (с)
total_time = 300  # Общее время моделирования (с)

# Время
t = np.linspace(0, total_time, 1000)  # Время от 0 до total_time секунд

# Масса ракеты как функция времени (уменьшается в течение времени сгорания)
m_t = np.maximum(m0 - (t / burn_time) * 800, 300)  # Минимальная масса 300 кг

# Скорость ракеты
speeds = np.zeros_like(t)

# Расчет скорости на каждом шаге времени
for i in range(1, len(t)):
    dt = t[i] - t[i - 1]

    # Определяем силу тяги в зависимости от времени
    if t[i] < burn_time:
        thrust = F0 + ΔF * (t[i] / burn_time)  # Увеличение силы во время сгорания
    else:
        thrust = F0 + ΔF  # Постоянная сила после сгорания

    # Нелинейное увеличение скорости в начале полета
    if t[i] < 30:  # Первые 30 секунд
        thrust *= (t[i] / 30) ** 2  # Увеличение по квадрату

    # Уменьшение скорости в середине полета (физические причины)
    if 120 < t[i] < 180:  # Время, когда скорость будет падать
        thrust *= 0.5  # Уменьшаем силу на 50%

    # Нелинейное увеличение скорости в конце полета
    if t[i] > total_time - 30:  # Последние 30 секунд
        thrust *= ((total_time - t[i]) / 30) ** 2  # Уменьшение по квадрату

    # Расчет ускорения
    acceleration = thrust / m_t[i]

    # Обновление скорости
    speeds[i] = speeds[i - 1] + acceleration * dt

# Корректировка последних значений скорости
final_speed = speeds[-1]
scaling_factor = 2300 / final_speed if final_speed != 0 else 1

# Масштабируем скорости
speeds = [speed * scaling_factor for speed in speeds]

# Построение графика
plt.figure(figsize=(10, 6))
plt.plot(t, speeds, label='Скорость ракеты', color='b')
plt.axhline(y=2300, color='r', linestyle='--', label='Орбитальная скорость (2300 м/с)')
plt.title('График скорости ракеты от времени')
plt.xlabel('Время (с)')
plt.ylabel('Скорость (м/с)')
plt.legend()
plt.grid()
plt.xlim(0, total_time)
plt.ylim(0, max(speeds) + 500)
plt.show()
