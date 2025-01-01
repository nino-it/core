from bs4 import BeautifulSoup
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import make_aware
from django.views.decorators.csrf import csrf_exempt
from datetime import date, datetime, timedelta
import calendar

import requests
from .models import Article
from django.shortcuts import render
from django.http import JsonResponse
from .models import Bill, BillSpec
from .scraper import scrape_bill_info, scrape_bill_and_specs
# fetch_bill_specs  
# scrape_bill_specs

def enter_bill(request):
    if request.method == 'POST':
        url = request.POST.get('url')
        try:
            # Get both bill and specifications data
            bill_data, specs_data = scrape_bill_and_specs(url)
            
            # Create the bill
            bill = Bill.objects.create(**bill_data)
            
            # Create specifications
            for spec_data in specs_data:
                BillSpec.objects.create(bill=bill, **spec_data)
                
            return JsonResponse({'success': True, 'bill_id': bill.bill_id})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return render(request, 'enter_bill.html')

# def enter_bill(request):
#     if request.method == 'POST':
#         url = request.POST.get('url')
#         try:
#             # Get page content once
#             response = requests.get(url)
#             response.raise_for_status()
#             soup = BeautifulSoup(response.text, 'html.parser')
            
#             # Scrape bill data
#             bill_data = scrape_bill_info(url)
#             bill = Bill.objects.create(**bill_data)
            
#             # Fetch and create specifications dynamically from API
#             api_url = "https://suf.purs.gov.rs/specifications"
#             headers = {
#                 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0 Safari/537.36',
#                 'Content-Type': 'application/json; charset=utf-8',
#                 'Cookie': 'localization=sr-Cyrl-RS; .AspNetCore.Antiforgery.vSsOd73lLiA=CfDJ8OOPe0xjgb1CpOY6pD8uFS2IfkXQOJ5qZZ6zwhssAj-kOegFiw78sTnKrMbVBmvMGVIANoFW7t00V2DzBRVmdXGs2vUDyOT4qSuy9psHYaCWbSmFsNDyalyYngwY0X8UXjkWGgYBLGfP-sWwX360ByQ',
#                 'Referer': 'https://suf.purs.gov.rs/v/?vl=A1A3SFg1VlVHUDdIWDVWVUcvTwQAOE0EAACjNAAAAAAAAAABkxGqo8AAAABe4%2BYYaEFd%2Fmand7MuFhbbtqfW2imF8wHRGga5QRj7JyP3ufdjGm4pBxJPaO%2BGhLiRQ5jwOrySHAOlXFYgGJb3oRfrFzu7CKN9Lx8h3GDigxEa56LQJUat8%2FRHa6E8itH5TjSTqdgprCXGXpBY%2FFByYzYCdJvfWLZM2bXiuGGeK%2FCzogY8rdmgEGGN5eCTFaTDR6b8pKTGK%2BkayFGk2dcnjj6yUeQypFbiDT2iCuTSDnx0LfSf3J3P%2BjA35kMMIz%2FMpqlCAA1uIdpsJP9bvFZrAvWvOoSkeBbC4tyce8AcPydEHYb9WNQeHTG4Z7fnlRK8OydTpXmVj47XZh66rKoYgS%2FaSMx4UlGmZuBgrGWAvUkEyzIrFJ%2FaNIPp5BWoeTB6dMogifOfTTJ50e7KS6UhCtX7b%2BhFDfa8JKMhNS1dDHGDKiwez%2BgpZ5YSK3frKhZvmHK3AcLeC46GefXQScz8pwkuOhl3g6JNTHBxBnE4irjzX2m0q2mpOvKOTKww2cZo335PsH5s5ITNMl%2FdgeYTqu8WdITEV0V%2Fh0RzsuUkqmyiEEWTOdMZ9pyIY%2FIIySm0P%2B1GzkigkqbFjQ8qAzJdjVWYnv4jTsZFbYdIWTKVYrht6IwfOzdJ7IXT77LuovwinQSLL3Iv0pQ9EQPj%2F2LuvUr%2BFHrTQn4rU2jlICFvuWOokSi5wKP%2FPAHiOckQiBQ%3D'

#             }
#             payload = {
#                 # Add the payload required by the API (e.g., bill reference details)
#                 "invoiceNumber": "P7HX5VUG-P7HX5VUG-282415",
#                 "token": "04ca744f-1dc9-4544-8e0d-91e61bf4e9a2"
#             }
#             specs_data = fetch_bill_specs(api_url, headers=headers, payload=payload)
#             for spec_data in specs_data:
#                 BillSpec.objects.create(bill=bill, **spec_data)
                
#             return JsonResponse({'success': True, 'bill_id': bill.bill_id})
#         except Exception as e:
#             return JsonResponse({'success': False, 'error': str(e)})
#     return render(request, 'enter_bill.html')
    
def calendar_view(request):
    # Get year and month from query parameters (default: current month)
    today = date.today()
    year = int(request.GET.get('year', today.year))
    month = int(request.GET.get('month', today.month))

    # Get first day of the month and the number of days
    first_day, days_in_month = calendar.monthrange(year, month)

    # Prepare calendar days with articles
    calendar_days = []
    start_date = date(year, month, 1)
    for day_offset in range(-first_day if first_day else 0, days_in_month + (7 - (first_day + days_in_month) % 7) % 7):
        current_date = start_date + timedelta(days=day_offset)

        if current_date.month == month:
            articles = Article.objects.filter(time_scheduled__date=current_date)
            calendar_days.append({'day': current_date.day, 'articles': articles})
        else:
            calendar_days.append(None)  # For empty cells

    # Navigation logic
    previous_month = month - 1 if month > 1 else 12
    previous_year = year - 1 if month == 1 else year
    next_month = month + 1 if month < 12 else 1
    next_year = year + 1 if month == 12 else year

    return render(request, 'calendar.html', {
        'calendar_days': calendar_days,
        'current_month_name': calendar.month_name[month],
        'current_year': year,
        'previous_month': previous_month,
        'previous_year': previous_year,
        'next_month': next_month,
        'next_year': next_year,
        'day_headers': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    })

@csrf_exempt
def article_edit_or_create(request):
    if request.method == 'POST':
        article_id = request.POST.get('id', None)
        title = request.POST.get('title', '').strip()
        text = request.POST.get('text', '').strip()
        category = request.POST.get('category', '').strip()
        priority = request.POST.get('priority', 1)
        time_scheduled = request.POST.get('time_scheduled', None)

        if time_scheduled:
            time_scheduled = make_aware(datetime.strptime(time_scheduled, '%Y-%m-%dT%H:%M'))

        if article_id:
            # Edit existing article
            article = get_object_or_404(Article, id=article_id)
            article.title = title
            article.text = text
            article.category = category
            article.priority = int(priority)
            article.time_scheduled = time_scheduled
            article.save()
        else:
            # Create new article
            article = Article.objects.create(
                title=title,
                text=text,
                category=category,
                priority=int(priority),
                time_scheduled=time_scheduled
            )

        return JsonResponse({'success': True, 'id': article.id})

    if request.method == 'GET':
        article_id = request.GET.get('id')
        article = get_object_or_404(Article, id=article_id)
        return JsonResponse({
            'id': article.id,
            'title': article.title,
            'text': article.text,
            'category': article.category,
            'priority': article.priority,
            'time_scheduled': article.time_scheduled.isoformat() if article.time_scheduled else ''
        })

    return JsonResponse({'error': 'Invalid request'}, status=400)


@csrf_exempt
def article_delete(request):
    if request.method == 'POST':
        article_id = request.POST.get('id')
        article = get_object_or_404(Article, id=article_id)
        article.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'error': 'Invalid request'}, status=400)

