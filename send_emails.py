import datetime
import os
import sys

import django
from django.contrib.auth import get_user_model
from django.core.mail import EmailMultiAlternatives

project_base_dir = os.path.dirname(os.path.abspath('manage.py'))
sys.path.append(project_base_dir)  # here store is root folder(means parent).
os.environ["DJANGO_SETTINGS_MODULE"] = "scrapping_service.settings"

django.setup()

from scraping.models import Vacancy, Error, Url
from scrapping_service.settings import EMAIL_HOST_USER

ADMIN_USER = EMAIL_HOST_USER

# Send emails with Vacancies to Users

today = datetime.date.today()
empty = '<h2>По вашему запросу нету свежих вакансий</h2>'
subject = f'Рассылка вакансий за {today}'
text_content = f'Рассылка вакансий за {today}'
from_email = EMAIL_HOST_USER
User = get_user_model()
subscribers_info = User.objects.filter(send_email=True).values('city', 'language', 'email')
mailing_list_dict = {}
for subscriber in subscribers_info:
    mailing_list_dict.setdefault((subscriber['city'], subscriber['language']), [])
    mailing_list_dict[(subscriber['city'], subscriber['language'])].append(subscriber['email'])
if mailing_list_dict:
    params = {'city_id__in': [], 'language_id__in': []}
    for pair in mailing_list_dict.keys():
        params['city_id__in'].append(pair[0])
        params['language_id__in'].append(pair[1])
#     vacancy_qs = Vacancy.objects.filter(**params, timestamp=today).values()[:10]
#     vacancies_dict = {}
#     for vacancy in vacancy_qs:
#         vacancies_dict.setdefault((vacancy['city_id'], vacancy['language_id']), [])
#         vacancies_dict[(vacancy['city_id'], vacancy['language_id'])].append(vacancy)
#     for keys, emails in mailing_list_dict.items():
#         rows = vacancies_dict.get(keys, [])
#         html = ''
#         for row in rows:
#             html += f'<h5><a href="{row["url"]}">{row["title"]}</a></h5>'
#             html += f'<p>{row["description"]}</p>'
#             html += f'<p>{row["company"]}</p><br><hr>'
#         html_content = html if html else empty
#         for email in emails:
#             to = email
#
#             msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
#             msg.attach_alternative(html_content, "text/html")
#             # msg.send()

# Compose email message with scraping Errors and New City/PL pairs desired by users

subject = ''
text_content = ''
to = ADMIN_USER
html_content = ''

error_qs = Error.objects.filter(timestamp=today)
if error_qs.exists():
    error_object = error_qs.first()
    error_list = error_object.data.get('errors', [])
    for _dict in error_list:
        html_content += f'<h5><a href="{_dict["url"]}">{_dict["status"]} at {_dict["url"]}</a></h5><br>'
    subject = 'Ошибки скапинга'
    text_content = 'Ошибки скапинга'
    new_search_params = error_object.data.get('user_desirable_search_params', [])
    if new_search_params:
        html_content += '<br><h2>Пожелания пользователей</h2>'
    for _dict in new_search_params:
        html_content += f'<h5>New pair: {_dict["city"]}/{_dict["language"]} desirable by {_dict["email"]}</h5><br>'
    subject += ' Новые пары для поиска'
    text_content += ' Новые пары для поиска'

# Compose (and append to previous email if exists) email message with absent Urls for City/Language pairs

urls_qs = Url.objects.all().values('city', 'language')
urls_dict = {(u['city'], u['language']): True for u in urls_qs}
non_existent_urls = ''
for keys in mailing_list_dict.keys():
    if keys not in urls_dict.keys():
        if keys[0] and keys[1]:
            non_existent_urls += f'<h5>There is no URL for City"{keys[0]}"/' \
                             f'Language"{keys[1]}" pair.</h5><br>'
if non_existent_urls:
    subject += ' Отсутствующие урлы'
    html_content += non_existent_urls

# Send composed email message with all Errors to Admin

if subject:
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()

# send mail using alternative data types implementation ('text/html')

# subject, from_email, to = 'hello', 'from@example.com', 'to@example.com'
# text_content = 'This is an important message.'
# html_content = '<p>This is an <strong>important</strong> message.</p>'
# msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
# msg.attach_alternative(html_content, "text/html")
# msg.send()
