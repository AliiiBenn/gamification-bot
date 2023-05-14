import discord 
from discord.ext import commands

from plugins.gamification import database, competences



class Gamification(commands.Cog):
    def __init__(self, bot : commands.Bot) -> None:
        self.bot = bot
        
        
    
    @commands.Cog.listener("on_ready")
    async def load_table(self) -> None:
        self.table = database.CompetenceDatabaseTable()
        await self.table.connect()
        
    
    @commands.hybrid_command(name="setup_table")
    async def setup_table(self, ctx : commands.Context) -> discord.Message:
        
        table = database.CompetenceDatabaseTable()
        await table.connect()
        await table.create_table()
        
        return await ctx.send("Table created.")
    
    @commands.hybrid_command(name="delete_table")
    async def delete_table(self, ctx : commands.Context) -> discord.Message:
        table = database.CompetenceDatabaseTable()
        await table.connect()
        await table.reset_table()
        
        return await ctx.send("Table deleted.")
    
        
        
    @commands.hybrid_command(name="competence")
    async def get_competence_information(self, ctx : commands.Context, competence : competences.CompetenceType) -> None:
        level, xp = await competence.value.get_information(ctx.author.id)
        
        embed = discord.Embed(
            title=f"Niveau actuel en {competence.name}",
            description=f"Vous êtes actuellement au niveau {level} en {competence.name}.\nVous avez {xp} points d'expérience sur 100 points pour passer au niveau 2.",
            color=discord.Color.green()
        )
        
        
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
        
        
        await ctx.send(embed=embed)
        
        
    @commands.hybrid_command(name="add_experience")
    async def add_experience(self, ctx : commands.Context, competence : competences.CompetenceType, xp : int) -> None:
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