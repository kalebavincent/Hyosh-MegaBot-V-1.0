import json

class LangManager:
    """Classe pour gérer la langue globale de l'application"""
    
    def __init__(self, default_lang="fr"):
        self.lang = self.load_lang(default_lang)
        self.current_lang = default_lang

    def load_lang(self, lang: str):
        """Charge le fichier de langue spécifié."""
        try:
            with open(f"lang/{lang}.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Langue {lang} non trouvée, utilisation de 'fr' comme langue par défaut.")
            return self.load_lang("fr")
    
    def set_lang(self, lang: str):
        """Change la langue de l'application et recharge les données de la langue."""
        self.current_lang = lang
        self.lang = self.load_lang(lang)
    
    def get_lang(self):
        """Retourne les données de la langue actuelle."""
        return self.lang
