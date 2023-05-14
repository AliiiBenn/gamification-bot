from abc import ABC, abstractmethod
from enum import Enum, auto

from plugins.gamification import database



class Competence(ABC):
    def __init__(self) -> None:
        self.table = database.CompetenceDatabaseTable()

    @abstractmethod
    async def add_experience(self, user_id : int, quantity_to_add : int) -> None:
        pass 
    
    @abstractmethod
    async def remove_experience(self, user_id : int, quantity_to_remove : int) -> None:
        pass
    
    @abstractmethod
    async def get_information(self, user_id : int) -> tuple[int, int]:
        pass
    
    
class Meditation(Competence):
    COMPETENCE_NAME = "MEDITATION"
    MULTIPLIER_PER_MINUTE = 10
    
    def __init__(self) -> None:
        super().__init__()
        
        
    def set_experience(self, minutes : int) -> int:
        return minutes * self.MULTIPLIER_PER_MINUTE
        
    async def add_experience(self, user_id : int, quantity_to_add : int) -> None:
        await database.CompetenceExperienceModifier.create().add_experience_to_competence(user_id, "MEDITATION", self.set_experience(quantity_to_add))
        
        
    async def remove_experience(self, user_id : int, quantity_to_remove : int) -> None:
        await database.CompetenceExperienceModifier.create().remove_experience_to_competence(user_id, "MEDITATION", self.set_experience(quantity_to_remove))
    
    async def get_information(self, user_id : int) -> tuple[int, int]:
        return await database.DatabaseInformationGetter.create().get_competence_information(user_id, "MEDITATION")
        


class Workout(Competence):
    COMPETENCE_NAME = "WORKOUT"
    
    def __init__(self) -> None:
        super().__init__()
        
        self.xp_per_minute = 2
        
    async def add_experience(self, user_id : int, quantity_to_add : int) -> None:
        await database.CompetenceExperienceModifier.create().add_experience_to_competence(user_id, "WORKOUT", quantity_to_add * self.xp_per_minute)
        
        
    async def remove_experience(self, user_id : int, quantity_to_remove : int) -> None:
        await database.CompetenceExperienceModifier.create().remove_experience_to_competence(user_id, "WORKOUT", quantity_to_remove * self.xp_per_minute)
    
    async def get_information(self, user_id : int) -> tuple[int, int]:
        return await database.DatabaseInformationGetter.create().get_competence_information(user_id, "WORKOUT")
        


class CompetenceType(Enum):
    MEDITATION = Meditation()
    WORKOUT = Workout()