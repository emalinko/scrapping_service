import asyncio
import sys, os
import codecs
import datetime

from django.contrib.auth import get_user_model
from django.db import DatabaseError

project_base_dir = os.path.dirname(os.path.abspath('manage.py'))
sys.path.append(project_base_dir)  # here store is root folder(means parent).
os.environ["DJANGO_SETTINGS_MODULE"] = "scrapping_service.settings"

import django

django.setup()

from scraping.parsers import *
from scraping.models import Vacancy, City, Language, Error, Url

User = get_user_model()

parsers = (
    (work, 'work'),
    (rabota, 'rabota'),
    (dou, 'dou'),
    (djinni, 'djinni')
)


def get_scraping_param_set():
    query_set = User.objects.filter(send_email=True).values()
    scraping_param_set = set((q['city_id'], q['language_id']) for q in query_set)
    return scraping_param_set


def get_urls(_settings):
    qs = Url.objects.all().values()
    url_dict = {(q['city_id'], q['language_id']): q['url_data'] for q in qs}
    urls = []
    for pair in _settings:
        if pair in url_dict:
            tmp = {}
            tmp['city'] = pair[0]
            tmp['language'] = pair[1]
            tmp['url_data'] = url_dict[pair]
            urls.append(tmp)
    return urls


lang_city_pairs = get_scraping_param_set()
url_list = get_urls(lang_city_pairs)

# city = City.objects.filter(slug='kiev').first()
# language = Language.objects.filter(slug='python').first()


# asynchronous launch of scraping functions
jobs, errors = [], []


async def async_scraping(value):
    func, url, city, language = value
    job, err = await loop.run_in_executor(None, func, url, city, language)
    errors.extend(err)
    jobs.extend(job)


loop = asyncio.get_event_loop()
tmp_task_list = [(func, data['url_data'][key], data['city'], data['language'])
                 for data in url_list
                 for func, key in parsers]
asyncio_tasks = asyncio.wait([loop.create_task(async_scraping(task_list_tuple)) for task_list_tuple in tmp_task_list])

# initial usual(synchronous) implementation

# for data in url_list:
#
#     for func, key in parsers:
#         url = data['url_data'][key]
#         j, e = func(url, city=data['city'], language=data['language'])
#         jobs += j
#         errors += e

loop.run_until_complete(asyncio_tasks)
loop.close()

for job in jobs:
    v = Vacancy(**job)
    try:
        v.save()
    except DatabaseError:
        pass

if errors:
    qs = Error.objects.filter(timestamp=datetime.date.today())
    if qs.exists():
        new_pair_query = qs.first()
        new_pair_query.data.update({'errors': errors})
        new_pair_query.save()
    else:
        er = Error(data=f'errors: {errors}').save()

# h = codecs.open('work.txt', 'w', 'utf-8')
# h.write(str(jobs))
# h.close()
