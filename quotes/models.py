from django.db import models
from django.db.models import F


class Source(models.Model):
    SOURCE_TYPES = [
        ('movie', 'Фильм'),
        ('book', 'Книга'),
        ('song', 'Песня'),
        ('other', 'Другое'),
    ]

    name = models.CharField(max_length=200, verbose_name="Название")
    type = models.CharField(max_length=20, choices=SOURCE_TYPES, verbose_name="Тип")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['name', 'type']
        verbose_name = "Источник"
        verbose_name_plural = "Источники"

    def __str__(self):
        return f"{self.get_type_display()}: {self.name}"

    def quote_count(self):
        return self.quotes.count()


class Quote(models.Model):
    text = models.TextField(verbose_name="Текст цитаты")
    source = models.ForeignKey(Source, on_delete=models.CASCADE, related_name='quotes', verbose_name="Источник",
                               null=False, blank=False)
    weight = models.PositiveIntegerField(default=1, verbose_name="Вес")
    views_count = models.PositiveIntegerField(default=0, verbose_name="Количество просмотров")
    likes = models.PositiveIntegerField(default=0, verbose_name="Лайки")
    dislikes = models.PositiveIntegerField(default=0, verbose_name="Дизлайки")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Цитата"
        verbose_name_plural = "Цитаты"
        unique_together = ['text', 'source']

    def __str__(self):
        return f"{self.text}({self.source})"

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def increment_views(self):
        Quote.objects.filter(id=self.id).update(views_count=F('views_count') + 1)
        self.refresh_from_db()

    def like(self):
        Quote.objects.filter(id=self.id).update(likes=F('likes') + 1)
        self.refresh_from_db()

    def dislike(self):
        Quote.objects.filter(id=self.id).update(dislikes=F('dislikes') + 1)
        self.refresh_from_db()

    @property
    def popularity(self):
        return self.likes - self.dislikes