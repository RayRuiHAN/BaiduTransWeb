# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from retrying import retry
from time import sleep
import os
import unicodedata as ucd
import pandas as pd
import tkinter as tk

root = tk.Tk()
root.withdraw()  # to hide the window
os.system('chcp 65001')

raw = input("The name of raw txt: ")
raw_name = raw + '.txt'
output = raw + '\n'
output_path = raw + '_zh.txt'
page = int(input("Continued Page (default 1): "))

# 声明谷歌浏览器，打开特定语言翻译网址
driver = webdriver.Chrome()
driver.minimize_window()
driver.get("https://fanyi.baidu.com/#jp/zh/")

# 关闭广告
sleep(1)
driver.find_element(by=By.XPATH, value='//*[@id="app-guide"]/div/div/div[2]/span').click()
sleep(2)

# 以UTF8按行读取源文本，清洗
str_list = []
with open(raw_name, 'r', encoding='utf-8') as f:
    for line in f.readlines():
        line = ucd.normalize('NFKC', line).replace(' ', '')
        if line != '':
            str_list.append(line)

# 以2500字符上限以及换行符作为分割条件
short_text = ''
long_text = []
total = 0
for i in range(len(str_list)):
    short_text = short_text + str_list[i] + '\n'
    if (len(short_text) > 2500) | (i == len(str_list) - 1):
        long_text.append(short_text)
        total += 1
        short_text = ''
print("Total quest number is ", total)

df = pd.read_csv('D:/Tool Script/BaiduTransAPI/BaiduTransReplace.csv')
count = page - 1

# 对选定范围的分割后文段进行处理
for j in range(count, len(long_text)):
    each_text = long_text[j]

    try:
        driver.find_element(by=By.XPATH, value='//*[@id="baidu_translate_input"]').send_keys(each_text)
        driver.find_element(by=By.XPATH, value='//*[@id="baidu_translate_input"]').send_keys(Keys.ENTER)
    except NoSuchElementException as error:
        print("Input Retrying...")
        sleep(3)
        driver.find_element(by=By.XPATH, value='//*[@id="baidu_translate_input"]').send_keys(each_text)
        driver.find_element(by=By.XPATH, value='//*[@id="baidu_translate_input"]').send_keys(Keys.ENTER)

    # 复制按钮出现作为翻译结束标志
    @retry(stop_max_delay=30000)
    def copy_button():
        sleep(2)
        driver.find_element(by=By.XPATH, value='//*[@id="main-outer"]/div/div/div[1]/div[2]/div[1]/div['
                                               '2]/div/div/div[2]/div[1]/a[1]/span')
        pass


    copy_button()
    # 翻译结果中仅提取目标语言翻译文本（位置列表）
    txt_list = driver.find_elements(by=By.XPATH, value='//*[@id="main-outer"]/div/div/div[1]/div[2]/div[1]/div['
                                                       '2]/div/div/div[1]/p[@class="ordinary-output target-output '
                                                       'clearfix"]')
    # 由位置列表生成文本
    sr = ''
    for item in range(len(txt_list)):
        sr = sr + txt_list[item].text + '\n'
    output = sr[:-1]

    # 使用自定义词典对翻译结果纠错
    for i in range(len(df)):
        output = output.replace(df.loc[i, 'wrong'], df.loc[i, 'right'])

    # 将该段翻译结果写入文件（可读写状态）
    with open(output_path, 'a+', encoding='utf-8') as file1:
        print(output, file=file1)

    # 抛出完成计数
    count += 1
    print(count, '/', total)

    # 清空输入区
    driver.find_element(by=By.XPATH,
                        value='/html/body/div[1]/div[2]/div/div/div[1]/div[2]/div[1]/div[1]/div/div[2]/a').click()
    sleep(1)

print(total, " All Down. Quit in 3 Seconds...")
sleep(3)
driver.quit()
os.system('''taskkill /F /im chromedriver.exe''')
