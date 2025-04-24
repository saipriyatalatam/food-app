from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import FoodItem, RecommendationHistory
from .utils import get_recommendations
from django.conf import settings


#login view
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        #If the user details are available in the Database and authenticated
        if user:
            login(request, user)
            return redirect('home')
        messages.error(request, 'Invalid credentials')
    return render(request, 'login.html')


#signup view
def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)   #Using Django inbuilt UserCreationForm
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return redirect('home')
    else:
        form = UserCreationForm()   #Django inbuilt usercreationform is rendered to frontend
    return render(request, 'signup.html', {'form': form})


#logout view
def logout_view(request):
    logout(request)
    return redirect('login')

#Allows only authenticated users
@login_required     
def home_view(request):
    food_groups = FoodItem.objects.values('food_group').distinct()
    food_items = FoodItem.objects.all()
    selected_group = request.GET.get('food_group', '')

    if selected_group:
        food_items = food_items.filter(food_group=selected_group)     #filter based on food group

    if request.method == 'POST':
        food_name = request.POST.get('food_item')
        if not food_name:
            messages.error(request, 'Please select a food item.')
            return redirect('home')

        try:
            result = get_recommendations(food_name, selected_features=settings.SELECTED_FEATURES)
            best = result.get('best_recommendation', [])
            # Sample recommendations from get_recommendation function
            # [['Amaranth seed, black (Amaranthus cruentus)', 'Subset 37', 'Barley (Hordeum vulgare)', 'Bajra (Pennisetum typhoideum)', 'Wheat flour, atta (Triticum aestivum)', 1.0446080903490655, 2.0, 0.08861111111111113, 0.5666096007300884]]
            

            if not best or len(best[0]) < 5:
                messages.error(request, 'No valid recommendations found for this food item.')
                return redirect('home')

            recommended_names = best[0][2:5]

            # Handle cases where a recommendation might not exist
            recommendations = []
            for name in recommended_names:
                food = get_object_or_404(FoodItem, food_name=name)
                recommendations.append(food)

            selected_food = get_object_or_404(FoodItem, food_name=food_name)

            #Load the recommendations to the Database
            RecommendationHistory.objects.create(
                user=request.user,
                selected_food=selected_food,
                recommended_food_1=recommendations[0],
                recommended_food_2=recommendations[1],
                recommended_food_3=recommendations[2],
            )

            return render(request, 'home.html', {
                'food_groups': food_groups,
                'food_items': food_items,
                'selected_group': selected_group,
                'recommendations': recommendations,
                'selected_food': selected_food,
            })

        except FoodItem.DoesNotExist:
            messages.error(request, 'Selected or recommended food item does not exist.')
        except ValueError as e:
            messages.error(request, f'Error: {e}')
        except Exception as e:
            messages.error(request, f'Unexpected error generating recommendations: {e}')
        return redirect('home')

    return render(request, 'home.html', {
        'food_groups': food_groups,
        'food_items': food_items,
        'selected_group': selected_group,
    })


#history view - Displays all the recommendation history of a user
@login_required
def history_view(request):
    history = RecommendationHistory.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'history.html', {'history': history})
