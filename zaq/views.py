from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Category
from .forms import EngineForm


# Create your views here.

@login_required
def register_engine(request):
    categories = Category.objects.filter(
        active=True).order_by('order', 'name')

    return render(
        request,
        'zaq/register_engine.html',
        {
            'categories': categories,
        }
    )


@login_required
def engine_details(request, category_id):
    category = get_object_or_404(Category,
                                 pk=category_id,
                                 active=True)

    if request.method == 'POST':

        form = EngineForm(request.POST,
                          category=category)

        if form.is_valid():
            engine = form.save(commit=False)
            engine.category = category
            engine.operator = request.user
            engine.save()
            form.save_m2m()

            messages.success(
                request,
                'Motor registrado correctamente'
            )

            return redirect('register_engine')

    else:
        code_bar = request.GET.get('code_bar')
        form = EngineForm(
            initial={'code_bar': code_bar},
            category=category)

    return render(
        request,
        'zaq/engine_details.html',
        {
            'form': form,
            'category': category,
        }
    )
