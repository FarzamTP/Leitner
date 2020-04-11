from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth import authenticate, login, logout
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
def logout_user(request):
    if request.user.is_authenticated:
        logout(request)
        return redirect(index)


@login_required
def home(request):
    user_categories = Category.objects.all().filter(owner=request.user.userprofile)
    if request.user.is_authenticated:
        users = User.objects.all()
    else:
        users = None

    if request.method == "GET":
        return render(request, 'web/home.html', context={'user_categories': user_categories,
                                                         'users': users})
    else:
        action_type = request.POST.get('action_type')
        if action_type == "add_category":
            category_name = request.POST.get('category_name')
            category_color_hex_code = request.POST.get('color_hex_code')

            sender_category = Category(owner=request.user.userprofile, name=category_name, color=category_color_hex_code)
            sender_category.save()

            status = 200
        elif action_type == "edit_category":
            category_name = request.POST.get('category_name')
            category_color_hex_code = request.POST.get('color_hex_code')
            category_new_name = request.POST.get('new_category_name')

            sender_category = Category.objects.all().filter(owner=request.user.userprofile,
                                                            name=category_name)[0]

            sender_category.name = category_new_name
            sender_category.color = category_color_hex_code
            sender_category.save()

            status = 201

        elif action_type == "delete_category":
            category_name = request.POST.get('category_name')
            sender_category = Category.objects.all().filter(owner=request.user.userprofile,
                                                            name=category_name)[0]
            sender_category.delete()

            status = 202

        elif action_type == "inherit_category":
            if request.user.is_superuser:
                sender_id = request.POST.get('sender')
                receiver_id = request.POST.get('receiver')
                category_name = request.POST.get('category_name')

                sender = User.objects.all().filter(pk=sender_id)[0]
                receiver = User.objects.all().filter(pk=receiver_id)[0]

                sender_category = Category.objects.all().filter(owner=sender.userprofile, name=category_name)[0]

                category_flashcard = FlashCart.objects.all().filter(category=sender_category)

                receiver_category_name = str(category_name + '_Inherited_from_%s' % sender.username.strip())

                if not Category.objects.all().filter(owner=receiver.userprofile, name=receiver_category_name).exists():
                    receiver_category = sender_category
                    receiver_category.pk = None
                    receiver_category.name = receiver_category_name
                    receiver_category.number_of_flashcards = 0
                    receiver_category.number_of_lv1 = 0
                    receiver_category.number_of_lv2 = 0
                    receiver_category.number_of_lv3 = 0
                    receiver_category.number_of_lv4 = 0
                    receiver_category.number_of_lv5 = 0
                    receiver_category.owner = receiver.userprofile
                    receiver_category.save()

                    for flashcard in category_flashcard:
                        flashcard.pk = None
                        flashcard.lv = 1
                        flashcard.category = receiver_category
                        flashcard.save()
                else:
                    receiver_category = Category.objects.all().filter(owner=receiver.userprofile,
                                                                      name=receiver_category_name)[0]

                    receiver_category_flashcards = FlashCart.objects.all().filter(category=receiver_category)

                    receiver_category_flashcards_words = []
                    for flashcard in receiver_category_flashcards:
                        receiver_category_flashcards_words.append(flashcard.word)

                    for flashcard in category_flashcard:
                        if not flashcard.word in receiver_category_flashcards_words:
                            flashcard.pk = None
                            flashcard.category = receiver_category
                            flashcard.save()

                status = 203

        return render(request, 'web/home.html', context={'status': status,
                                                         'category_name': category_name,
                                                         'user_categories': user_categories,
                                                         'users': users})


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
        example = request.POST.get('example')

        category = Category.objects.all().filter(name=category_name)[0]

        flashcard = FlashCart.objects.create(category=category, word=word, definition=definition,
                                             synonyms=synonyms, example=example)
        flashcard.save()
        return redirect(category_page_render, category_name, lv, page)


@csrf_exempt
@login_required
def get_selected_user_categories(request):
    user_id = request.POST.get('user_id')
    user = User.objects.all().filter(pk=user_id)[0]
    user_categories = Category.objects.all().filter(owner=user.userprofile)
    user_categories_name = []
    for category in user_categories:
        user_categories_name.append(category.name)
    return JsonResponse(data={'user_categories_name': user_categories_name})


@csrf_exempt
def BOT_get_all_users_data(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            if user.is_superuser:
                login(request, user)
                all_users = User.objects.all().values()
                return JsonResponse(data={'users_data': list(all_users)})
            else:
                return JsonResponse(data={'users_data': 403})
        else:
            return JsonResponse(data={'users_data': 404})


@csrf_exempt
def BOT_get_user_detail(request):
    if request.method == "POST":
        user_id = request.POST.get('user_id')
        user = User.objects.all().filter(pk=user_id)[0]
        user_categories = Category.objects.all().filter(owner=user.userprofile)

        user_data = ":busts_in_silhouette: %s\nID: %s\nFirstName: %s\nLastName: %s\nEmail: " \
                    "%s\n<b>Categories</b>:\n" % (user.username, str(user.id), user.first_name,
                                                  user.last_name, user.email)

        if len(user_categories) != 0:
            for category in user_categories:
                user_data += "\t" + category.name + " (%d Flashcards)" % category.number_of_flashcards + "\n"
        else:
            user_data += "None"

        user_data += "Is active: %s\nIs staff: %s\nIs superuser: %s\nDate joined: %s\nLast login: %s\nPassword:%s " %\
                     (user.is_active, user.is_staff, user.is_superuser, user.date_joined, user.last_login, user.password)
        return JsonResponse(data={'user_detail': user_data})
