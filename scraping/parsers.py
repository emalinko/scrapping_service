import requests
import codecs
from bs4 import BeautifulSoup as BS
from random import randint

__all__ = ('work', 'rabota', 'dou', 'djinni')

headers = [
    {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:82.0) Gecko/20100101 Firefox/82.0',
     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'},
    {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'},
    {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}
]


def work(url, city=None, language=None):
    jobs = []
    errors = []
    domain = 'https://www.work.ua'
    if url:
        resp = requests.get(url, headers=headers[randint(0, 2)])
        if resp.status_code == 200:
            soup = BS(resp.content, 'html.parser')
            main_div = soup.find('div', id='pjax-job-list')
            if main_div:
                div_list = main_div.find_all('div', attrs={'class': 'job-link'})
                for div in div_list:
                    title_container = div.find('h2')
                    title = title_container.text
                    href = title_container.a['href']
                    content = div.p.text
                    company_container = div.find('div', attrs={'class': 'add-top-xs'})
                    try:
                        company = company_container.span.b.text
                    except AttributeError:
                        company = 'Работодатель не указан'
                    jobs.append({'title': title, 'url': domain + href, 'description': content, 'company': company,
                                 'city_id': city, 'language_id': language})
            else:
                errors.append({'url': url, 'status': 'main div absence'})
        else:
            errors.append({'url': url, 'status': resp.status_code})

    return jobs, errors


def rabota(url, city=None, language=None):
    jobs = []
    errors = []
    domain = 'https://rabota.ua'
    if url:
        resp = requests.get(url, headers=headers[randint(0, 2)])
        if resp.status_code == 200:
            soup = BS(resp.content, 'html.parser')
            new_jobs = soup.find('div', attrs={'class': 'f-vacancylist-newnotfound'})
            if not new_jobs:
                table = soup.find('table', id='ctl00_content_vacancyList_gridList')
                if table:
                    div_list = table.find_all('div', attrs={'class': 'card-body'})
                    for div in div_list:
                        title_container = div.find('h2', attrs={'class': 'card-title'})
                        title = title_container.a.text
                        href = title_container.a['href']
                        content = div.find('div', attrs={'class': 'card-description'}).text
                        company_container = div.find('p', attrs={'class': 'company-name'})
                        try:
                            company = company_container.a.text
                        except AttributeError:
                            company = 'Работодатель не указан'
                        jobs.append({'title': title, 'url': domain + href, 'description': content, 'company': company,
                                     'city_id': city, 'language_id': language})
                else:
                    errors.append({'url': url, 'status': 'table absence'})
            else:
                errors.append({'url': url, 'status': 'no vacancy'})
        else:
            errors.append({'url': url, 'status': resp.status_code})

    return jobs, errors


def dou(url, city=None, language=None):
    jobs = []
    errors = []
    if url:
        resp = requests.get(url, headers=headers[randint(0, 2)])
        if resp.status_code == 200:
            soup = BS(resp.content, 'html.parser')
            vacancy_list = soup.find('div', id='vacancyListId')
            if vacancy_list:
                div_list = vacancy_list.find_all('div', attrs={'class': 'vacancy'})
                for div in div_list:
                    title_container = div.find('div', attrs={'class': 'title'})
                    title = title_container.a.text
                    href = title_container.a['href']
                    content = div.find('div', attrs={'class': 'sh-info'}).text
                    company_container = title_container.strong.a
                    try:
                        company = company_container.text
                    except AttributeError:
                        company = 'Работодатель не указан'
                    jobs.append({'title': title, 'url': href, 'description': content, 'company': company,
                                 'city_id': city, 'language_id': language})
            else:
                errors.append({'url': url, 'status': 'vacancy_div absence'})
        else:
            errors.append({'url': url, 'status': resp.status_code})

    return jobs, errors


def djinni(url, city=None, language=None):
    jobs = []
    errors = []
    domain = 'https://djinni.co'
    if url:
        resp = requests.get(url, headers=headers[randint(0, 2)])
        if resp.status_code == 200:
            soup = BS(resp.content, 'html.parser')
            vacancy_list = soup.find('ul', attrs={'class': 'list-unstyled list-jobs'})
            if vacancy_list:
                li_list = vacancy_list.find_all('li', attrs={'class': 'list-jobs__item'})
                for li in li_list:
                    title_container = li.find('div', attrs={'class': 'list-jobs__title'})
                    title = title_container.a.text
                    href = title_container.a['href']
                    content = li.find('div', attrs={'class': 'list-jobs__description'}).p.text
                    company = 'Ресурс не указывает работодателя'
                    jobs.append({'title': title, 'url': domain + href, 'description': content, 'company': company,
                                 'city_id': city, 'language_id': language})
            else:
                errors.append({'url': url, 'status': 'vacancy_ul absence'})
        else:
            errors.append({'url': url, 'status': resp.status_code})

    return jobs, errors


# if __name__ == '__main__':
#     url = 'https://djinni.co/jobs/keyword-python/kyiv/'
#     jobs, errors = djinni(url)
#
#     h = codecs.open('../djinni.txt', 'w', 'utf-8')
#     h.write(str(jobs))
#     h.close()
