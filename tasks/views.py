from django.shortcuts import render
from .models import Task
from django.views.generic import ListView

class TaskListView(ListView):
    model = Task
    template_name = 'tasks-list.html'
   
