from django import forms
from bd.models import Etudiant, Utilisateur

class EtudiantInscriptionForm(forms.ModelForm):
    prenom = forms.CharField(max_length=150, label="Prénom")
    nom = forms.CharField(max_length=150, label="Nom")
    email = forms.EmailField(label="Email")
    username = forms.CharField(max_length=150, label="Nom d'utilisateur")
    mdp = forms.CharField(widget=forms.PasswordInput, label="Mot de passe")
    filiere = forms.ChoiceField(
        choices=[
            ("GL", "Génie Logiciel"),
            ("SR", "Systèmes et Réseaux"),
            ("SE", "Software Engineering"),
            ("MI", "Maintenance IT"),
            ("MC", "Microsoft Certification"),
        ],
        label="Filière d'intérêt"
    )

    class Meta:
        model = Etudiant
        fields = ['numero_matricule', 'filiere']

    def save(self, commit=True):
        # Création de l'utilisateur
        utilisateur = Utilisateur.objects.create_user(
            email=self.cleaned_data['email'],
            username=self.cleaned_data['username'],
            nom=self.cleaned_data['nom'],
            prenom=self.cleaned_data['prenom'],
            privilege='ETU',
            mdp=self.cleaned_data['mdp'],
        )
        utilisateur.set_password(self.cleaned_data['mdp'])
        utilisateur.save()
        # Création du profil étudiant
        etudiant = super().save(commit=False)
        etudiant.utilisateur = utilisateur
        if commit:
            etudiant.save()
        return etudiant