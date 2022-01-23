import time
import datetime
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import queue
import threading
import PySimpleGUI as sg

def get_data():
    global data_list
    data = open('data.txt', 'rt')
    data_list = data.read().split(",")

def get_page(username, password):
        global browser
        chrome_options = Options()
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--headless')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        browser = webdriver.Chrome(data_list[0], options=chrome_options)
        del_cookies()
        browser.get('https://ehall.jlu.edu.cn')
        try:
            browser.find_element_by_id('username').clear()
            browser.find_element_by_id('password').clear()
            browser.find_element_by_id('username').send_keys(username)
            browser.find_element_by_id('password').send_keys(password)
            browser.find_element_by_id('login-submit').click()
        except:
            pass
        
def morning_sign_in():
    flag = False
    global browser
    a = 0
    while flag is not True:
        try:
            browser.get('https://ehall.jlu.edu.cn/infoplus/form/BKSMRDK/start')
            time.sleep(20 + 5*a)
            browser.switch_to.frame(0)
            time.sleep(1 + 0.5*a)
            browser.find_element_by_xpath('//input[@value="我同意"]').click()
            time.sleep(1 + 0.5*a)
            browser.switch_to.default_content()
            js = 'document.getElementsByClassName("infoplus_radioLabel")[4].click()'
            browser.execute_script(js)
            js = 'document.getElementsByClassName("command_button_content")[0].click()'
            browser.execute_script(js)
            time.sleep(1 + 0.5*a)
            js = 'document.getElementsByClassName("dialog_button default fr")[0].click()'
            browser.execute_script(js)
            time.sleep(1 + 0.5*a)
            js = 'document.getElementsByClassName("dialog_button default fr")[0].click()'
            browser.execute_script(js)
            flag = True
        except:
            a += 1
            if a > 2:
                raise Exception

def night_sign_in():
    flag = False
    global browser
    a = 0
    while flag is not True:
        try:
            browser.get('https://ehall.jlu.edu.cn/infoplus/form/BKSMRDK/start')
            time.sleep(3 + 0.5*a)
            js = 'document.getElementsByClassName("command_button_content")[0].click()'
            browser.execute_script(js)
            time.sleep(1 + 0.5*a)
            js = 'document.getElementsByClassName("dialog_button default fr")[0].click()'
            browser.execute_script(js)
            time.sleep(1 + 0.5*a)
            js = 'document.getElementsByClassName("dialog_button default fr")[0].click()'
            browser.execute_script(js)
            flag = True
        except:
            a += 1
            if a > 2:
                raise Exception

def return_text():
    global browser
    try:
        time.sleep(5)
        serial_number = browser.find_element_by_class_name('form_top_description').text
        status = browser.find_element_by_class_name('form_top_t').text
        time_text = browser.find_element_by_class_name('form_remark_title').text
        print(serial_number)
        print(status)
        print(time_text)
    except:
        print('打卡成功，但返回信息失败')
        
def del_cookies():
    global browser
    try:
        browser.delete_all_cookies()
    except:
        pass
    
def main_thread(gui_queue):
    global flag
    get_data()
    username = data_list[1]
    password = data_list[2]
    print('自动打卡已部署！')
    while flag is True:
        time_now = datetime.datetime.now()
        if 6 <= time_now.hour < 12:
            print('打卡中，预计需要25秒...')
            try:
                get_page(username, password)
                morning_sign_in()
                return_text()
                browser.quit()
                print(time.ctime())
                print('==========================================')
                time_next = time_now + datetime.timedelta(hours =+ 12)
                time_delta = (time_next - time_now).total_seconds()
                time.sleep(time_delta)
            except:
                browser.quit()
                del_cookies()
                print('打卡失败')
        elif 21 <= time_now.hour < 24:
            print('打卡中，预计需要10秒...')
            try:
                get_page(username, password)
                night_sign_in()
                return_text()
                browser.quit()
                print(time.ctime())
                print('==========================================')
                time_next = time_now + datetime.timedelta(hours =+ 12)
                time_delta = (time_next - time_now).total_seconds()
                time.sleep(time_delta)
            except:
                browser.quit()
                del_cookies()
                print('打卡失败')
        else:
            time.sleep(3600)
    try:
        browser.quit()
    except:
        pass
    sys.exit(0)
    
def the_gui():
    global flag
    gui_queue = queue.Queue()
    layout = [[sg.Text('控制台')],
              [sg.Output(size=(70, 12))],
              [sg.Button('启动'),sg.Button('退出')]]
    sg.set_options(element_padding=(0, 0))
    window = sg.Window('自动定时打卡').Layout(layout)
    while True:
        event, values = window.Read(timeout=100)
        if event is None or event == '退出':
            flag = False
            break
        elif event == '启动':
            for key, state in {'启动': True, '退出': False}.items():
                window[key].update(disabled=state)
                flag = True
            threading.Thread(target=main_thread, args=(gui_queue,), daemon=True).start()
    window.Close()

if __name__ == '__main__':
    the_gui()
