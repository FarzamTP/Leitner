from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt

from .models import Category, FlashCart


# Create your views here.

def index(request):
    if not request.user.is_authenticated:
        if request.method == "GET":
            return render(request, 'web/index.html')
        else:
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return redirect(home)
            else:
                return HttpResponse("User not found!")
    else:
        return redirect(home)


@login_required
def home(request):
    user_categories = Category.objects.all().filter(owner=request.user.userprofile)
    if request.method == "GET":
        return render(request, 'web/home.html', context={'user_categories': user_categories})
    else:
        action_type = request.POST.get('action_type')
        if action_type == "add_category":
            category_name = request.POST.get('category_name')
            category_color_hex_code = request.POST.get('color_hex_code')

            category = Category(owner=request.user.userprofile, name=category_name, color=category_color_hex_code)
            category.save()

            status = 200
        elif action_type == "edit_category":
            category_name = request.POST.get('category_name')
            category_color_hex_code = request.POST.get('color_hex_code')
            category_new_name = request.POST.get('new_category_name')

            category = Category.objects.all().filter(owner=request.user.userprofile,
                                                     name=category_name)[0]

            category.name = category_new_name
            category.color = category_color_hex_code
            category.save()

            status = 201

        elif action_type == "delete_category":
            category_name = request.POST.get('category_name')
            category = Category.objects.all().filter(owner=request.user.userprofile,
                                                     name=category_name)[0]
            category.delete()

            status = 202
        return render(request, 'web/home.html', context={'status': status,
                                                         'category_name': category_name,
                                                         'user_categories': user_categories})


@csrf_exempt
@login_required
def retrieve_category_color(request):
    if request.method == "POST":
        category_name = request.POST.get('category_name')

        category = Category.objects.all().filter(owner=request.user.userprofile,
                                                 name=category_name)[0]
        category_color = category.color
        return JsonResponse(data={'category_color': category_color})


@login_required
def category_page_render(request, category_name, lv, page):
    has_next_page = False
    has_previous_page = False
    next_page_num = None
    previous_page_num = None

    category = Category.objects.all().filter(owner=request.user.userprofile,
                                             name=category_name)[0]
    if lv != 0:
        category_flashcards = FlashCart.objects.all().filter(category=category, lv=lv)
    else:
        category_flashcards = FlashCart.objects.all().filter(category=category)

    if page < len(category_flashcards) - 1:
        has_next_page = True
        next_page_num = page + 1
    if page > 0:
        has_previous_page = True
        previous_page_num = page - 1

    if len(category_flashcards) != 0:
        category_lv_len = len(category_flashcards)
        selected_flashcard = category_flashcards[page]
    else:
        category_lv_len = 0
        selected_flashcard = None

    if request.method == "POST":
        action_type = request.POST.get('action_type')
        flashcard_id = request.POST.get('flashcard_id')

        flashcard = FlashCart.objects.all().filter(pk=flashcard_id)[0]

        if action_type == "lv_up":
            if flashcard.lv != 5:
                if flashcard.lv == 1:
                    flashcard.category.number_of_lv2 += 1
                    flashcard.category.number_of_lv1 -= 1
                elif flashcard.lv == 2:
                    flashcard.category.number_of_lv3 += 1
                    flashcard.category.number_of_lv2 -= 1
                elif flashcard.lv == 3:
                    flashcard.category.number_of_lv4 += 1
                    flashcard.category.number_of_lv3 -= 1
                elif flashcard.lv == 4:
                    flashcard.category.number_of_lv5 += 1
                    flashcard.category.number_of_lv4 -= 1
                flashcard.lv += 1

        elif action_type == "lv_down":
            if flashcard.lv != 1:
                if flashcard.lv == 2:
                    flashcard.category.number_of_lv2 -= 1
                    flashcard.category.number_of_lv1 += 1
                elif flashcard.lv == 3:
                    flashcard.category.number_of_lv3 -= 1
                    flashcard.category.number_of_lv2 += 1
                elif flashcard.lv == 4:
                    flashcard.category.number_of_lv4 -= 1
                    flashcard.category.number_of_lv3 += 1
                elif flashcard.lv == 5:
                    flashcard.category.number_of_lv5 -= 1
                    flashcard.category.number_of_lv4 += 1

                flashcard.lv -= 1

        if page > 0:
            page -= 1
        else:
            page = 0

        flashcard.save()
        flashcard.category.save()

        return redirect(category_page_render, category_name, lv, page)

    return render(request, 'web/category.html', context={'category': category,
                                                         'selected_flashcard': selected_flashcard,
                                                         'page': page,
                                                         'lv': lv,
                                                         'category_lv_len': category_lv_len,
                                                         'has_next_page': has_next_page,
                                                         'has_previous_page': has_previous_page,
                                                         'next_page_num': next_page_num,
                                                         'previous_page_num': previous_page_num,
                                                         'current_page_demonstrator': page + 1})


@csrf_exempt
@login_required
def add_new_flashcard(request):
    if request.method == "POST":
        category_name = request.POST.get('category_name')
        lv = request.POST.get('lv')
        page = request.POST.get('page')
        word = request.POST.get('word')
        definition = request.POST.get('definition')
        synonyms = request.POST.get('synonyms')
        antonyms = request.POST.get('antonyms')
        example = request.POST.get('example')

        category = Category.objects.all().filter(name=category_name)[0]

        flashcard = FlashCart.objects.create(category=category, word=word, definition=definition,
                                             synonyms=synonyms, antonyms=antonyms, example=example)
        flashcard.save()
        print("category_name", category_name)
        print("page:", page)
        print("lv:", lv)
        return redirect(category_page_render, category_name, lv, page)