import discord
from discord.ext import commands
import aiohttp
import datetime


# class StrawpollFlags(commands.FlagConverter, delimiter=' ', prefix='--'):
#     is_private: bool
#     allow_comments: bool
#     deadline_at: datetime.datetime
#     allow_vpn_users: bool
#     results_visibility: str
#     is_multiple_choice: bool
#     multiple_choice_min: int
#     multiple_choice_max: int
#     description: str


class Polls(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="poll", aliases=["vote"])
    async def poll(self, ctx, *, question):
        """
        Create a simple poll without any options.

        :param question: The question to ask.
        """
        await ctx.message.delete()
        embed = discord.Embed(title=question, color=discord.Color.blurple())
        embed.set_footer(text=f"Poll created by {ctx.author}")
        msg = await ctx.send(embed=embed)
        await msg.add_reaction("👍")
        await msg.add_reaction("👎")

    @commands.command(name="strawpoll")
    async def strawpoll(self, ctx, *, args):
        """
        Create a poll in strawpoll.com. Separate title and options with |
        Eg: `are bots cool?|yes|no`

        :param title: The question of the poll
        :param options: The various options separated by |
        """
        args = args.split("|")
        title = args[0]
        options = args[1:]
        url = f"https://api.strawpoll.com/v3/polls"
        payload = {
            "title": title,
            "poll_options": [{"id": i, "value": option, "position": i, "type": "text"} for i, option in enumerate(options)],
            "type": "group_poll",
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as resp:
                data = await resp.json()
        embed = discord.Embed(
            title="Strawpoll Created",
            description=f"[Visit Poll]({data['url']})",
            color=discord.Color.blurple()
        )
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Polls(bot))
