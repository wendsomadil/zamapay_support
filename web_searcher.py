import requests
from bs4 import BeautifulSoup
import googlesearch
import random
import time

class WebSearcher:
    def __init__(self):
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15'
        ]
    
    def search_web(self, query, num_results=3):
        """Recherche sur le web et extrait des informations"""
        try:
            print(f"🌐 Recherche web pour: {query}")
            
            # Recherche Google
            search_results = list(googlesearch.search(query, num_results=num_results, lang='fr'))
            
            results = []
            for url in search_results:
                try:
                    content = self._extract_content(url)
                    if content and len(content) > 100:
                        results.append({
                            'url': url,
                            'content': content[:500]  # Limiter la taille
                        })
                    
                    # Pause pour éviter le rate limiting
                    time.sleep(1)
                    
                except Exception as e:
                    print(f"❌ Erreur extraction {url}: {e}")
                    continue
            
            return results
            
        except Exception as e:
            print(f"❌ Erreur recherche web: {e}")
            return []
    
    def _extract_content(self, url):
        """Extrait le contenu textuel d'une URL"""
        try:
            headers = {'User-Agent': random.choice(self.user_agents)}
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Supprimer les scripts et styles
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Extraire le texte des balises pertinentes
            text = soup.get_text()
            
            # Nettoyer le texte
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text
            
        except Exception as e:
            print(f"❌ Erreur extraction contenu: {e}")
            return None
    
    def generate_web_response(self, query, web_results):
        """Génère une réponse basée sur les résultats web"""
        if not web_results:
            return None
        
        # Construire le contexte à partir des résultats
        context = "**Informations trouvées sur le web :**\n\n"
        for i, result in enumerate(web_results[:2], 1):
            context += f"**Source {i}:** {result['content']}\n\n"
        
        # Réponse structurée basée sur la recherche
        response = f"""**🔍 Recherche Web - {query}**

D'après mes recherches, voici les informations disponibles :

{context}

**💡 Analyse ZamaPay :**
Ces informations proviennent de sources externes. Pour des détails précis concernant nos services ZamaPay, je vous recommande de :

• Consulter notre centre d'aide officiel
• Contacter notre support au 01 23 45 67 89
• Vérifier les dernières mises à jour dans l'application

**📌 Note importante :** Les informations externes peuvent ne pas refléter nos dernières fonctionnalités ou tarifs."""

        return response
    