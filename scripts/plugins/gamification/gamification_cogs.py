import discord 
from discord.ext import commands

from abc import ABC, abstractmethod
from enum import Enum, auto
import aiosqlite

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
    
    async def create_table(self) -> None:
        if self.connection is None:
            raise MissingConnectionError("You must connect to the database before creating a table. Do this by calling the connect() method.")
        
        await self.connection.execute(
                """
                CREATE TABLE IF NOT EXISTS competence(
                    user_id INTEGER,
                    competence_type TEXT,
                    level INTEGER,
                    current_xp INTEGER,
                    xp_to_next_level INTEGER
                )
                """
            )
            
        await self.connection.commit()
    
    
class DatabaseUserAdder:
    def __init__(self):
        self.table = CompetenceDatabaseTable()
        
    async def add_user(self, user_id : int, competence_type : str, level : int, current_xp : int, xp_to_next_level : int) -> None:
        await self.table.connection.execute(
                """
                INSERT INTO competence(user_id, competence_type, level, current_xp, xp_to_next_level)
                VALUES(?, ?, ?, ?, ?)
                """,
                (user_id, competence_type, level, current_xp, xp_to_next_level)
            )
        
        await self.table.connection.commit()  
        
        
    @staticmethod
    async def create() -> "DatabaseUserAdder":
        return DatabaseUserAdder()
        
        

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
        
        
    async def add_experience_to_competence(self, user_id : int, competence_type : str, quantity_to_add : int) -> None:
        if not await DatabaseCompetenceChecker().check_if_user_competence_exists(user_id, competence_type):
            await DatabaseUserAdder().add_user(user_id, competence_type, 1, quantity_to_add, 100)
        
        await self.table.connection.execute(
                """
                UPDATE competence
                SET current_xp = current_xp + ?
                WHERE user_id = ? AND competence_type = ?
                """,
                (quantity_to_add, user_id, competence_type)
            )

        await self.table.connection.commit()
    
    async def remove_experience_to_competence(self, user_id : int, competence_type : str, quantity_to_remove : int) -> None:
        await self.table.connection.execute(
                """
                UPDATE competence
                SET current_xp = current_xp - ?
                WHERE user_id = ? AND competence_type = ?
                """,
                (quantity_to_remove, user_id, competence_type)
            )

        await self.table.connection.commit()
        
        
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
        
        return await cursor.fetchone()
    
    
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


class Competence(ABC):
    def __init__(self) -> None:
        self.table = CompetenceDatabaseTable()

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
    def __init__(self) -> None:
        super().__init__()
        
        self.xp_per_minute = 10
        
    async def add_experience(self, user_id : int, quantity_to_add : int) -> None:
        await CompetenceExperienceModifier.create().add_experience_to_competence(user_id, "MEDITATION", quantity_to_add * self.xp_per_minute)
        
        
    async def remove_experience(self, user_id : int, quantity_to_remove : int) -> None:
        await CompetenceExperienceModifier.create().remove_experience_to_competence(user_id, "MEDITATION", quantity_to_remove * self.xp_per_minute)
    
    async def get_information(self, user_id : int) -> tuple[int, int]:
        information = await DatabaseInformationGetter.create().get_competence_information(user_id, "MEDITATION")
        if information is None:
            return (0, 0)
        return information


class Workout(Competence):
    def __init__(self) -> None:
        super().__init__()
        
        self.xp_per_minute = 10
        
    async def add_experience(self, user_id : int, quantity_to_add : int) -> None:
        await CompetenceExperienceModifier.create().add_experience_to_competence(user_id, "WORKOUT", quantity_to_add * self.xp_per_minute)
        
        
    async def remove_experience(self, user_id : int, quantity_to_remove : int) -> None:
        await CompetenceExperienceModifier.create().remove_experience_to_competence(user_id, "WORKOUT", quantity_to_remove * self.xp_per_minute)
    
    async def get_information(self, user_id : int) -> tuple[int, int]:
        information = await DatabaseInformationGetter.create().get_competence_information(user_id, "WORKOUT")
        if information is None:
            return (0, 0)
        return information


class CompetenceType(Enum):
    MEDITATION = Meditation()
    WORKOUT = Workout()
    
    

class Gamification(commands.Cog):
    def __init__(self, bot : commands.Bot) -> None:
        self.bot = bot
        
        
    
    @commands.Cog.listener("on_ready")
    async def load_table(self) -> None:
        self.table = CompetenceDatabaseTable()
        await self.table.connect()
        
    
    @commands.hybrid_command(name="setup_table")
    async def setup_table(self, ctx : commands.Context) -> discord.Message:
        table = CompetenceDatabaseTable()
        await table.connect()
        await table.create_table()
        
        return await ctx.send("Table created.")
        
        
    @commands.hybrid_command(name="competence")
    async def get_competence_information(self, ctx : commands.Context, competence : CompetenceType) -> None:
        level, xp = await competence.value.get_information(ctx.author.id)
        
        embed = discord.Embed(
            title="Niveau actuel en méditation",
            description=f"Vous êtes actuellement au niveau {level} en méditation.\nVous avez {xp} points d'expérience sur 100 points pour passer au niveau 2.",
            color=discord.Color.green()
        )
        
        
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
        
        
        await ctx.send(embed=embed)
        
        
    @commands.hybrid_command(name="add_experience")
    async def add_experience(self, ctx : commands.Context, competence : CompetenceType, xp : int) -> None:
        await competence.value.add_experience(ctx.author.id, xp)
        
        embed = discord.Embed(
            title="Experience modifié",
            description=f"Vous avez gagné {xp} points d'expérience.",
            color=discord.Color.green()
        )
        
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
        
        await ctx.send(embed=embed)
        
        
        
        
async def setup(bot : commands.Bot) -> None:
    await bot.add_cog(Gamification(bot))