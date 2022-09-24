from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import csv

urls = ['https://mediakit.iportal.ru/our-team#team#!/tab/219191124-1',
        'https://mediakit.iportal.ru/our-team#team#!/tab/219191124-2',
        'https://mediakit.iportal.ru/our-team#team#!/tab/219191124-3']

# Соединяем имя сотрудника с его должностью и почтой
def join_elements(arr):
    d1 = arr[::2]
    d2 = arr[1::2]
    return list(zip(d1, d2))

# Соединяем города с сотрудниками
def join_cities_and_employee(cities, emp_l, emp_r):
    d1 = cities[::2] # Нечет
    d2 = cities[1::2] # Чет
    return list(zip(d1, emp_l)), list(zip(d2, emp_r))

# Получаем текстовые значения по каждому сотруднику
def get_emloyee(object):
    arr = []
    for i in range(len(object)):
        if object[i].text != '':
            arr.append(object[i].text)
    return join_elements(arr)

# Получение массива с данными по каждому сотруднику
def get_data(arr):
    new_arr = []
    for i in arr:
        city = i[0]
        if '@' not in i[1][0]:
            name = i[1][0]
            data = i[1][1].split('\n')
            position = data[0]
            if len(data)==2:
                mail = data[1]
            else: mail = data[2]
        else:
            name = i[1][1]
            data = i[1][0].split('\n')
            position = data[0]
            if len(data) == 2:
                mail = data[1]
            else:
                mail = data[2]
        new_arr.append([city, name, position, mail])
    return new_arr

# Получение массива с данными по каждому руководящему сотруднику
def get_boss_data(bosses):
    new_data = []
    for i in bosses:
        arr = i.text.split('\n')
        len_arr = len(arr)
        if len_arr == 4:
            new_data.append(['', arr[0], arr[1], arr[3]])
        if len_arr == 2:
            new_data.append(['', arr[0], arr[1], ''])
    return new_data

# Запись в csv
def write_file(arr):
    with open('employees.csv', 'a', encoding='UTF8') as f:
        writer = csv.writer(f)
        for i in arr:
            writer.writerow(i)
    f.close()

def run_driver(url, driver):
    driver.get(url)
    driver.refresh()
    time.sleep(2)

def parser(driver):
# РЯДОВЫЕ СОТРУДНИКИ
    # Парсим города
    cities = driver.find_elements(By.XPATH, "//div[@style='line-height: 56px;']")
    arr_cities = [i.text for i in cities if i.text != '']

    # Парсим сотрудников
    right_block = driver.find_elements(By.XPATH,"//div[(@data-field-left-value='880' or @data-field-left-value='891' or @data-field-left-value='882') and @data-field-width-value='300']")
    left_block = driver.find_elements(By.XPATH,"//div[@data-field-left-value='280' and @data-field-width-value='300']")

    time.sleep(2)

    right_arr = get_emloyee(right_block)
    left_arr = get_emloyee(left_block)

    arr_l, arr_r = join_cities_and_employee(arr_cities, left_arr, right_arr)
    data = get_data(arr_l + arr_r)

# РУКОВОДЯЩИЕ ДОЛЖНОСТИ
    bosses = driver.find_elements(By.XPATH,"//div[contains(@class, 't544__content') or contains(@class, 't527__wrapperleft')]")
    data_bosses = get_boss_data(bosses)

    return data+data_bosses

def start():
    driver = webdriver.Chrome()
    for url in urls:
        try:
            run_driver(url, driver)
            # Парсинг
            data = parser(driver)
            # Запись в файл
            write_file(data)
        except Exception as ex:
            print(ex)
    driver.close()
    driver.quit()

start()
