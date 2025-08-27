from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import Sum, F
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import random

from .models import Quote
from .forms import QuoteForm


def get_random_quote():
    valid_quotes = Quote.objects.filter(source__isnull=False)

    total_weight = valid_quotes.aggregate(total=Sum('weight'))['total'] or 0
    if total_weight == 0:
        return None

    random_value = random.randint(1, total_weight)
    current = 0

    for quote in valid_quotes:
        current += quote.weight
        if current >= random_value:
            return quote

    return valid_quotes.order_by('?').first()


def random_quote_view(request):
    quote = get_random_quote()

    if quote:
        quote.increment_views()

    if request.method == 'POST':
        form = QuoteForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Цитата успешно добавлена!')
                return redirect('random_quote')
            except Exception as e:
                messages.error(request, f'Ошибка при сохранении: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{error}')
    else:
        form = QuoteForm()

    context = {
        'quote': quote,
        'form': form,
    }

    return render(request, 'quotes/random_quote.html', context)


@require_POST
def like_quote(request, quote_id):
    try:
        quote = Quote.objects.get(id=quote_id)
        quote.like()
        return JsonResponse({
            'likes': quote.likes,
            'dislikes': quote.dislikes,
            'status': 'success'
        })
    except Quote.DoesNotExist:
        return JsonResponse({
            'error': 'Цитата не найдена',
            'status': 'error'
        }, status=404)


@require_POST
def dislike_quote(request, quote_id):
    try:
        quote = Quote.objects.get(id=quote_id)
        quote.dislike()
        return JsonResponse({
            'likes': quote.likes,
            'dislikes': quote.dislikes,
            'status': 'success'
        })
    except Quote.DoesNotExist:
        return JsonResponse({
            'error': 'Цитата не найдена',
            'status': 'error'
        }, status=404)


def popular_quotes_view(request):
    popular_quotes = Quote.objects.annotate(
        popularity_calc=F('likes') - F('dislikes')
    ).order_by('-popularity_calc')[:10]

    most_viewed = Quote.objects.order_by('-views_count')[:10]
    recent_quotes = Quote.objects.order_by('-created_at')[:10]

    context = {
        'popular_quotes': popular_quotes,
        'most_viewed': most_viewed,
        'recent_quotes': recent_quotes,
    }

    return render(request, 'quotes/popular_quotes.html', context)


@require_POST
@login_required
def delete_quote(request, quote_id):
    quote = get_object_or_404(Quote, id=quote_id)
    quote.delete()
    messages.success(request, 'Цитата успешно удалена!')
    return redirect('manage_quotes')


@login_required
def manage_quotes_view(request):
    quotes = Quote.objects.all().order_by('-created_at')
    return render(request, 'quotes/manage_quotes.html', {'quotes': quotes})