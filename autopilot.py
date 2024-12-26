import matplotlib.pyplot as plt
import numpy as np
import krpc
import time

speed_data = []
high_data = []
mass_data = []
time_data = []

def main():

    conn = krpc.connect(name="My project")

    # Получение доступа к важным объектам и функциям
    vessel = conn.space_center.active_vessel
    ap = vessel.auto_pilot
    control = vessel.control
    initial_propellant_mass = vessel.mass

    # Создание полезных переменных потока
    altitude = conn.add_stream(getattr, vessel.flight(), "mean_altitude")
    apoapsis = conn.add_stream(getattr, vessel.orbit, "apoapsis_altitude")
    periapsis = conn.add_stream(getattr, vessel.orbit, "periapsis_altitude")
    surface_velocity_stream = conn.add_stream(
        getattr, vessel.flight(vessel.orbit.body.reference_frame), "velocity"
    )

    # Получение объекта топливного бака
    fuel_tank = vessel.parts.with_tag("fuel")[0]

    # Получение объекта ресурса LiquidFuel
    liquid_fuel_resource = fuel_tank.resources.with_resource("LiquidFuel")[0]

    # Данные для создания графиков

    # Функция вывода информации в терминал
    def print_logs(mass, curr_speed, seconds):
        print(f"*Данные на {seconds} секундах*")
        print(f"Текущая скорость ступенчатой ракеты: {curr_speed} м/с")
        print("Расстояние от Земли:", round(altitude(), 3), "м")
        print(f"Масса ракеты: {mass} кг\n")

    def get_logs(ideal, distance, mass, curr_time):
        speed_data.append(ideal)
        high_data.append(distance)
        mass_data.append(mass)
        time_data.append(curr_time)

    # Активация двигателя
    control.throttle = 1
    control.sas = True

    print("Запуск двигателей прошел успешно, полет через:")
    time.sleep(1)
    print("3...")
    time.sleep(1)
    print("2...")
    time.sleep(1)
    print("1...")
    control.activate_next_stage()

    timing = time.time()

    print("\n*Данные на 0 минуте*")
    print(f"Текущая скорость ступенчатой ракеты: {0} м/с")
    print("Расстояние от Земли:", round(altitude(), 3), "м")
    print(f"Масса ракеты на момент старта составляет: {vessel.mass}\n")
    times = 0
    changed = 0

    get_logs(0, round(altitude()), vessel.mass, 0)

    # Основной цикл полета
    while True:
        seconds = round(time.time() - timing)
        # Скорость ракеты
        surface_velocity = surface_velocity_stream()
        surface_speed = (surface_velocity[0] ** 2 + surface_velocity[1] ** 2 + surface_velocity[2] ** 2) ** 0.5

        get_logs(surface_speed, round(altitude()), vessel.mass, seconds)

        # Печать информации на определенных интервалах
        if 13 <= seconds <= 17:
            if times == 0:
                times += 1
                print_logs(vessel.mass, surface_speed, seconds)

        if 500 <= surface_speed <= 550:
            if times == 1 and (30 <= seconds <= 38):
                times += 1
                print_logs(vessel.mass, surface_speed, seconds)
                print("*уменьшение тяги до 55%*\n")
            control.throttle = 0.55

        elif 30000 <= altitude() <= 50000 and changed < 1:
            print("*достижение высоты в 30.000 метров*")
            print("*изменение угла наклона*\n")
            vessel.control.pitch = -1
            time.sleep(4.0)
            vessel.control.pitch = 0
            changed += 1

        elif (times == 2) and (58 <= seconds <= 62):
            times += 1
            print_logs(vessel.mass, surface_speed, seconds)

        elif (times == 3) and (88 <= seconds <= 250):
            times += 1
            print_logs(vessel.mass, surface_speed, seconds)

        elif 50500 <= altitude() <= 60000:
            vessel.control.pitch = 0
            control.sas = True

        elif altitude() >= 60500 or liquid_fuel_resource.amount < 7:
            break

    # Извлечение данных после завершения полета
    print("Выход в космос прошел успешно!")
    print("*отделение первой ступени*")
    control.activate_next_stage()

    # Изменение тангажа ракеты к внутреннему радиальному вектору
    print("*изменение угла наклона к внутреннему радиальному вектору*")
    control.sas = True
    vessel.control.pitch = -1
    time.sleep(5.0)
    vessel.control.pitch = 0

    # Ожидание выхода на орбиту
    print("\nРакета идет к орбите")

    seconds = round(time.time() - timing)
    surface_velocity = surface_velocity_stream()
    surface_speed = (surface_velocity[0] ** 2 + surface_velocity[1] ** 2 + surface_velocity[2] ** 2) ** 0.5

    get_logs(surface_speed, round(altitude()), vessel.mass, seconds)



    while True:
        seconds = round(time.time() - timing)
        surface_velocity = surface_velocity_stream()
        surface_speed = (surface_velocity[0] ** 2 + surface_velocity[1] ** 2 + surface_velocity[2] ** 2) ** 0.5

        get_logs(surface_speed, round(altitude()), vessel.mass, seconds)
        apoapsis_value = apoapsis()
        periapsis_value = periapsis()
        #time.sleep(0.1)
        if (850000 <= apoapsis_value) and (90000 <= periapsis_value):
            print("*отключение двигателей*")
            control.sas = False
            vessel.control.pitch = 0.05
            time.sleep(0.1)
            vessel.control.pitch = 0
            control.sas = True
            control.throttle = 0
            break

    print("*ракета вышла на орбиту*")
    # Выпуск спутника на орбиту
    time.sleep(5)
    control.activate_next_stage()
    print("*отделение спутника от ракетоносителя 1 ЭТАП*")
    time.sleep(5)
    control.activate_next_stage()
    print("*вывод антенн*")
    time.sleep(5)
    control.antennas = True

    print("Спутник успешно вышел на орбиту!")

    # Добавление 20 секунд после отделения спутника
    post_separation_time = 20  # Время в секундах
    final_time = time_data[-1] + post_separation_time

    for t in range(1, post_separation_time + 1):
        time_data.append(time_data[-1] + 1)
        speed_data.append(speed_data[-1])  # Скорость не изменяется
        high_data.append(high_data[-1])  # Высота не изменяется
        mass_data.append(mass_data[-1])  # Масса остается постоянной

    # Построение графиков
    x = np.linspace(0, final_time, len(time_data))  # Общее значение X для всех графиков
    y1 = mass_data  # Первый график: масса
    y2 = speed_data  # Второй график: скорость
    y3 = high_data # Третий график: высота

# Создание фигуры и осей
#fig, axs = plt.subplots(3, 1, figsize=(10, 15))

# Первый график

if __name__ == "__main__":
    main()

# Показ графиков
#plt.show()
