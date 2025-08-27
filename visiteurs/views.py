from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.http import JsonResponse
from bd.models import Utilisateur, Etudiant
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
def home(request):
    return render(request, 'index.html')

def login_modal(request):
    return render(request, 'login_modal.html')

def register_modal(request):
    return render(request, 'register_modal.html')

@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            # Vérifier si l'utilisateur existe
            user = Utilisateur.objects.get(email=email)
            
            # Authentifier l'utilisateur
            authenticated_user = authenticate(request, email=user.nom, password=password)
            
            if authenticated_user is not None:
                login(request, authenticated_user)
                
                # Réponse JSON pour les requêtes AJAX
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'message': 'Connexion réussie!',
                        'redirect_url': '/dashboard/'  # URL de redirection après connexion
                    })
                return redirect('dashboard')
            else:
                messages.error(request, 'Mot de passe incorrect.')
                
        except Utilisateur.DoesNotExist:
            messages.error(request, 'Aucun compte trouvé avec cet email.')
        
        # Réponse pour les requêtes AJAX en cas d'erreur
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': 'Échec de la connexion. Veuillez vérifier vos identifiants.'
            }, status=400)
    
    # Pour les requêtes GET, afficher le modal via le template principal
    return render(request, 'index.html')

@csrf_exempt
def register_view(request):
    if request.method == 'POST':
        # Récupérer les données du formulaire
        nom = request.POST.get('nom')
        prenom = request.POST.get('prenom')
        email = request.POST.get('email')
        mdp = request.POST.get('mdp')
        mdp_confirm = request.POST.get('mdp_confirm')
        filiere = request.POST.get('filiere')

        # Validation des données
        errors = []
                      
        if mdp != mdp_confirm:
            errors.append('Les mots de passe ne correspondent pas.')
        
        if Utilisateur.objects.filter(email=email).exists():
            errors.append('Un compte avec cet email existe déjà.')
    
        if errors:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': 'Erreurs de validation',
                    'errors': errors
                }, status=400)
            
            for error in errors:
                messages.error(request, error)
            return render(request, 'index.html')
        
        try:
            # Créer l'utilisateur
            user = Utilisateur.objects.create_user(
                
                nom=nom,
                prenom=prenom,
                email=email,
                mdp=mdp,
                etat_compte='ACT',
                privilege='ETU'
            )
            
            # Créer le profil étudiant
            Etudiant.objects.create(
                utilisateur=user,
                filiere=filiere
            )
            
            # Connecter automatiquement l'utilisateur
            login(request, user)
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Compte créé avec succès!',
                    'redirect_url': 'home'  # URL de redirection après inscription
                })
            
            return redirect('dashboard')
            
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': f'Erreur lors de la création du compte: {str(e)}'
                }, status=500)
            
            messages.error(request, f'Erreur lors de la création du compte: {str(e)}')
            return render(request, 'index.html')
    
    # Pour les requêtes GET, afficher le modal via le template principal
    return render(request, 'index.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'Vous avez été déconnecté avec succès.')
    return redirect('home')
