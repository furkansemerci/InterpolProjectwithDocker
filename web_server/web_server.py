import pika
import time
import sqlite3
import json
from flask import Flask, render_template, request
import threading

time.sleep(10) # rabbitmq kurulana kadar bekletme

nationalities_map = {"AF": "Afghanistan", "AX": "Aland Islands", "AL": "Albania", "DZ": "Algeria", "AS": "American Samoa", "AD": "Andorra", "AO": "Angola", "AI": "Anguilla", "AQ": "Antarctica", "AG": "Antigua and Barbuda", "AR": "Argentina", "AM": "Armenia", "AW": "Aruba", "AU": "Australia", "AT": "Austria", "AZ": "Azerbaijan", "BS": "Bahamas", "BH": "Bahrain", "BD": "Bangladesh", "BB": "Barbados", "BY": "Belarus", "BE": "Belgium", "BZ": "Belize", "BJ": "Benin", "BM": "Bermuda", "BT": "Bhutan", "BO": "Bolivia", "BQ": "Bonaire, Sint Eustatius and Saba", "BA": "Bosnia and Herzegovina", "BW": "Botswana", "BV": "Bouvet Island", "BR": "Brazil", "IO": "British Indian Ocean Territory", "BN": "Brunei Darussalam", "BG": "Bulgaria", "BF": "Burkina Faso", "BI": "Burundi", "CV": "Cabo Verde", "KH": "Cambodia", "CM": "Cameroon", "CA": "Canada", "KY": "Cayman Islands", "CF": "Central African Republic", "TD": "Chad", "CL": "Chile", "CN": "China", "CX": "Christmas Island", "CC": "Cocos (Keeling) Islands", "CO": "Colombia", "KM": "Comoros", "CG": "Congo", "CD": "Congo (Democratic Republic)", "CK": "Cook Islands", "CR": "Costa Rica", "CI": "Côte d'Ivoire", "HR": "Croatia", "CU": "Cuba", "CW": "Curaçao", "CY": "Cyprus", "CZ": "Czech Republic", "DK": "Denmark", "DJ": "Djibouti", "DM": "Dominica", "DO": "Dominican Republic", "EC": "Ecuador", "EG": "Egypt", "SV": "El Salvador", "GQ": "Equatorial Guinea", "ER": "Eritrea", "EE": "Estonia", "SZ": "Eswatini", "ET": "Ethiopia", "FK": "Falkland Islands (Malvinas)", "FO": "Faroe Islands", "FJ": "Fiji", "FI": "Finland", "FR": "France", "GF": "French Guiana", "PF": "French Polynesia", "TF": "French Southern Territories", "GA": "Gabon", "GM": "Gambia", "GE": "Georgia", "DE": "Germany", "GH": "Ghana", "GI": "Gibraltar", "GR": "Greece", "GL": "Greenland", "GD": "Grenada", "GP": "Guadeloupe", "GU": "Guam", "GT": "Guatemala", "GG": "Guernsey", "GN": "Guinea", "GW": "Guinea-Bissau", "GY": "Guyana", "HT": "Haiti", "HM": "Heard Island and McDonald Islands", "VA": "Holy See", "HN": "Honduras", "HK": "Hong Kong", "HU": "Hungary", "IS": "Iceland", "IN": "India", "ID": "Indonesia", "IR": "Iran", "IQ": "Iraq", "IE": "Ireland", "IM": "Isle of Man", "IL": "Israel", "IT": "Italy", "JM": "Jamaica", "JP": "Japan", "JE": "Jersey", "JO": "Jordan", "KZ": "Kazakhstan", "KE": "Kenya", "KI": "Kiribati", "KP": "Korea (North)", "KR": "Korea (South)", "KW": "Kuwait", "KG": "Kyrgyzstan", "LA": "Lao People's Democratic Republic", "LV": "Latvia", "LB": "Lebanon", "LS": "Lesotho", "LR": "Liberia", "LY": "Libya", "LI": "Liechtenstein", "LT": "Lithuania", "LU": "Luxembourg", "MO": "Macao", "MG": "Madagascar", "MW": "Malawi", "MY": "Malaysia", "MV": "Maldives", "ML": "Mali", "MT": "Malta", "MH": "Marshall Islands", "MQ": "Martinique", "MR": "Mauritania", "MU": "Mauritius", "YT": "Mayotte", "MX": "Mexico", "FM": "Micronesia", "MD": "Moldova", "MC": "Monaco", "MN": "Mongolia", "ME": "Montenegro", "MS": "Montserrat", "MA": "Morocco", "MZ": "Mozambique", "MM": "Myanmar", "NA": "Namibia", "NR": "Nauru", "NP": "Nepal", "NL": "Netherlands", "NC": "New Caledonia", "NZ": "New Zealand", "NI": "Nicaragua", "NE": "Niger", "NG": "Nigeria", "NU": "Niue", "NF": "Norfolk Island", "MK": "North Macedonia", "MP": "Northern Mariana Islands", "NO": "Norway", "OM": "Oman", "PK": "Pakistan", "PW": "Palau", "PS": "Palestine", "PA": "Panama", "PG": "Papua New Guinea", "PY": "Paraguay", "PE": "Peru", "PH": "Philippines", "PN": "Pitcairn", "PL": "Poland", "PT": "Portugal", "PR": "Puerto Rico", "QA": "Qatar", "RE": "Reunion", "RO": "Romania", "RU": "Russian Federation", "RW": "Rwanda", "BL": "Saint Barthelemy", "SH": "Saint Helena", "KN": "Saint Kitts and Nevis", "LC": "Saint Lucia", "MF": "Saint Martin", "PM": "Saint Pierre and Miquelon", "VC": "Saint Vincent and the Grenadines", "WS": "Samoa", "SM": "San Marino", "ST": "Sao Tome and Principe", "SA": "Saudi Arabia", "SN": "Senegal", "RS": "Serbia", "SC": "Seychelles", "SL": "Sierra Leone", "SG": "Singapore", "SX": "Sint Maarten", "SK": "Slovakia", "SI": "Slovenia", "SB": "Solomon Islands", "SO": "Somalia", "ZA": "South Africa", "GS": "South Georgia and the South Sandwich Islands", "SS": "South Sudan", "ES": "Spain", "LK": "Sri Lanka", "SD": "Sudan", "SR": "Suriname", "SJ": "Svalbard and Jan Mayen", "SE": "Sweden", "CH": "Switzerland", "SY": "Syrian Arab Republic", "TW": "Taiwan", "TJ": "Tajikistan", "TZ": "Tanzania", "TH": "Thailand", "TL": "Timor-Leste", "TG": "Togo", "TK": "Tokelau", "TO": "Tonga", "TT": "Trinidad and Tobago", "TN": "Tunisia", "TR": "Turkey", "TM": "Turkmenistan", "TC": "Turks and Caicos Islands", "TV": "Tuvalu", "UG": "Uganda", "UA": "Ukraine", "AE": "United Arab Emirates", "GB": "United Kingdom", "US": "United States", "UY": "Uruguay", "UZ": "Uzbekistan", "VU": "Vanuatu", "VE": "Venezuela", "VN": "Viet Nam", "VG": "Virgin Islands (British)", "VI": "Virgin Islands (U.S.)", "WF": "Wallis and Futuna", "EH": "Western Sahara", "YE": "Yemen", "ZM": "Zambia", "ZW": "Zimbabwe"}
# dictionary for nationalities 

app = Flask(__name__)

DATABASE = 'red_notices.db'

def init_db():    ### Database initialize eder. entity_id alanı, her bildirimi tanımlayan birincil anahtar olarak tanımlanmıştır.
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor() #conn --> connection 
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notices (
                entity_id TEXT PRIMARY KEY,
                forename TEXT,
                name TEXT,
                date_of_birth TEXT,
                nationalities TEXT,
                image_href TEXT,
                thumbnail_href TEXT,
                self_href TEXT
            )
        ''')
        conn.commit()
########################################
def save_notice_to_db(notice):

    entity_id = notice.get('entity_id')
    forename = notice.get('forename', '')
    name = notice.get('name', '')
    date_of_birth = notice.get('date_of_birth', '')

    # nationality'i uzun isim ile yazma
    raw_nationalities = notice.get('nationalities', [])
    nationalities_str = []
    for code in raw_nationalities:
        full_name = nationalities_map.get(code, code)
        nationalities_str.append(full_name)
    nationalities = ','.join(nationalities_str)

    image_href = notice.get('_links', {}).get('images', {}).get('href', '')
    thumbnail_href = notice.get('_links', {}).get('thumbnail', {}).get('href', '')
    self_href = notice.get('_links', {}).get('self', {}).get('href', '')

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR IGNORE INTO notices (entity_id, forename, name, date_of_birth, nationalities, 
                                           image_href, thumbnail_href, self_href)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (entity_id, forename, name, date_of_birth, nationalities, image_href, thumbnail_href, self_href))
        conn.commit()

###########################################################

def consume_from_queue():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='host.docker.internal'))
    channel = connection.channel()
    channel.queue_declare(queue='interpol_notices', durable=True)

    def callback(ch, method, properties, body):
        notice_dict = json.loads(body)
        for notice in notice_dict['notices']:
            save_notice_to_db(notice)

    channel.basic_consume(queue='interpol_notices', on_message_callback=callback, auto_ack=True)
    channel.start_consuming()
#############################################################


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

########################################

@app.route('/') #ana sayfa
def index():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM notices')
        notices = cursor.fetchall()
    return render_template('index.html', notices=notices)

########################################
@app.route('/search') #search fonksiyonunu göster
def search():
    query = request.args.get('q', '').strip().lower() #searchden alına queryi databaseden alma
    print(f"Search Query Received: '{query}'")
    conn = get_db() #database connection
    cur = conn.cursor() #cursor 
    cur.execute("SELECT * FROM notices WHERE LOWER(name) LIKE ?", ('%' + query + '%',)) #cursor soyadı bul 
    notices = cur.fetchall() #cursor bulunca hepsini al
    print(f"Notices Found: {len(notices)}")
    conn.close()
    return render_template('search_results.html', notices=notices, query=query)

########################################
if __name__ == '__main__':
    init_db()
    threading.Thread(target=consume_from_queue).start()
    app.run(host='0.0.0.0', port=8000, debug=True) # Flask server'ını 8000 portunda çalıştırır





