# conversation_manager.py
import json
import os
from datetime import datetime
from config import APP_NAME

class ConversationManager:
    def __init__(self):
        self.conversations_dir = "conversations"
        os.makedirs(self.conversations_dir, exist_ok=True)
    
    def save_conversation(self, user_email, messages):
        """Sauvegarde une conversation"""
        try:
            filename = f"{user_email.replace('@', '_').replace('.', '_')}.json"
            filepath = os.path.join(self.conversations_dir, filename)
            
            conversation_data = {
                'user_email': user_email,
                'last_updated': datetime.now().isoformat(),
                'message_count': len(messages),
                'messages': messages
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(conversation_data, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"❌ Erreur sauvegarde conversation: {e}")
            return False
    
    def load_conversation(self, user_email):
        """Charge une conversation"""
        try:
            filename = f"{user_email.replace('@', '_').replace('.', '_')}.json"
            filepath = os.path.join(self.conversations_dir, filename)
            
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('messages', [])
            return []
        except Exception as e:
            print(f"❌ Erreur chargement conversation: {e}")
            return []
    
    def get_user_conversations(self, user_email):
        """Récupère l'historique des conversations pour l'historique"""
        messages = self.load_conversation(user_email)
        
        # Formate pour l'affichage historique
        history = []
        for i, msg in enumerate(messages):
            if msg.get('role') == 'user':
                history.append({
                    'date': msg.get('timestamp', 'Date inconnue'),
                    'question': msg.get('content', ''),
                    'response': self._get_next_assistant_response(messages, i)
                })
        
        return history
    
    def _get_next_assistant_response(self, messages, start_index):
        """Trouve la réponse de l'assistant après une question utilisateur"""
        for i in range(start_index + 1, len(messages)):
            if messages[i].get('role') == 'assistant':
                return messages[i].get('content', '')
        return "Réponse non trouvée"

# Instance globale
conversation_manager = ConversationManager()
