from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from typing import Dict, List, Optional


class Task(BaseModel):
    id: int
    user_id: int
    posts_id: List[int] = []  
    channels_id: List[int]  
    description: Optional[str] = None
    schedule_delay: Optional[timedelta] = None 
    posted_date: Optional[datetime] = Field(default_factory=datetime.now)
    status: str = "pending"  

    class Config:
        arbitrary_types_allowed = True

    def mark_completed(self):
        """Marque la tâche comme terminée."""
        self.status = "completed"

    def mark_failed(self):
        """Marque la tâche comme échouée."""
        self.status = "failed"
        
    def mak_scheduled(self):
        """Marque la tâche comme planifiée."""
        self.status = "scheduled"

    def mak_saved(self):
        """Marque la tâche comme enregistrée."""
        self.status = "saved"
        
    def add_channel(self, channel_id: int):
        """Ajoute un canal à la liste s'il n'existe pas déjà."""
        if channel_id not in self.channels_id:
            self.channels_id.append(channel_id)

    def remove_channel(self, channel_id: int):
        """Supprime un canal de la liste s'il est présent."""
        if channel_id in self.channels_id:
            self.channels_id.remove(channel_id)

    def update_description(self, new_description: str):
        """Met à jour la description de la tâche."""
        self.description = new_description

    def add_post(self, post_id: int):
        """Ajoute un post à la tâche s'il n'est pas déjà présent."""
        if post_id not in self.posts_id:
            self.posts_id.append(post_id)
            
    def get_tsk_status(self):
        """Retourne le status actuel de la tâche."""
        if self.status == "completed":
            return 1
        elif self.status == "failed":
            return 0
        else:
            return 2

    def remove_post(self, post_id: int):
        """Supprime un post de la tâche s'il est présent."""
        if post_id in self.posts_id:
            self.posts_id.remove(post_id)

    def to_dict(self):
        """Convertit la tâche en dictionnaire."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "posts_id": self.posts_id,
            "channels_id": self.channels_id,
            "description": self.description,
            "schedule_delay": str(self.schedule_delay),
            "posted_date": self.posted_date.isoformat(),
            "status": self.status
        }



