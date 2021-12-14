from django.shortcuts import render
from django.http import JsonResponse
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.views import generic
from django.shortcuts import redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Q
from django.views import View
from django.http import HttpResponseRedirect
from django.views.generic.edit import UpdateView
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin

from datetime import timedelta

from .models import *
from .forms import PostForm
from .utils import *
import redis


def postList(request):
    posts = Post.objects.filter(
        createdon__lte=timezone.now()).order_by('-createdon')
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    client = redis.StrictRedis(
        host='127.0.0.1', port=6379, db=0, password=None, decode_responses=True)
    client.lpush('ipList', ip)
    if client.lindex('ipList', 0) != client.lindex('ipList', 1):
        errorMsg = 'Your IP address is different than before!'
    else:
        errorMsg = ''

    context = {
        'post_list': posts,
        'form': form,
        'errorMsg': errorMsg
    }
    return render(request, 'social/post_list.html', context)


class PostListView(View):
    def get(self, request, *args, **kwargs):
        postsOnFeed = Post.objects.all().order_by('-createdon')
        form = PostForm()
        context = {
            'post_list': postsOnFeed,
            'form': form,
        }
        return render(request, 'social/post_list.html', context)

    def post(self, request, *args, **kwargs):
        postsOnFeed = Post.objects.all().order_by('-createdon')
        form = PostForm(request.POST)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.author = request.user
            new_post.save()
            new_post.writeOnChain()
            form = PostForm()
            return HttpResponseRedirect('/social')
        context = {
            'post_list': postsOnFeed,
            'form': form,
        }
        return render(request, 'social/post_list.html', context)


class ProfileView(View):
    def get(self, request, pk, *args, **kwargs):
        profile = UserProfile.objects.get(pk=pk)
        user = profile.user
        posts = Post.objects.filter(author=user).order_by('-createdon')

        context = {
            'user': user,
            'profile': profile,
            'posts': posts
        }
        return render(request, 'social/profile.html', context)


class ProfileEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = UserProfile
    fields = ['name', 'bio', 'birth_date', 'location']
    template_name = 'social/profile_edit.html'

    def get_success_url(self):
        pk = self.kwargs['pk']
        return reverse_lazy('profile', kwargs={'pk': pk})

    def test_func(self):
        profile = self.get_object()
        return self.request.user == profile.user


class PostSearch(View):
    def get(self, request, *args, **kwargs):
        query = self.request.GET.get('query')
        posts = Post.objects.filter(
            Q(content__icontains=query)).order_by('-createdon')
        count = Post.objects.filter(
            Q(content__icontains=query)).order_by('-createdon').count()
        context = {
            'query': query,
            'posts': posts,
            'count': count
        }
        return render(request, 'social/search.html', context)


@staff_member_required
def numberOfPosts(request):
    users = User.objects.all().annotate(post_count=Count('post'))
    for user in users:
        user.post_count
    return render(request, 'social/numberOfPosts.html', {'users': users})


def postLastHour(request):
    response = []
    this_hour = timezone.now()
    one_hour_before = this_hour - timedelta(hours=1)
    posts = Post.objects.filter(createdon__range=(one_hour_before, this_hour))
    for post in posts:
        response.append(
            {
                'author': post.author.username,
                'createdon': post.createdon,
                'content': post.content
            }
        )
    if not response:
        return JsonResponse('No post has been published during the last hour', safe=False)
    return JsonResponse(response, safe=False)
