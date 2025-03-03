import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime


def get_next_month(year, month):
    if month == 12:
        year += 1
        month = 1
    else:
        month += 1
    return year, month


def fetch_data_for_month(year, month):
    BLOCKED_TITLES = [
        "Пугачёв",
        "Совершенно Невероятное Событие (Женитьба в 2‑х действиях)",
        "Безумная из Шайо",
        "Бесприданница",
        "Война и мир. Начало романа",
        "Волки и овцы",
        "Двадцать третий",
        "Египетские ночи",
        "Король Лир",
        "К 90‑летию Петра Фоменко. «Комедия о трагедии»",
        "Мастер и Маргарита",
        "Семейное счастие",
        "Сон в летнюю ночь",
        "Чайка",
        "Алиса в Зазеркалье",
        "Вишнёвый сад",
        "Молли Суини",
        "Завещание Чарльза Адамса, или Дом семи повешенных",
        "Театральный роман (Записки покойника)",
        "…Души",
        "Мой Брель",
        "Новогоднее приключение Маши и Вити",
        "Руслан и Людмила",
        "Триптих",
        "Путешествие в театральную историю",
        "Рыцарь. Моцарт. Пир ",
        "Божественная комедия. Вариации",
        "Lёгкое Dыхание",
        "Мамаша Кураж",
        "Египетская марка",
        "Подарок",
        "Опасные связи",
        "Рыжий",
        "Сказка Арденнского леса",
        "Школа жён",
        "Светлые души, или О том, как написать рассказ",
        "Заходите-заходите",
        # "Маякосвкий. Послушайте",
        "Последние свидания",
        "В гостях у барона Мюнхгаузена",
        "Он был титулярный советник",
        "Самое важное",
        "Смешной человек",
        "Фантазии Фарятьева",
        "Чающие движения воды",
        "Серёжа очень тупой",
        "Выбрать троих",
        "Доктор Живаго",
        "Королевство кривых",
        "Летний осы кусают нас даже в ноябре",
        "Одна абсолютно счастливая деревня",
        "Моцарт «Дон Жуан». Генеральная репетиция",
        "Пять вечеров",
        "Счастливые дни"
    ]

    url = f'https://fomenki.ru/timetable/{month:02d}-{year}/'
    print(f'Запрашиваю данные с {url}')
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        events = []

        event_blocks = soup.find_all('div', class_='event')

        if not event_blocks:
            print(f'Нет данных для {month:02d}-{year}. Останавливаю сбор данных.')
            return []

        for event in event_blocks:
            date_div = event.find('div', class_='date')
            if date_div:
                date_str = date_div.find('h2').get_text(strip=True)
                day = date_str.split()[0]
            else:
                continue

            time_div = event.find('p', class_='time') if event.find('p', class_='time') else None
            time_text = time_div.get_text(strip=True) if time_div else ''
            premiere_text = ''
            is_premiere = False

            if time_div:
                premiere_tag = time_div.find('span', class_='prime')
                if premiere_tag:
                    is_premiere = True
                    premiere_text = premiere_tag.get_text(strip=True)
                    time_text = time_text.replace(premiere_text, '').strip()

            title_tag = event.find('div', class_='title').find('a') if event.find('div', class_='title') else None
            title = title_tag['title'] if title_tag else None
            link = title_tag['href'] if title_tag else None

            if title:
                title = title.replace('\u00A0', ' ').replace('\u00ad', '')

                if title in BLOCKED_TITLES:
                    print(f'Спектакль "{title}" пропущен, так как он в списке запрещённых.')
                    continue

            try:
                event_datetime_str = f'{year}-{month:02d}-{int(day):02d}T{time_text}'
                event_datetime = datetime.fromisoformat(event_datetime_str)
            except ValueError as e:
                print(f'Ошибка в дате: {e}')
                continue

            events.append({
                'datetime': event_datetime,
                'title': title,
                'link': f'https://fomenki.ru{link}',
                'is_premiere': is_premiere
            })

        return events
    else:
        print(f'Ошибка при получении данных с {url}: {response.status_code}')
        return None


def get_main_data():
    print('asdadasd')
    with open('app/storage/parser_events_data.json', 'w', encoding='utf-8') as jsonfile:
        json.dump({"date": "sss"}, jsonfile, ensure_ascii=False, indent=4)

    print('Данные успешно записаны.')

if __name__ == '__main__':
    get_main_data()

