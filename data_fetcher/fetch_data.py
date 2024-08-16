import pika
import json
import time
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from webdriver_manager.firefox import GeckoDriverManager

time.sleep(10) # rabbitmq kurulana kadar executelanmasın diye bekletiyorum

def fetch_red_notices():
    firefox_options = webdriver.FirefoxOptions()
    firefox_options.add_argument("--disable-dev-shm-usage")
    firefox_options.add_argument("--no-sandbox")

    driver = webdriver.Remote(  
        command_executor=f'http://selenium:4444/wd/hub',
        options=firefox_options
    )

    unique_set = set() #set of unique ids
    red_notice_list = [] #notices list
    MAX_NOTICE = 20 # API sayfasında bulunacak maximum notice sayısı

##########################################
    def data_proc(notice):             #Bir bildirimi notice_list listesine ekleyen yardımcı bir fonksiyon.
        if notice:
            red_notice_list.append(notice)

##########################################
# PARSING
    def proc_noti(url):

        driver.get(url)
        page_source = driver.page_source
        json_start = page_source.find('{')
        json_end = page_source.rfind('}') + 1
        json_text = page_source[json_start:json_end]
        try:
            data = json.loads(json_text)
            total = int(data['total'])

            if total == 0:
                print(f"No data for URL: {url}")  
                return 0   #Hiç bildirim bulunamazsa (total == 0), bir mesaj yazdırılır ve fonksiyon 0 döner.

            notices = data['_embedded']['notices']
            for notice in notices: ######### Eğer entity_id notice_list içinde yoksa onu kaydeder
                entity_id = notice['entity_id']
                if entity_id not in unique_set:
                    unique_set.add(entity_id)
                    data_proc(notice)

            return total
        except json.JSONDecodeError:
            print("Failed to parse JSON data.")
            return 0
##########################################
    
    url = f"https://ws-public.interpol.int/notices/v1/red?resultPerPage={MAX_NOTICE}" # max_notice kadar sayfada bildiri bulundurur
    proc_noti(url)

##########################################
    driver.quit()
    return red_notice_list

def send_to_queue(red_notice_list):
    #rabbitmq bağlantısı
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='host.docker.internal')) 
    channel = connection.channel()
    channel.queue_declare(queue='interpol_notices', durable=True)

    notices_dictionary = {"notices": red_notice_list} # notice_list'i dictionary yapar
    message_body = json.dumps(notices_dictionary) # json ile okunur hale getirir

    channel.basic_publish(exchange='', routing_key='interpol_notices', body=message_body) #gönderme
    connection.close()
    print("Data sent to RabbitMQ")

while True:
    notices = fetch_red_notices()
    if notices:
        send_to_queue(notices)
    time.sleep(3600)  # her 1 saatte tekrar çalışır