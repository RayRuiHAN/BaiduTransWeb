# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
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

str_list = []
with open(raw_name, 'r', encoding='utf-8') as f:
    for line in f.readlines():
        line = ucd.normalize('NFKC', line).replace(' ', '')
        if line != '':
            str_list.append(line)
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
input("Press any to continue...")

# 声明谷歌、Firefox、Safari等浏览器
driver = webdriver.Chrome()
driver.minimize_window()
driver.get("https://fanyi.baidu.com/#jp/zh/")

sleep(1)
driver.find_element(by=By.XPATH, value='//*[@id="app-guide"]/div/div/div[2]/span').click()

df = pd.read_csv('D:/Tool Script/BaiduTransAPI/BaiduTransReplace.csv')
count = 0
for each_text in long_text:
    driver.find_element(by=By.XPATH, value='//*[@id="baidu_translate_input"]').send_keys(each_text)
    sleep(1)
    driver.find_element(by=By.XPATH, value='//*[@id="baidu_translate_input"]').send_keys(Keys.ENTER)
    sleep(5)
    # 滚动到底部
    driver.execute_script("document.documentElement.scrollTop=10000")
    sleep(2)
    driver.find_element(by=By.XPATH,
                        value='/html/body/div[1]/div[2]/div/div/div[1]/div[2]/div[1]/div[2]/div/div/div[2]/div[1]/a['
                              '1]/span').click()
    output = root.clipboard_get()
    for i in range(len(df)):
        output = output.replace(df.loc[i, 'wrong'], df.loc[i, 'right'])
    with open(output_path, 'a+', encoding='utf-8') as file1:
        print(output, file=file1)
    count += 1
    print(count, '/', total)
    driver.find_element(by=By.XPATH,
                        value='/html/body/div[1]/div[2]/div/div/div[1]/div[2]/div[1]/div[1]/div/div[2]/a').click()
    sleep(1)

print(total, " All Down. Quit in 3 Seconds...")
sleep(3)
driver.quit()
os.system('''taskkill /F /im chromedriver.exe''')
