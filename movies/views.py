from django.shortcuts import render, redirect, get_object_or_404
from .models import Movie, Review, Petition, Vote
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
def index(request):
    search_term = request.GET.get('search')
    if search_term:
        movies = Movie.objects.filter(name__icontains=search_term)
    else:
        movies = Movie.objects.all()
    
    # Filter out movies with amount_left = 0 (only if amount_left is not None)
    available_movies = []
    for movie in movies:
        if movie.amount_left is None or movie.amount_left > 0:
            available_movies.append(movie)
    
    template_data = {}
    template_data['title'] = 'Movies'
    template_data['movies'] = available_movies
    return render(request, 'movies/index.html',
                  {'template_data': template_data})

def show(request, id):
    movie = Movie.objects.get(id=id)
    reviews = Review.objects.filter(movie=movie)
    template_data = {}
    template_data['title'] = movie.name
    template_data['movie'] = movie
    template_data['reviews'] = reviews
    return render(request, 'movies/show.html',
                  {'template_data': template_data})

@login_required
def create_review(request, id):
    if request.method == 'POST' and request.POST['comment'] != '':
        movie = Movie.objects.get(id=id)
        review = Review()
        review.comment = request.POST['comment']
        review.movie = movie
        review.user = request.user
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)

@login_required
def edit_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.user != review.user:
        return redirect('movies.show', id=id)
    if request.method == 'GET':
        template_data = {}
        template_data['title'] = 'Edit Review'
        template_data['review'] = review
        return render(request, 'movies/edit_review.html',
            {'template_data': template_data})
    elif request.method == 'POST' and request.POST['comment'] != '':
        review = Review.objects.get(id=review_id)
        review.comment = request.POST['comment']
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)

@login_required
def delete_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id,
        user=request.user)
    review.delete()
    return redirect('movies.show', id=id)

def petition_list(request):
    petitions = Petition.objects.all().order_by('-created_at')
    
    # Add user vote information to each petition
    for petition in petitions:
        if request.user.is_authenticated:
            user_vote = petition.votes.filter(user=request.user).first()
            petition.user_vote = user_vote.vote_type if user_vote else None
            petition.user_has_voted = user_vote is not None
        else:
            petition.user_vote = None
            petition.user_has_voted = False
    
    template_data = {
        'title': 'Movie Petitions',
        'petitions': petitions
    }
    return render(request, 'movies/petition_list.html', {'template_data': template_data})

@login_required
def create_petition(request):
    if request.method == 'POST':
        movie_title = request.POST.get('movie_title', '').strip()
        movie_description = request.POST.get('movie_description', '').strip()
        
        if movie_title and movie_description:
            petition = Petition()
            petition.movie_title = movie_title
            petition.movie_description = movie_description
            petition.created_by = request.user
            petition.save()
            messages.success(request, f'Petition for "{movie_title}" has been created successfully!')
            return redirect('movies.petition_list')
        else:
            messages.error(request, 'Please fill in all required fields.')
    
    template_data = {
        'title': 'Create New Petition'
    }
    return render(request, 'movies/create_petition.html', {'template_data': template_data})

@login_required
def vote_petition(request, petition_id):
    petition = get_object_or_404(Petition, id=petition_id)
    
    if request.method == 'POST':
        vote_type = request.POST.get('vote_type')
        
        if vote_type in ['yes', 'no']:
            # Check if user already voted
            existing_vote = Vote.objects.filter(petition=petition, user=request.user).first()
            
            if existing_vote:
                # Update existing vote
                existing_vote.vote_type = vote_type
                existing_vote.save()
                messages.info(request, f'Your vote has been updated to {vote_type}.')
            else:
                # Create new vote
                vote = Vote()
                vote.petition = petition
                vote.user = request.user
                vote.vote_type = vote_type
                vote.save()
                messages.success(request, f'Thank you for voting {vote_type}!')
        else:
            messages.error(request, 'Invalid vote type.')
    
    return redirect('movies.petition_list')