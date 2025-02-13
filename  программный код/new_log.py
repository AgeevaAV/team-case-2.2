'''
АННОТАЦИЯ

Последний актуальный скрипт.

Описание:
    На ардуино отсылается то, что должно. Всё остальное работает в штатном режиме, добавлены все константы

Настроить:
    Коэффициенты  "PID'a"

Осталось:
    Добавить цикл, связанный с gpio
    Событие достижения конца пути

'''


import serial
import time
import RPi.GPIO as GPIO
import time

# разрешение 640 х 480

# time.sleep(20)


port = '/dev/Buzina_Nano'  # поменять
baudrate = 115200  # поменять
# 1 - правый поворот, 2 - левый поворот, 3 - объезд, 4 - разворот, 5 - поворот с объездом справа, 6 - поворот с объездом слева, 7 - проехать и остановиться
function_to_move = 0
function_to_grab = 0  # 1 - схватить, 2 - переставить, 3 - переставить с грузом на борту
correction_speed_to_right_wheels = 0
correction_speed_to_left_wheels = 0
# на каком расстояни роботот должен остановиться, что бы схватить цилиндр с небольшим допуском, поменять!
max_distance_for_color_obj = 31
# Для ПДа
pred_norm_x = 0
# массив сохраняющий путь пройденный роботом

black_objects_roi = []
color_objects_central = []
matrix = []
id_matrix = ''


# считывает скорость для моторов


def go_to_line(black_objects_roi):
    global pred_norm_x, correction_speed_to_left_wheels, correction_speed_to_right_wheels, corect_flag
    if len(black_objects_roi) == 1:
        x = black_objects_roi[0][3]
        width = black_objects_roi[0][1]
        norm_x = black_objects_roi[0][5]
    else:
        obj = min(black_objects_roi, key=lambda x: (x[3])**2 + (x[4])**2)
        x = obj[3]
        norm_x = obj[5]
        width = obj[1]
        if norm_x > 0.1:
            corect_flag = 1

    Kp = 1.0
    Kd = 0.3
    if width < 150:
        if (norm_x > 0 and pred_norm_x < 0) or (norm_x < 0 and pred_norm_x > 0):
            pred_norm_x = 0

        if x > 0:
            correction_speed_to_left_wheels = round(
                norm_x * Kp - (pred_norm_x - norm_x) * Kd, 3)
        if x < 0:
            n_norm_x = abs(norm_x)
            pred_norm_x = abs(pred_norm_x)
            correction_speed_to_right_wheels = round(
                n_norm_x * Kp - (pred_norm_x - norm_x) * Kd, 3)

    pred_norm_x = norm_x


pred_norm_x_roi = 0


def corection_way():
    global pred_norm_x_roi
    limit = 0.04
    if black_objects_roi != []:

        if len(black_objects_roi) == 1:
            x_cor = black_objects_roi[0][5]
        elif len(black_objects_roi) > 1:
            print('FOR MISTAKE:', black_objects_roi, len(black_objects_roi))
            obj = min(black_objects_roi, key=lambda x: (x[3])**2 + (x[4])**2)
            x_cor = obj[5]

        if -limit <= x_cor <= limit:
            return 0

        else:
            correction_speed_to_right_wheels = x_cor
            correction_speed_to_left_wheels = 0
            function_to_move = 11
            function_to_grab = 0

            data_to_arduino = "$" + str(function_to_move) + ";" + str(function_to_grab) + ";" + \
                str(correction_speed_to_right_wheels) + ";" + \
                str(correction_speed_to_left_wheels) + ";#"

            ser.write(data_to_arduino.encode('utf-8'))
            print(f'Message sent to serial: {data_to_arduino}')

            pred_norm_x_roi = x_cor

            return 1
    else:
        if pred_norm_x_roi != 0:
            correction_speed_to_right_wheels = pred_norm_x_roi
        else:
            correction_speed_to_right_wheels = -1
        correction_speed_to_left_wheels = 0
        function_to_move = 11
        function_to_grab = 0

        data_to_arduino = "$" + str(function_to_move) + ";" + str(function_to_grab) + ";" + \
            str(correction_speed_to_right_wheels) + ";" + \
            str(correction_speed_to_left_wheels) + ";#"

        ser.write(data_to_arduino.encode('utf-8'))
        print(f'Message sent to serial: {data_to_arduino}')

# прописать функции!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


pred_shape = 0


def recognize_shape(id_matrix, color1):
    global function_to_move, function_to_grab, do_color, state_flag, count, pred_shape
    dead_end = ['1111011111110111100111011', '1111011111111111001110011', '1111111111101111011110111', '1111111111111111110111101', '1111111111111111111011100', '1111111111111111100111001', '1111111111111111001110011', '1111111111111111111011110', '1111011111111111100111001', '1111111111111111110011101', '1111111111110111101111011', '1111011111110111101111011', '1111011111101111011110111', '1111111111111111101111011', '1111111111111111110011100', '1111111111111011110111101', '0011110100000001011110111', '0111100100000010011110111', '1011110110000001011110011', '1111000110100001111011101', '1110000100000001110011101', '1100111001000001110111101', '1110001100000001110011101', '1111000010100001111011110', '1101111011000000101111011', '0011100100000000011110111', '1001110011000001101111011', '0111101000000010011110111',
                '1101111011000001101111011', '1111000110100001111011110', '1101111010000001101111011', '0111100100000000011110111', '1111001110000001110011101', '1011110000000001001110011', '0111101000000010111100111', '0011110100000000011110111', '0111101000000010111101111', '1111110010110001111011110', '1110111001000001110111101', '0111101100000010011110111', '1101111011000000100111011', '1111000110000001110011100', '1111010010100001111011110', '1011110100000001011110111', '1110111101000001110111101', '1111000110000001111011100', '0111101000000110111101111', '1100111001000001100111001', '1101111000000001101111011', '1001110011000001001111011', '1101111011000001100111011', '1101111001000001101111011', '1011110110000001011110111', '1111000100000001110011100', '1110101101000001110111101', '1111010010110001111011110']

    platform = ['1101100011000110000110111', '1111110000100001000011001', '1111110001000010000110011', '1101110001100011000111011', '1110110001100011000111011', '1101100011000010000110011', '1101100011000110001110111', '1111110001100011000111011', '1000110001100011000011011', '1111111000110001100011100', '1101111000110001100011100', '1110110001100011000111011', '1101110000100001000011000', '1111110001100001000011001', '1101100001000010000110011', '1111111000110001000011100', '1100110001100011000011011', '1000110001100001000011011', '1111100111000110001100111',
                '1000110001100011000111011', '1100110001100011000111011', '1000110001100011000011001', '1101100011000010000100011', '1101100011000110000100011', '1111110001100011000111001', '1111100011000110001100111', '1101111000110001000011000', '1111110000100001000011001', '1111100001000010000110011', '1101110001000010000110011', '1111111100110001100011100', '1111110001100011000011001', '1111110001100011000111011', '1111110001100010000110011', '1111110001000010000110011', '1111110001100011000110001', '1101100011000110001100111', '1000110000100001100111011', '1111111000110001000011000']

    left_turn = ['1111111111001110011100111', '1111101111000011110111001', '1111111111000011100111001', '1111101111000011100111001', '1111111111001110011110011', '1111111111000111001110011', '1111111111000110001111011', '1111111111000111001111011', '1111111111001110001110011',
                 '1111100111000011110111101', '1111100111000011100111001', '1111111111011110111100111', '1111111111001110011110111', '1111111111011110111101111', '1111111111011110011100111', '1111100111000011110111001', '1111111111000110001110011', '1111111111000111101111011', '1111111111001111001110011']
    right_turn = ['1111111111100001001110011', '1111111111111001110011101', '1111111111110001000111011', '1111111111110001100111011', '1111111111111001100011001', '1111111111110001000010011',
                  '1111111111110001100011011', '1111111111100001011110111', '1111111111111001110011001', '1111111111111001110011100', '1111111111110001000110011', '1111111111110001100011001', '1111111111100001001110111']
    right_E_crossroad = ['0111101000000110111100111', '1101111011110001101111011', '1110111101111001100111001', '1101111011110001101111001', '1111011100111001110011101', '0111101000000110111101111', '1110111001110001100111001', '1011110000100001011110011', '0111100000100111011110111', '1110111101111001110111001', '1011110100100001011110111', '1111011110111101111001110', '1101111011110001100111011', '1110011100111001110011101', '0111110000100011011110111', '0111101000000110011110111', '1100111001110001100111001', '1101111001110001100111001', '1011110100100011011110111', '0111101000000110011100111', '1101111011110001100011011', '1111110000100011011110111', '1101111000110001101110011',
                         '1111011110111101110011100', '1111010000001110111101111', '1111111110111101111011110', '1101111000110001001110011', '0111101000000111011110111', '1011110000100001001110011', '1111111111111101111001110', '1110010001001111111101111', '1110111101111001110011101', '0111101000100111011110111', '1011110000100011011110111', '1111111111111111111011110', '1111011110111101111011110', '1111111111111111111001110', '0111100000000110011100111', '0111001000000110111101111', '1111011110111101111011100', '0111100000100011011110111', '1111010001001110111101111', '1111000000001110111101111', '1101111000110001101111011', '1101111010110001101111011', '1110111101111001110111101', '1011110000100001011110111']

    left_E_crossroad = ['1001111011000111001111011', '1011110111001110011110111', '1101111011000111100111001', '1110001100000001110111101', '0111101111001110011100111', '1101111011000111101111011', '1100111001000011100111001', '1011110111000111001110011', '0111101111011110011100111', '1011110111001111001110011', '1110111001000011100111001', '1110000100100001110011100', '1001110011100110001110011', '1101111011110110001111011', '1011110111001110001110011', '1001110011000110001111011', '1011110111001111011110011', '1101111011000110001111011', '1001110011000111101111011', '1111000100100001110011100',
                        '1111000110100001110011100', '0111101111001110011110111', '0011110111001110011110111', '1001110011000111001111011', '0111101111011110111100111', '1011110011000111001110011', '1011110011001110001110011', '1001110011000111001110011', '1110001100000001110011101', '1110000100000001110011101', '1101111011000111001111011', '1101111011100110001111011', '1001110011100110001111011', '1101111001000111001111011', '0011100111001110011110111', '1011110111001111011110111', '1110111101000011110111101', '1110001100000011110111101', '1101110011100110001111011', '1101110011000110001110011', '1001110011000110001110011']
    T_crossroad = ['1111110000000110111101111', '1111100111000001110111101', '1111100111100001110011100', '1111101111000001100111001', '0010000001111001111011111', '1111111111000001110111101', '1111010000000110111101111', '1111111000000001011110111', '0011100001110001111011110', '1111111110000001101111011', '1111101111000001110111101', '1111111110000001001110011', '1111100011100001111011100', '1111111111000001100111001', '1111111100000001001110011', '0111100011100001111011100', '1111110000000001101111011', '1111100011110001111011110', '1111111100000001101111011', '1111111000000110011100111', '1111100111000001100111001', '1111111100000001001111011',
                   '1111111111000001001111011', '1111100111100001110011101', '1111111111000001101111011', '1111100011100001110011101', '1111111000000001101111011', '1111100000000001101111011', '1111100011100001110011100', '0011100001111001111011111', '1111100011000001110111101', '1111111000000010011110111', '1111011000000110111101111', '0011100001111001111011110', '0111100011110001111011110', '0111100001100001111011100', '0011000001111001111011111', '1111111000000011011110111', '1111100011100001111011110', '1111111000000110011110111', '1111111000000001001110011', '1111111100000001011110011', '0111100001110001111011110', '1111111000000110111100111']

    X_crossroad = ['0011110100000001011110111', '0111100100000010011110111', '1011110110000001011110011', '1111000110100001111011101', '1110000100000001110011101', '1100111001000001110111101', '1110001100000001110011101', '1111000010100001111011110', '1101111011000000101111011', '0011100100000000011110111', '1001110011000001101111011', '0111101000000010011110111', '1101111011000001101111011', '1111000110100001111011110', '1101111010000001101111011', '0111100100000000011110111', '1111001110000001110011101', '1011110000000001001110011', '0111101000000010111100111', '0011110100000000011110111',
                   '0111101000000010111101111', '1111110010110001111011110', '1110111001000001110111101', '0111101100000010011110111', '1101111011000000100111011', '1111000110000001110011100', '1111010010100001111011110', '1011110100000001011110111', '1110111101000001110111101', '1111000110000001111011100', '0111101000000110111101111', '1100111001000001100111001', '1101111000000001101111011', '1001110011000001001111011', '1101111011000001100111011', '1101111001000001101111011', '1011110110000001011110111', '1111000100000001110011100', '1110101101000001110111101', '1111010010110001111011110']

    shape = 0
    for i in dead_end:
        if id_matrix == i:
            shape = 'dead_end'

    for i in platform:
        if id_matrix == i:
            shape = 'platform'

    for i in right_turn:
        if id_matrix == i:
            shape = 'right_turn'

    for i in left_turn:
        if id_matrix == i:
            shape = 'left_turn'

    for i in right_E_crossroad:
        if id_matrix == i:
            shape = 'right_E_crossroad'

    for i in left_E_crossroad:
        if id_matrix == i:
            shape = 'left_E_crossroad'

    for i in T_crossroad:
        if id_matrix == i:
            shape = 'T_crossroad'

    for i in X_crossroad:
        if id_matrix == i:
            shape = 'X_crossroad'

    if color1 == 'Green' and do_color:
        function_to_grab = 1
        flag_back = 1
        count_E_crosses = 0
        count_T_crosses = 0
        count_X_crosses = 0
    elif color1 == 'Blue' and do_color:
        if flag_back == 0:
            function_to_grab = 2
        if flag_back == 1:
            function_to_grab = 3
    elif color1 == 'Red' and (shape == 'dead_end' or shape == 'line'):
        function_to_move = 3
    elif shape == 'platform' and color1 != 'Green':
        function_to_move = 7
        state_flag = 1
        count = 1
        time.sleep(10)
    elif shape == 'dead_end':
        function_to_move = 4
    elif shape == 'right_turn':
        function_to_move = 1
    elif shape == 'left_turn':
        function_to_move = 2
    elif shape == 'right_E_crossroad':
        if pred_shape != 'right_E_crossroad':
            count_E_crosses += 1
        if flag_back == 0 and count_E_crosses == 2:
            function_to_move = 1
    elif shape == 'left_E_crossroad':
        pass
    elif shape == 'T_crossroad':
        if pred_shape != 'T_crossroad':
            count_T_crosses += 1
        if flag_back == 1 and count_T_crosses == 1:
            function_to_move = 1
        elif flag_back == 1 and count_T_crosses == 2:
            function_to_move = 2
    elif shape == 'X_crossroad':
        if pred_shape != 'X_crossroad':
            count_X_crosses += 1
        if flag_back == 1 and count_X_crosses == 1:
            function_to_move = 2

    pred_shape = shape


def recognize_color(color_objects):
    cylinder = min(color_objects, key=lambda x: (x[3])**2 + (x[4])**2)
    color = cylinder[0]
    if color == 'Green':
        return 'Green'
    elif color == 'Blue':
        return 'Blue'
    elif color == 'Red':
        return 'Red'


def read_fifo():
    global id_matrix

    lines = fifo.readlines()
    if len(lines) > 1:
        line = lines[-1]
    else:
        line = []

    if len(line) != 0:
        now = line.split(";")
        now.pop()
        l = 0
        k_roi = 0
        for i in now:
            obj = i.split(",")
            first = obj.pop(0)
            if first == 'Black_roi':
                black_objects_roi.append(
                    [first] + [float(j) for j in obj])
                black_objects_roi[k_roi][4] = - \
                    black_objects_roi[k_roi][4] + 240
                black_objects_roi[k_roi][3] = black_objects_roi[k_roi][3] - 320
                k_roi += 1
            if first == 'Matrix':
                id_matrix = "".join(obj)
                for j in obj:
                    stroka = []
                    for a in j:
                        a_int = int(a)
                        stroka.append(a_int)
                    matrix.append(stroka)
            else:
                color_objects.append([first] + [float(j) for j in obj])
                color_objects[l][4] = -color_objects[l][4] + 240
                color_objects[l][3] = color_objects[l][3] - 320
                l += 1


fifo_path = 'fifo'
fifo = open(fifo_path, 'r')

GPIO.setmode(GPIO.BCM)  # Используем BCM нумерацию
# Устанавливаем GPIO 17 как вход
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
set_mus = set()
mes_time = 0
mes_delay = 0

count_crosses = 0
count_E_crosses = 0
count_T_crosses = 0
count_X_crosses = 0

flag_back = 0
state_flag = 0
count = 0

corect_flag = 0
wait_flag = 0

shape = 0
time_send_messege = 0

try:
    # Открываем COM-порт
    ser = serial.Serial(port, baudrate)
    print("Соединение с Arduino установлено.")
    time.sleep(2)

    # Небольшая задержка для установления соединения
    time.sleep(2)

    while True:
        input_state = GPIO.input(17)  # Читаем состояние GPIO 17

        if input_state == GPIO.LOW and count == 1:
            state_flag = 0
            count = 0
            print('Ожидание сигнала...\n')

        if input_state == GPIO.HIGH and state_flag == 0:
            while True:

                input_state = GPIO.input(17)
                if input_state == GPIO.LOW:
                    state_flag = 1
                    count = 1
                    break

                function_to_move = 0
                function_to_grab = 0
                correction_speed_to_right_wheels = 0
                correction_speed_to_left_wheels = 0
                black_objects_roi = []
                color_objects = []
                matrix = []
                id_matrix = 0

                # получение данных с камеры
                read_fifo()
                time.sleep(0.1)

                print('Matrix:')
                print(id_matrix)
                for h in matrix:
                    print(h)

                set_mus.add(id_matrix)

                # получение сообщения с ардуино ¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬
                if ser.in_waiting > 0:
                    data_from_arduino = ser.readline()
                    data_from_arduino = data_from_arduino.decode(
                        'utf-8').strip()
                    print(f'Message get from serial: {data_from_arduino}')
                else:
                    print('No data from Arduino')
                    data_from_arduino = 10000

                serial_data = ser.in_waiting
                if serial_data > 0:
                    print('Were still data', serial_data)
                    r = ser.read_all()

                try:
                    if 0 < float(data_from_arduino) <= max_distance_for_color_obj:
                        do_color = 1
                    else:
                        do_color = 0
                except ValueError:
                    print('Uncorrect messege or text messege')

                # конец блок получения сообщения с ардуино ¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬

                # ПДи
                if corect_flag == 0 and wait_flag == 0:
                    if black_objects_roi != []:
                        go_to_line(black_objects_roi)

                # блок логики ¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬

                if corect_flag == 0 and wait_flag == 0:
                    if color_objects != []:
                        color = recognize_color(color_objects)
                    print(f'Color: {color}')

                    if id_matrix != 0:
                        shape = recognize_shape(id_matrix, color)
                    print(f'Shape: {shape}')

                    if shape != 0 and shape != 'unknown':
                        corect_flag = 1

                if corect_flag == 1 and wait_flag == 0:
                    corect_flag = corection_way()

                if corect_flag == 0 and wait_flag == 0:
                    shape = recognize_shape(id_matrix, color)

                    data_to_arduino = "$" + str(function_to_move) + ";" + str(function_to_grab) + ";" + \
                        str(correction_speed_to_right_wheels) + ";" + \
                        str(correction_speed_to_left_wheels) + ";#"
                    ser.write(data_to_arduino.encode('utf-8'))

                    print(f'Message sent to serial: {data_to_arduino}')
                    time.sleep(0.07)

                    time_send_messege = time.time()
                    wait_flag = 1

                if (data_from_arduino == 'OK' or time.time() - time_send_messege > 60) and wait_flag == 1:
                    corect_flag = 1
                    wait_flag = 0
                time.sleep(0.05)
        # Универсальная логика
                # if color == 'Green' and do_color:
                #     function_to_grab = 1
                # elif color == 'Blue' and do_color:
                #     function_to_grab = 2
                # elif color == 'Red' and shape == 'dead_end':
                #     function_to_move = 3
                #     main_way.append(3)
                # elif color == 'Red' and shape == 'right_turn':
                #     function_to_move = 5
                #     main_way.append(5)
                # elif color == 'Red' and shape == 'left_turn':
                #     function_to_move = 6
                #     main_way.append(6)
                # elif color == 'Red' and shape == 'right_T_crossroad':
                #     function_to_move = 1
                #     main_way.append(1)
                # elif shape == 'platform' and color != 'Green':
                #     function_to_move = 7
                #     main_way.append(7)
                # elif shape == 'dead_end':
                #     function_to_move = 4
                #     main_way.append(4)
                # elif shape == 'right_turn':
                #     function_to_move = 1
                #     main_way.append(1)
                # elif shape == 'left_turn':
                #     function_to_move = 2
                #     main_way.append(2)
                # elif shape == 'right_E_crossroad':
                #     function_to_move = 1
                #     main_way.append(1)
                # elif shape == 'left_E_crossroad':
                #     pass
                # elif shape == 'T_crossroad':
                #     function_to_move = 1
                #     main_way.append(1)
                # elif shape == 'X_crossroad':
                #     function_to_move = 1
                #     main_way.append(1)

                # конец блока логики ¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬


except KeyboardInterrupt:
    print("Прерывание программы. Закрытие порта...")
    print(list(set_mus))

# except Exception as e:
#    print(f'Error: {str(e)}')

finally:
    if 'ser' in locals() and ser.is_open:  # закрытие COM-port
        ser.close()
        print("Соединение закрыто.")

    fifo.close()  # Закрываем FIFO
    GPIO.cleanup()  # Очистка настроек GPIO
