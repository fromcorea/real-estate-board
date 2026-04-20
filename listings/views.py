from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView

from django.contrib import messages

from .forms import PropertyForm, PropertyImageFormSet, ReportForm, BoardPostForm, BoardPasswordForm
from .models import Property, Bookmark, Notice, BoardPost


class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['latest_properties'] = Property.objects.filter(status='approved').select_related('author')[:8]
        ctx['notices'] = Notice.objects.all()[:3]
        ctx['property_types'] = Property.PROPERTY_TYPE_CHOICES
        return ctx


class PropertyListView(ListView):
    model = Property
    template_name = 'listings/property_list.html'
    context_object_name = 'properties'
    paginate_by = 12

    def get_queryset(self):
        qs = Property.objects.filter(status='approved').select_related('author')
        params = self.request.GET

        keyword = params.get('keyword', '').strip()
        if keyword:
            qs = qs.filter(Q(title__icontains=keyword) | Q(address__icontains=keyword))

        property_type = params.get('property_type')
        if property_type:
            qs = qs.filter(property_type=property_type)

        trade_type = params.get('trade_type')
        if trade_type:
            qs = qs.filter(trade_type=trade_type)

        price_min = params.get('price_min')
        if price_min:
            qs = qs.filter(price__gte=int(price_min))

        price_max = params.get('price_max')
        if price_max:
            qs = qs.filter(price__lte=int(price_max))

        area_min = params.get('area_min')
        if area_min:
            qs = qs.filter(area__gte=float(area_min))

        area_max = params.get('area_max')
        if area_max:
            qs = qs.filter(area__lte=float(area_max))

        rooms = params.get('rooms')
        if rooms:
            if rooms == '4':
                qs = qs.filter(rooms__gte=4)
            else:
                qs = qs.filter(rooms=int(rooms))

        include_completed = params.get('include_completed')
        if not include_completed:
            qs = qs.filter(is_available=True)

        ordering = params.get('ordering', '-created_at')
        if ordering in ['-created_at', 'price', '-price', '-view_count']:
            qs = qs.order_by(ordering)

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['params'] = self.request.GET
        ctx['property_types'] = Property.PROPERTY_TYPE_CHOICES
        ctx['trade_types'] = Property.TRADE_TYPE_CHOICES
        if self.request.user.is_authenticated:
            ctx['bookmarked_ids'] = set(
                Bookmark.objects.filter(user=self.request.user).values_list('property_id', flat=True)
            )
        return ctx


class PropertyDetailView(DetailView):
    model = Property
    template_name = 'listings/property_detail.html'
    context_object_name = 'property'

    def get_queryset(self):
        return Property.objects.select_related('author').prefetch_related('images')

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        Property.objects.filter(pk=self.object.pk).update(view_count=self.object.view_count + 1)
        return response

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['report_form'] = ReportForm()
        if self.request.user.is_authenticated:
            ctx['is_bookmarked'] = Bookmark.objects.filter(
                user=self.request.user, property=self.object
            ).exists()
        return ctx


class PropertyCreateView(CreateView):
    model = Property
    form_class = PropertyForm
    template_name = 'listings/property_form.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if self.request.POST:
            ctx['image_formset'] = PropertyImageFormSet(self.request.POST, self.request.FILES)
        else:
            ctx['image_formset'] = PropertyImageFormSet()
        return ctx

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            form.instance.author = self.request.user
        else:
            form.instance.author = None
        self.object = form.save()
        image_formset = PropertyImageFormSet(self.request.POST, self.request.FILES, instance=self.object)
        if image_formset.is_valid():
            images = image_formset.save()
            if images and not any(img.is_thumbnail for img in images):
                images[0].is_thumbnail = True
                images[0].save()
        return redirect('listings:detail', pk=self.object.pk)


class PropertyUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Property
    form_class = PropertyForm
    template_name = 'listings/property_form.html'

    def test_func(self):
        obj = self.get_object()
        return obj.author is None or obj.author == self.request.user

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if self.request.POST:
            ctx['image_formset'] = PropertyImageFormSet(
                self.request.POST, self.request.FILES, instance=self.object
            )
        else:
            ctx['image_formset'] = PropertyImageFormSet(instance=self.object)
        return ctx

    def form_valid(self, form):
        ctx = self.get_context_data()
        image_formset = ctx['image_formset']
        self.object = form.save()
        if image_formset.is_valid():
            image_formset.save()
        return redirect('listings:detail', pk=self.object.pk)


class PropertyDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Property
    template_name = 'listings/property_confirm_delete.html'
    success_url = reverse_lazy('listings:my_listings')

    def test_func(self):
        return self.get_object().author == self.request.user


class MyListingsView(LoginRequiredMixin, ListView):
    model = Property
    template_name = 'listings/my_listings.html'
    context_object_name = 'properties'

    def get_queryset(self):
        qs = Property.objects.filter(author=self.request.user)
        status = self.request.GET.get('status')
        if status:
            qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        ctx['total_count'] = user.properties.count()
        ctx['pending_count'] = user.properties.filter(status='pending').count()
        ctx['approved_count'] = user.properties.filter(status='approved').count()
        ctx['rejected_count'] = user.properties.filter(status='rejected').count()
        ctx['completed_count'] = user.properties.filter(status='completed').count()
        return ctx


class BookmarkListView(LoginRequiredMixin, ListView):
    template_name = 'listings/bookmarks.html'
    context_object_name = 'bookmarks'

    def get_queryset(self):
        return Bookmark.objects.filter(user=self.request.user).select_related('property__author')


class BookmarkToggleView(LoginRequiredMixin, View):
    def post(self, request, pk):
        prop = get_object_or_404(Property, pk=pk)
        bookmark, created = Bookmark.objects.get_or_create(user=request.user, property=prop)
        if not created:
            bookmark.delete()
            return JsonResponse({'bookmarked': False})
        return JsonResponse({'bookmarked': True})


class PropertyCompleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        prop = get_object_or_404(Property, pk=pk, author=request.user)
        prop.status = 'completed'
        prop.is_available = False
        prop.save()
        return redirect('listings:my_listings')


class ReportCreateView(LoginRequiredMixin, View):
    def post(self, request, pk):
        prop = get_object_or_404(Property, pk=pk)
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.reporter = request.user
            report.property = prop
            report.save()
        return redirect('listings:detail', pk=pk)


class MapView(TemplateView):
    template_name = 'listings/map.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['properties'] = Property.objects.filter(
            status='approved', latitude__isnull=False, longitude__isnull=False
        ).select_related('author')[:100]
        return ctx


class NoticeListView(ListView):
    model = Notice
    template_name = 'listings/notice_list.html'
    context_object_name = 'notices'
    paginate_by = 20


class NoticeDetailView(DetailView):
    model = Notice
    template_name = 'listings/notice_detail.html'
    context_object_name = 'notice'


# ===== Board (게시판형 매물 공유) =====

class BoardListView(ListView):
    model = BoardPost
    template_name = 'listings/board_list.html'
    context_object_name = 'posts'
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset()
        category = self.request.GET.get('category')
        if category:
            qs = qs.filter(category=category)
        keyword = self.request.GET.get('keyword', '').strip()
        if keyword:
            qs = qs.filter(Q(title__icontains=keyword) | Q(content__icontains=keyword))
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['categories'] = BoardPost.CATEGORY_CHOICES
        ctx['params'] = self.request.GET
        return ctx


class BoardDetailView(DetailView):
    model = BoardPost
    template_name = 'listings/board_detail.html'
    context_object_name = 'post'

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        BoardPost.objects.filter(pk=self.object.pk).update(view_count=self.object.view_count + 1)
        return response


class BoardCreateView(CreateView):
    model = BoardPost
    form_class = BoardPostForm
    template_name = 'listings/board_form.html'

    def get_success_url(self):
        return reverse_lazy('listings:board_detail', kwargs={'pk': self.object.pk})


class BoardEditView(View):
    def get(self, request, pk):
        post = get_object_or_404(BoardPost, pk=pk)
        password_form = BoardPasswordForm()
        return render(request, 'listings/board_password.html', {
            'post': post, 'password_form': password_form, 'action': 'edit'
        })

    def post(self, request, pk):
        post = get_object_or_404(BoardPost, pk=pk)
        password_form = BoardPasswordForm(request.POST)
        if password_form.is_valid():
            if post.check_password(password_form.cleaned_data['password']):
                form = BoardPostForm(instance=post)
                form.fields.pop('raw_password')
                return render(request, 'listings/board_form.html', {
                    'form': form, 'object': post, 'edit_mode': True
                })
            else:
                messages.error(request, '비밀번호가 일치하지 않습니다.')
        return render(request, 'listings/board_password.html', {
            'post': post, 'password_form': password_form, 'action': 'edit'
        })


class BoardUpdateView(View):
    def post(self, request, pk):
        post = get_object_or_404(BoardPost, pk=pk)
        post.category = request.POST.get('category', post.category)
        post.writer_name = request.POST.get('writer_name', post.writer_name)
        post.title = request.POST.get('title', post.title)
        post.content = request.POST.get('content', post.content)
        if request.FILES.get('file1'):
            post.file1 = request.FILES['file1']
        post.save()
        return redirect('listings:board_detail', pk=post.pk)


class BoardDeleteView(View):
    def get(self, request, pk):
        post = get_object_or_404(BoardPost, pk=pk)
        password_form = BoardPasswordForm()
        return render(request, 'listings/board_password.html', {
            'post': post, 'password_form': password_form, 'action': 'delete'
        })

    def post(self, request, pk):
        post = get_object_or_404(BoardPost, pk=pk)
        password_form = BoardPasswordForm(request.POST)
        if password_form.is_valid():
            if post.check_password(password_form.cleaned_data['password']):
                post.delete()
                messages.success(request, '게시글이 삭제되었습니다.')
                return redirect('listings:board_list')
            else:
                messages.error(request, '비밀번호가 일치하지 않습니다.')
        return render(request, 'listings/board_password.html', {
            'post': post, 'password_form': password_form, 'action': 'delete'
        })
