`Interpol Red Notices Web App`

Bu proje, Interpol'ün Kırmızı Bülten verilerini çeker, bu verileri bir SQLite veritabanına kaydeder ve web sunucusu üzerinden görüntüler. Proje, veri çekme ve web sunucusu bileşenlerinin eşzamanlı çalışabilmesi için RabbitMQ kullanır. Docker ile de containerlara ayrılır.

## Proje Bileşenleri

1. **RabbitMQ**
2. **SQLite Veritabanı**
3. **Flask Web Sunucusu**
4. **Docker**
5. **Selenium(Seleniarm)** 

## Docker ile Yapılanlar
Bu proje, Docker kullanılarak aşağıdaki adımlar gerçekleştirilmiştir:

1. __Servislerin Ayrılması__: Proje bileşenleri (RabbitMQ, Selenium, veri çekme servisi, ve Flask web sunucusu) ayrı Docker containerlara yerleştirildi. Bu, her bir bileşenin bağımsız olarak çalışmasını ve yönetilmesini sağladı.<br><br>
2. __Bağımlılıkların Yalıtılması__: Her servis için gerekli olan bağımlılıklar Dockerfile'lar aracılığıyla yalıtıldı ve sadece gerekli bağımlılıkların yüklü olduğu bir çalışma ortamı sağlandı.<br><br>
3. __Ağ Yapılandırması__: docker-compose, servislerin birbirleriyle haberleşmesini sağlamak için ağ yapılandırması gerçekleştirdi. Örneğin, veri çekme servisi ve web sunucusu, RabbitMQ kuyruğuna erişmek için rabbitmq ismini kullanabilir.<br><br>

## Neden Selenium
- Interpol, belirli API'lar sunmadığı veya API'lar veri çekme gereksinimlerinizi karşılamadığı için, web sayfasındaki içerikleri almak ve bu içerikleri işlemek amacıyla Selenium kullanıldı. Selenium, web tarayıcısı otomasyonu sağlayarak sayfa içeriğini tarayıcı üzerinden işleyip, gerekli verileri çekmeye olanak tanıdı.<br><br>

1. **Web Scraping İçin Otomasyon**: Selenium, web sayfalarını otomatik olarak tarayarak dinamik içerikleri almaya olanak tanıdı. Interpol'ün Kırmızı Bülten verilerini çekerken sayfa yüklemeleri ve kullanıcı etkileşimleri gibi işlemleri simüle etmek için Selenium kullanıldı.<br><br>
2. **Çoklu Tarayıcı Desteği**: Docker container'ları içinde farklı tarayıcıları (örneğin, Chrome veya Firefox) çalıştırmak, web scraping işlemlerine olanak sağladı<br><br>
3. **Kolay Kurulum ve Dağıtım**: Selenium'u Docker içinde çalıştırmak, Selenium'un gerekli tüm bağımlılıklarıyla birlikte yüklü olduğu bir ortam sağladı. Bu, projenin farklı sistemlerde tutarlı bir şekilde çalışmasını sağladı.<br><br>

4. **Bağımlılıkların Yalıtılması**: Selenium'un bir Docker container'ında çalıştırılması, projenin diğer bileşenlerinden (örneğin, Flask web server ve RabbitMQ) izole edilmesini sağladı. Bağımlılıkların çakışmasını önledi.<br><br>
## Dosya Yapısı

- `fetch_notices.py`: Interpol API'sinden veri çeker ve RabbitMQ kuyruğuna kaydeder.<br><br>
        **fetch_red_notices()**: Interpol kırmızı bültenlerini çeker ve bu verileri işler.<br><br>
            ---- __process_data(notice)__: Bir bildirimi notice_list listesine ekleyen yardımcı bir fonksiyondur.<br><br>
            ---- __process_notices(url)__: Belirtilen URL'yi ziyaret eder ve sayfadaki JSON verisini işler. Veriler çözüldükten sonra, her bir bülten benzersiz kimliğine (entity_id) göre unique_ids  listesinde kontrol edilir ve kaydedilir.<br><br>
        ---- **send_to_queue(notice_list)**: Alınan veriyi RabbitMQ kuyruğuna gönderir.

- `web_server.py`: Flask uygulaması olup, SQLite veritabını yoksa oluşturur, veritabanından verileri okuyup web sayfasında sunar. <br><br>
    ---- **init_db()**: SQLite veritabanını başlatır ve notices tablosunu oluşturur.<br><br>
    ---- **save_notice_to_db(notice)**: RabbitMQ'dan alınan bildirimleri veritabanına kaydeder.<br><br>
    ---- **consume_from_queue()**: RabbitMQ kuyruğundan veri tüketir ve bu verileri veritabanına kaydeder.<br><br>
    ---- **index()**: Ana sayfa rotası, veritabanındaki tüm bildirimleri görüntüler.<br><br>
    ---- **search()**: Kullanıcının yaptığı aramaya göre bildirimleri arar ve sonuçları gösterir.<br><br>

- `requirements.txt`: Projenin çalışması için gereken Python bağımlılıklarını listeler.


## Gereksinimler

Proje çalıştırılmadan önce aşağıdaki yazılımların kurulu olduğundan emin olun:

- Python 3.x
- RabbitMQ Sunucusu
- SQLite 
- pip 
- Selenium
- webdriver-manager
- pika
- Flask
- Docker

## Kurulum

1. **Depoyu Klonlayın**

2. **Aşağıdaki docker komutu ile kodu çalıştırın**
    - `docker-compose up --build`

3. **Proje Servisleri**
    - __RabbitMQ__: RabbitMQ kuyruğunu oluşturur ve mesaj alışverişini yönetir.
    - __Selenium__: Interpol web sitesinden veri çekmek için kullanılır.
    - __Veri Çekme Servisi__: Interpol Kırmızı Bülten verilerini çeker ve kuyruğa ekler.
    - __Flask Web Sunucusu__: Web üzerinden kullanıcıya veritabanındaki verileri sunar.

