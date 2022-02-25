from django.db import models


class Author(models.Model):

    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)


class Book(models.Model):

    title = models.CharField(max_length=200)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)


