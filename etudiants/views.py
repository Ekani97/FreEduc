from django.shortcuts import render, redirect
from bd.models import Utilisateur, Etudiant



def home(request):
    return render(request, 'home.html')

def inscription_etudiant(request):
    if request.method == "POST":
        prenom = request.POST.get('prenom')
        nom = request.POST.get('nom')
        email = request.POST.get('email')
        username = request.POST.get('username')
        mdp = request.POST.get('mdp')
        numero_matricule = request.POST.get('numero_matricule')
        filiere = request.POST.get('filiere')

        # Création de l'utilisateur
        utilisateur = Utilisateur.objects.create_user(
            email=email,
            username=username,
            nom=nom,
            prenom=prenom,
            privilege='ETU'
        )
        utilisateur.set_password(mdp)
        utilisateur.save()

        # Création du profil étudiant
        Etudiant.objects.create(
            utilisateur=utilisateur,
            numero_matricule=numero_matricule,
            filiere=filiere
        )

        return render(request, "login_modal.html", {"show_login_modal": True})  # Redirigez vers la page de connexion ou autre

    return render(request, "inscription.html")