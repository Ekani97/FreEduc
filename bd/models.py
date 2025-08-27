from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


# ---------------------------
# Utilisateur (compte Django)
# ---------------------------
class Utilisateur(AbstractUser):
    PRIVILEGE_CHOICES = [
        
        ('ETU', 'Etudiant'),
        ('ADM', 'Administrateur'),
    ]
    ETAT_COMPTE_CHOICES = [
        ('ACT', 'Actif'),
        ('INA', 'Inactif'),
        ('SUS', 'Suspendu'),    
    ]
    nom = models.CharField(max_length=150)
    prenom = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    mdp = models.CharField(max_length=128)
    privilege = models.CharField(max_length=3, choices=PRIVILEGE_CHOICES, default='ETU')
    etat_compte = models.CharField(max_length=3, choices=ETAT_COMPTE_CHOICES, default='ACT')
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nom','prenom','privilege','etat_compte']

    def __str__(self):
        return f"{self.username} ({self.get_privilege_display()})"


# Proxies pratiques (facultatif mais utile)
class VisiteurManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(privilege='ETU')


class Visiteur(Utilisateur):
    objects = VisiteurManager()
    class Meta:
        proxy = True
        verbose_name = "Visiteur"
        verbose_name_plural = "Visiteurs"


class AdministrateurManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(privilege='ADM')


class Administrateur(Utilisateur):
    objects = AdministrateurManager()
    class Meta:
        proxy = True
        verbose_name = "Administrateur"
        verbose_name_plural = "Administrateurs"


# ---------------------------
# Système Chatbot
# ---------------------------
class SystemeChatbot(models.Model):
    id_bot = models.AutoField(primary_key=True)
    version = models.CharField(max_length=50)

    def __str__(self):
        return f"Bot {self.id_bot} v{self.version}"


# ---------------------------
# Catalogue (contenus consultables)
# ---------------------------
class Catalogue(models.Model):
    id_catalogue = models.AutoField(primary_key=True)
    contenu = models.TextField()
    description = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Catalogue #{self.id_catalogue}"


class ConsultationCatalogue(models.Model):
    """Qui (visiteur) a consulté quel catalogue et quand"""
    visiteur = models.ForeignKey(
        Utilisateur,
        on_delete=models.CASCADE,
       
        related_name="consultations_catalogue",
    )
    catalogue = models.ForeignKey(Catalogue, on_delete=models.CASCADE, related_name="consultations")
    date = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "Consultation de catalogue"
        verbose_name_plural = "Consultations de catalogue"
        unique_together = ("visiteur", "catalogue", "date")


# ---------------------------
# Questions / Réponses
# ---------------------------
class Question(models.Model):
    id_question = models.AutoField(primary_key=True)
    contenu = models.TextField()
    type = models.CharField(max_length=50, blank=True)
    auteur = models.ForeignKey(
        Utilisateur, on_delete=models.SET_NULL, null=True, related_name="questions_posees"
    )
    chatbot = models.ForeignKey(
        SystemeChatbot, on_delete=models.SET_NULL, null=True, blank=True, related_name="questions"
    )
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Q{self.id_question} par {self.auteur or 'inconnu'}"


class Reponse(models.Model):
    id_reponse = models.AutoField(primary_key=True)
    contenu = models.TextField()
    type = models.CharField(max_length=50, blank=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="reponses")
    # Provenance: généralement le chatbot ; on garde un lien optionnel vers un expéditeur humain
    provenance_chatbot = models.ForeignKey(
        SystemeChatbot, on_delete=models.SET_NULL, null=True, blank=True, related_name="reponses"
    )
    expediteur_humain = models.ForeignKey(
        Utilisateur, on_delete=models.SET_NULL, null=True, blank=True, related_name="reponses_envoyees"
    )
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Réponse {self.id_reponse} à Q{self.question.id_question}"


# ---------------------------
# Notifications & Réceptions
# ---------------------------
class Notification(models.Model):
    id_notif = models.AutoField(primary_key=True)
    expediteur = models.ForeignKey(
        Utilisateur, on_delete=models.SET_NULL, null=True, related_name="notifications_envoyees"
    )
    objet = models.CharField(max_length=150)
    contenu = models.TextField(blank=True)
    date = models.DateField(default=timezone.now)
    heure = models.TimeField(default=lambda: timezone.now().time())

    def __str__(self):
        return f"Notif {self.id_notif}: {self.objet}"
    

class Reception(models.Model):
    """
    Table 'Recevoir' du diagramme : relie Notification <-> Utilisateur (destinataire)
    et permet de suivre la réception/lecture.
    """
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, related_name="receptions")
    destinataire = models.ForeignKey(
        Utilisateur, on_delete=models.CASCADE, related_name="receptions"
    )
    recu_le = models.DateTimeField(default=timezone.now)
    lu_le = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("notification", "destinataire")
        verbose_name = "Réception"
        verbose_name_plural = "Réceptions"

    def __str__(self):
        return f"{self.destinataire} ← Notif {self.notification.id_notif}"


# ---------------------------
# Étudiant (profil)
# ---------------------------
class Etudiant(models.Model):
    utilisateur = models.OneToOneField(
        Utilisateur,
        on_delete=models.CASCADE,
        related_name="profil_etudiant",
        limit_choices_to={"privilege": "ETU"},
    )
    idEtudiant = models.AutoField(primary_key=True)
    filiere = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.utilisateur.get_full_name() or self.utilisateur.username} - {self.numero_matricule}"


# ---------------------------
# FAQ
# ---------------------------
class FAQ(models.Model):
    id_faq = models.AutoField(primary_key=True)
    question = models.CharField(max_length=255)
    reponse = models.TextField()
    date = models.DateField(default=timezone.now)

    def __str__(self):
        return f"FAQ #{self.id_faq} - {self.question[:40]}"


# ---------------------------
# Test d’orientation
# ---------------------------
class TestOrientation(models.Model):
    id_test = models.AutoField(primary_key=True)
    etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE, related_name="tests_orientation")
    profil = models.CharField(max_length=100)
    question = models.TextField()
    reponse = models.TextField()
    date = models.DateField(default=timezone.now)

    def __str__(self):
        return f"Test {self.id_test} - {self.etudiant}"


# ---------------------------
# Paiements (par étudiants)
# ---------------------------
class Paiement(models.Model):
    id_paiement = models.AutoField(primary_key=True)
    etudiant = models.ForeignKey(Etudiant, on_delete=models.PROTECT, related_name="paiements")
    montant_transaction = models.DecimalField(max_digits=12, decimal_places=2)
    contact = models.CharField(max_length=50)  # téléphone ou email de contact
    numero_crediteur = models.CharField(max_length=50)
    numero_debiteur = models.CharField(max_length=50)
    date = models.DateField(default=timezone.now)
    heure = models.TimeField(default=lambda: timezone.now().time())
    gere_par = models.ForeignKey(
        Utilisateur,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="paiements_geres",
        limit_choices_to={"privilege": "ADM"},
        help_text="Administrateur qui a validé/traité le paiement",
    )

    class Meta:
        indexes = [models.Index(fields=["date"]), models.Index(fields=["etudiant"])]

    def __str__(self):
        return f"Paiement {self.id_paiement} - {self.etudiant} - {self.montant_transaction} FCFA"
