import requests
import bs4
from fake_headers import Headers
import re
import time
import json


def get_headers():
    return Headers(browser='opera', os='win').generate()


data = requests.get('https://spb.hh.ru/search/vacancy?text=python&area=1&area=2', headers=get_headers()).text
soup = bs4.BeautifulSoup(data, 'lxml')


main_content = soup.find('div', id='a11y-main-content')
summary = {}
for job in main_content.find_all('a', class_='serp-item__title'):
    href = job['href']

    data_job = requests.get(url=href, headers=get_headers()).text
    soup_data_job = bs4.BeautifulSoup(data_job, 'lxml')
    job_description = soup_data_job.find('div', class_='vacancy-description')
    description_text = job_description.get_text('\n', strip=True)
    pattern = r'django|flask'
    match = re.search(pattern, description_text, flags=re.IGNORECASE)

    if match is not None:
        salary_exist = soup_data_job.find('div', attrs={'data-qa': 'vacancy-salary'})
        if salary_exist is None:
            salary = 'Зарплата не указана'
        else:
            salary = soup_data_job.find('span', class_='bloko-header-section-2 bloko-header-section-2_lite').text
        vacancy_name = soup_data_job.find('span', class_='vacancy-company-name').text
        vacancy_city = soup_data_job.find('span', attrs={'data-qa': 'vacancy-view-raw-address'})
        if vacancy_city is None:
            vacancy_city = soup_data_job.find('p', attrs={'data-qa': 'vacancy-view-location'}).text
        else:
            vacancy_city = vacancy_city.text.split(',')[0]
        summary[href] = {
                'vacancy_name': vacancy_name.replace('\xa0', ''),
                'vacancy_city': vacancy_city,
                'salary': salary.replace('\xa0', '')
            }
    time.sleep(1)
with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(summary, f, ensure_ascii=False)
