// Gestion des formulaires de connexion et d'inscription
document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            e.preventDefault();
            handleFormSubmit(this, '/login/');  // URL directe au lieu de la balise Django
        });
    }
    
    if (registerForm) {
        registerForm.addEventListener('submit', function(e) {
            e.preventDefault();
            handleFormSubmit(this, '/register/');  // URL directe au lieu de la balise Django
        });
    }
});

function handleFormSubmit(form, url) {
    const formData = new FormData(form);
    
    fetch(url, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Erreur réseau');
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            // Afficher message de succès
            showNotification(data.message, 'success');
            
            // Rediriger après un court délai
            setTimeout(() => {
                if (data.redirect_url) {
                    window.location.href = data.redirect_url;
                } else {
                    window.location.reload();
                }
            }, 1500);
        } else {
            // Afficher erreurs
            showNotification(data.message, 'error');
            
            // Afficher les erreurs détaillées si disponibles
            if (data.errors) {
                data.errors.forEach(error => {
                    showNotification(error, 'error');
                });
            }
        }
    })
    .catch(error => {
        console.error('Erreur:', error);
        showNotification('Une erreur s\'est produite. Veuillez réessayer.', 'error');
    });
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function showNotification(message, type) {
    // Créer une notification toast
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg z-50 ${
        type === 'success' ? 'bg-success-green text-white' : 'bg-red-500 text-white'
    }`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // Supprimer après 5 secondes
    setTimeout(() => {
        notification.remove();
    }, 5000);
}

//verifier si les deux mots de passe sont identiques
document.addEventListener('DOMContentLoaded', function() {
    const registerForm = document.getElementById('registerForm');
    
    if (registerForm) {
        registerForm.addEventListener('submit', function(e) {
            const password = this.querySelector('input[name="mdp"]').value;
            const passwordConfirm = this.querySelector('input[name="mdp_confirm"]').value;
            
            if (password !== passwordConfirm) {
                e.preventDefault();
                showNotification('Les mots de passe ne correspondent pas.', 'error');
            }
        });
    }
});