import aiosqlite
import logging

logger = logging.getLogger('discord')


class Singleton(type):
    _instances = {} # type: ignore
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class MissingConnectionError(Exception):
    """Error raised when the database is not connected."""



class CompetenceDatabaseTable(metaclass=Singleton):
    def __init__(self):
        self.connection = None
    
    async def connect(self) -> None:
        self.connection = await aiosqlite.connect("data/databases/competence.db")
        
    async def execute_query(self, query: str, *args) -> None:
        if self.connection is None:
            raise MissingConnectionError("You must connect to the database before executing queries. Do this by calling the connect() method.")
        
        await self.connection.execute(query, *args)
        await self.connection.commit()
    
    async def create_table(self) -> None:
        
        query = """
                CREATE TABLE IF NOT EXISTS competence(
                    user_id INTEGER,
                    competence_type TEXT,
                    level INTEGER,
                    current_xp INTEGER,
                    xp_to_next_level INTEGER
                )
                """


        logger.info("Creating competence table...")
        return await self.execute_query(query)                
            
    async def reset_table(self) -> None:
        query = """delete from competence"""

        logger.info("Resetting competence table...")
        return await self.execute_query(query)        
      

class DatabaseUserAdder:
    def __init__(self, 
                 user_id : int, 
                 competence_type : str, 
                 level : int, 
                 current_xp : int, 
                 xp_to_next_level : int) -> None:
        
        
        self.table = CompetenceDatabaseTable()
        self.connection = self.table.connection
        
        self.user_id = user_id
        self.competence_type = competence_type
        self.level = level
        self.current_xp = current_xp
        self.xp_to_next_level = xp_to_next_level
        
        
    async def add(self) -> None:
        """Add the user to the database based on the given information during the creation of the object."""
        await self.connection.execute(
                """
                INSERT INTO competence(user_id, competence_type, level, current_xp, xp_to_next_level)
                VALUES(?, ?, ?, ?, ?)
                """,
                (self.user_id, self.competence_type, self.level, self.current_xp, self.xp_to_next_level)
            )
        
        await self.connection.commit()
        
        
    @staticmethod
    def create_empty(user_id : int, competence_type : str) -> "DatabaseUserAdder":
        return DatabaseUserAdder(user_id, competence_type, 1, 0, 100)
    
    @staticmethod
    def create_custom(user_id : int, competence_type : str, level : int, current_xp : int, xp_to_next_level : int) -> "DatabaseUserAdder":
        return DatabaseUserAdder(user_id, competence_type, level, current_xp, xp_to_next_level)
        
        

class DatabaseCompetenceChecker:
    def __init__(self) -> None:
        self.table = CompetenceDatabaseTable()
    
    async def check_if_user_competence_exists(self, user_id : int, competence_type : str) -> bool:
        cursor = await self.table.connection.execute(
                """
                SELECT user_id
                FROM competence
                WHERE user_id = ? AND competence_type = ?
                """,
                (user_id, competence_type)
            )
        
        return await cursor.fetchone() is not None        
        

class CompetenceExperienceModifier:
    def __init__(self) -> None:
        self.table = CompetenceDatabaseTable()
        
    async def check_if_user_competence_exists(self, user_id : int, competence_type : str) -> bool:
        return await DatabaseCompetenceChecker().check_if_user_competence_exists(user_id, competence_type)
    
    async def add_user_competence(self, user_id : int, competence_type : str) -> None:
        await DatabaseUserAdder.create_empty(user_id, competence_type).add()
        
    async def add_experience_to_user(self, user_id : int, quantity_to_add : int) -> None:
        await self.table.connection.execute(
                """
                UPDATE competence
                SET current_xp = current_xp + ?
                WHERE user_id = ?
                """,
                (quantity_to_add, user_id)
            )

        await self.table.connection.commit()
        
    async def remove_experience_to_user(self, user_id : int, quantity_to_remove : int) -> None:
        await self.table.connection.execute(
                """
                UPDATE competence
                SET current_xp = current_xp - ?
                WHERE user_id = ?
                """,
                (quantity_to_remove, user_id)
            )

        await self.table.connection.commit()
        
    async def add_experience_to_competence(self, user_id : int, competence_type : str, quantity_to_add : int) -> None:
        if not await self.check_if_user_competence_exists(user_id, competence_type):
            return await self.add_user_competence(user_id, competence_type)
        return await self.add_experience_to_user(user_id, quantity_to_add)
    
    async def remove_experience_to_competence(self, user_id : int, competence_type : str, quantity_to_remove : int) -> None:
        if not await self.check_if_user_competence_exists(user_id, competence_type):
            raise ValueError("The user does not have this competence. You cannot remove experience from a competence that does not exist.")
        
        return await self.remove_experience_to_user(user_id, quantity_to_remove)
        
        
    @staticmethod
    def create() -> "CompetenceExperienceModifier":
        return CompetenceExperienceModifier()

    
class DatabaseInformationGetter:
    def __init__(self):
        self.table = CompetenceDatabaseTable()
    
    async def get_competence_information(self, user_id : int, competence_type : str) -> tuple[int, int]:
        cursor = await self.table.connection.execute(
                """
                SELECT level, current_xp
                FROM competence
                WHERE user_id = ? AND competence_type = ?
                """,
                (user_id, competence_type)
            )
        
        value = await cursor.fetchone()
        
        if value is None:
            return (0, 0)
        return value
    
    
    async def get_user_information(self, user_id : int) -> list[tuple[int, int, int, int]]:
        cursor = await self.table.connection.execute(
                """
                SELECT competence_type, level, current_xp, xp_to_next_level
                FROM competence
                WHERE user_id = ?
                """,
                (user_id,)
            )
        
        return await cursor.fetchall()
    
    
    @staticmethod
    def create() -> "DatabaseInformationGetter":
        return DatabaseInformationGetter()


class DatabaseLevelModifier:
    def __init__(self) -> None:
        self.table = CompetenceDatabaseTable()
        
        
    


    
  