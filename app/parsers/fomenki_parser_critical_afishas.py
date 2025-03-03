import requests
from bs4 import BeautifulSoup
import json
import time
import re
from datetime import datetime


def get_event_year(event_date_str):
    current_year = datetime.now().year
    current_month = datetime.now().month
    current_day = datetime.now().day

    day, month, time = event_date_str.replace(',', '').split()
    months = {
        'января': '01', 'февраля': '02', 'марта': '03', 'апреля': '04',
        'мая': '05', 'июня': '06', 'июля': '07', 'августа': '08',
        'сентября': '09', 'октября': '10', 'ноября': '11', 'декабря': '12'
    }

    event_month = months[month]
    event_day = int(day)

    event_date = datetime.strptime(f"{event_month}-{event_day}", "%m-%d")
    current_date = datetime.strptime(f"{current_month}-{current_day}", "%m-%d")

    if event_date < current_date:
        return current_year + 1
    else:
        return current_year


def format_date(date_str):
    months = {
        'января': '01', 'февраля': '02', 'марта': '03', 'апреля': '04',
        'мая': '05', 'июня': '06', 'июля': '07', 'августа': '08',
        'сентября': '09', 'октября': '10', 'ноября': '11', 'декабря': '12'
    }
    day, month, time = date_str.replace(',', '').split()
    event_year = get_event_year(date_str)
    day = day.zfill(2)
    return f"{event_year}-{months[month]}-{day}T{time}:00"

def clean_text(text):
    return text.replace('\xa0', ' ').replace('\u00ad', '').strip()

def remove_extra_spaces(text):
    return re.sub(r'\s+', ' ', text).strip()

def extract_duration(text):
    match = re.search(r'(продолжительность:\s*(\d+)\s*(час[а-я]*|минут[а-я]*)\s*(с\s*\d*\s*антрактом|без\s*антракта)?)',
                      text, re.IGNORECASE)
    return match.group(0).strip() if match else None

def remove_classes(soup):
    for tag in soup.find_all(True):
        tag.attrs.pop('class', None)
    return soup

def remove_blocks_with_hashtags(html):
    soup = BeautifulSoup(html, 'html.parser')
    soup = remove_classes(soup)

    for element in soup.find_all(string=re.compile(r'#\w+')):
        element.parent.extract()

    cleaned_html = str(soup).replace('\xa0', ' ')

    return cleaned_html

def fomenki_parser_critical_afishas():
    print('Загрузка данных из файла JSON.')
    with open('app/storage/critical_afishas.json', 'r', encoding='utf-8') as jsonfile:
        events_data = json.load(jsonfile)

    all_events = []
    seen_titles = set()

    for index, event_data in enumerate(events_data):
        try:
            url = event_data['link']
            time.sleep(1)
            print(f'Запрос к URL: {url}.')
            response = requests.get(url, timeout=10)
            time.sleep(2)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                print('Парсинг заголовка.')
                title_tag = soup.find('h1', class_='with-play-btn') or soup.find('header', class_='header').find('h1')
                if title_tag:
                    unwanted_place_tag = title_tag.find('div', class_='place w-theatre-icon')
                    if unwanted_place_tag:
                        unwanted_place_tag.decompose()

                    premiere_tag = title_tag.find('span', class_='prime plate plate-magenta')
                    if premiere_tag:
                        premiere_tag.decompose()

                    hall_tag = title_tag.find('div', class_='place')
                    hall_text = clean_text(hall_tag.get_text(strip=True)) if hall_tag else None

                    if hall_tag:
                        hall_tag.decompose()

                    title_text = clean_text(title_tag.get_text())
                else:
                    title_text = ''
                    hall_text = ''

                if title_text in seen_titles:
                    print(f'Событие "{title_text}" уже добавлено, пропускаем.')
                    print('Пауза перед следующим запросом.')
                    time.sleep(2)
                    continue
                seen_titles.add(title_text)

                print('Парсинг блока короткой информации.')
                info_block = soup.select_one('.info-wrapper .info')
                duration = extract_duration(
                    remove_extra_spaces(clean_text(info_block.get_text(separator=" ").strip()))) if info_block else None
                short_description = duration.capitalize() if duration else None

                print('Парсинг списка создателей.')
                creators_list = []
                creators = soup.select('.creators li')

                for creator in creators:
                    role_text = clean_text(creator.get_text(strip=True))
                    person = creator.find('span') or creator.find('a')

                    is_link = person.name == 'a' if person else False
                    person_name = clean_text(person.get_text(strip=True)) if person else ""
                    creator_url = f'https://fomenki.ru{person["href"]}' if is_link else None

                    role = role_text.replace(person_name, '').replace('—', '').strip()

                    creators_list.append({
                        "role": role,
                        "name": person_name,
                        "is_link": bool(is_link),
                        "url": creator_url
                    })

                print('Парсинг предупреждения о курении.')
                smoking_warning = soup.select_one('.info.smoking')
                smoking_text = clean_text(smoking_warning.get_text(strip=True)) if smoking_warning else None

                print('Парсинг событий.')
                events = []
                event_elements = soup.select('.events .event')

                for event_element in event_elements:
                    date_str = clean_text(event_element.select_one('.date').get_text(strip=True))
                    formatted_date = format_date(date_str)

                    ticket_btn = event_element.select_one('.tickets .btn')
                    if ticket_btn and 'href' in ticket_btn.attrs:
                        ticket_link = ticket_btn['href'].split('/')[-1].lstrip('#')
                    else:
                        ticket_link = None

                    events.append({
                        'date': formatted_date,
                        'external_id': ticket_link
                    })

                print('Парсинг описания.')
                about_section = soup.select_one('.about')
                if about_section:
                    description_html = str(about_section)
                    description_cleaned = remove_blocks_with_hashtags(description_html)
                else:
                    description_cleaned = None

                print('Парсинг актеров и ролей.')
                current_actors_roles = []
                current_actor_elements = soup.select('.actors.actors-all li')

                for current_actor_elem in current_actor_elements:
                    current_role_elem = current_actor_elem.select_one('.role')

                    if current_role_elem:
                        current_role = clean_text(current_role_elem.get_text(strip=True)).replace('\n', ' ').replace('<br>',
                                                                                                                     ', ')

                        cast_elements = current_actor_elem.select('.cast .person .hl')
                        current_img_elem = current_actor_elem.select_one('.cast .person img')
                        current_actor_image = f'https://fomenki.ru{current_img_elem["src"]}' if current_img_elem else None

                        for cast_elem in cast_elements:
                            actor_name = clean_text(cast_elem.get_text(strip=True))
                            actor_url = f'https://fomenki.ru{cast_elem.find("a")["href"]}' if cast_elem.find("a") else None

                            current_actors_roles.append({
                                'role': current_role,
                                'actor': actor_name,
                                'actor_url': actor_url,
                                'image': current_actor_image
                            })

                print('Парсинг галереи.')
                gallery_images = []
                gallery_section = soup.select_one('.gallery .list')

                if gallery_section:
                    image_elements = gallery_section.select('.item a')
                    for img_elem in image_elements:
                        img_url = img_elem['href']
                        gallery_images.append(f'https:{img_url}')

                print(f'Добавление события "{title_text}".')
                event = {
                    'title': title_text,
                    'hall': hall_text,
                    'hall_code': event_data.get('hall_code'),
                    'short_description': short_description,
                    'creators': creators_list,
                    'smoking_warning': smoking_text,
                    'events': events,
                    'description': description_cleaned,
                    'current_actors_roles': current_actors_roles,
                    'gallery': gallery_images,
                }

                all_events.append(event)

                print('Пауза перед следующим запросом.')
                time.sleep(2)
            else:
                print(f"Ошибка при запросе данных с {url}: {response.status_code}")
        except Exception as err:
            print(f"Не удалось подключиться: {url}, Ошибка: {err}")

    print('Запись всех данных в файл.')
    with open('app/storage/critical_afishas_data.json', 'w', encoding='utf-8') as jsonfile:
        json.dump(all_events, jsonfile, ensure_ascii=False, indent=4)

    print('Все данные успешно записаны.')
