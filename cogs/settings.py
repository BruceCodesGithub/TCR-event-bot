import discord
from discord.ext import commands
import aiosqlite


class Settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.has_permissions(manage_guild=True)
    @commands.command(name="prefix", aliases=["setprefix", "set-prefix"])
    async def set_prefix(self, ctx, *, prefix=None):
        """
        Set the prefix for the bot.

        :param prefix: The prefix to set. If this is not specified, the bot will return the current prefix.
        """
        if prefix is None:
            p = await self.bot.get_prefix(ctx.message)
            return await ctx.send(f"The current prefix is `{p}`. To change it, use `{p}prefix <new prefix>`.")

        if len(prefix) > 10:
            return await ctx.send("Prefixes can't be longer than 10 characters")

        if await self.bot.get_prefix(ctx.message) == prefix:
            return await ctx.send("The prefix is already set to that")

        await self.bot.db.execute("INSERT OR REPLACE INTO prefixes VALUES (?, ?)", (ctx.guild.id, prefix))
        await self.bot.db.commit()


def setup(bot):
    bot.add_cog(Settings(bot))
