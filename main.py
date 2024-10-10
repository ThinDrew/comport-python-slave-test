import serial
import struct
import time
from crc16 import get_crc16, append_crc16_to_array

# Конфигурация COM-порта (измените по необходимости)
port = "/dev/ttyS3"  # Ваш COM-порт
baudrate = 115200
parity = serial.PARITY_NONE
stopbits = serial.STOPBITS_ONE
bytesize = serial.EIGHTBITS
timeout = 1

# Создаем соединение с COM-портом
ser = serial.Serial(
    port=port,
    baudrate=baudrate,
    parity=parity,
    stopbits=stopbits,
    bytesize=bytesize,
    timeout=timeout
)

# Основной цикл чтения и ответа
try:
    print(f"Подключение к {port} открыто, ожидание данных...")
    
    while True:
        # Читаем данные из порта
        if ser.in_waiting > 0:
            request = ser.read(ser.in_waiting)  # Читаем все доступные байты
            print(f"Принято: {request.hex()}")

            # Проверяем, что сообщение достаточно длинное
            if len(request) < 4:
                print("Недостаточно данных для обработки")
                continue
            
            # Извлекаем данные из запроса
            unit_id = request[0]
            function_code = request[1]
            payload_length = request[2]
            data = request[3:3 + payload_length]
            received_crc = request[3 + payload_length:5 + payload_length]

            # Проверка контрольной суммы (CRC)
            crc = get_crc16(request)
            if crc != 0:
                print("Неверная контрольная сумма (CRC)")
                continue

            print(f"Modbus запрос: unit_id={unit_id}, function_code={function_code}, data={data.hex()}")

            # Пример обработки запроса: ответ на запрос функции 0x03 (чтение регистров)
            if function_code == 0x03:  # Функция чтения регистров
                # Пример: возвращаем одно значение 12345 (в виде одного 16-битного регистра)
                value = 12345
                response_data = struct.pack('>H', value)  # Один 16-битный регистр
                
                # Количество байт в ответе (1 байт для количества регистров + 2 байта данных)
                byte_count = len(response_data)  # Длина response_data, которая равна 2
                response = bytes([unit_id, function_code, byte_count]) + response_data
                response = append_crc16_to_array(response)  # Добавляем CRC
                
                ser.write(response)  # Отправка ответа
                print(f"Отправлено: {response.hex()}")


except KeyboardInterrupt:
    print("Программа завершена.")
finally:
    ser.close()
    print(f"Соединение с {port} закрыто.")