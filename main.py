import re
import discord  # pycord
from discord.ext import commands
from discord.ext import tasks
import aiosqlite
import config  # config.py file


cached_prefixes = {}


async def get_prefix(bot, message):
    if message.guild.id in cached_prefixes.keys():
        return cached_prefixes[message.guild.id]
    async with aiosqlite.connect('data/prefixes.db') as db:
        cursor = await db.execute("SELECT * FROM prefixes WHERE guild_id = ?", (message.guild.id,))
        row = await cursor.fetchone()
        if row:
            cached_prefixes.update({message.guild.id: row[1]})
            return row[1]
        else:
            cached_prefixes.update({message.guild.id: config.prefix})  # add guild prefix to cache
            return config.prefix  # default prefix

bot = commands.Bot(
    command_prefix=get_prefix,
    description='A cool bot to compete in TCR Bot Jam',
    case_insensitive=True,
    intents=discord.Intents.all(),
)


# task to clear cache every 12 hours
@tasks.loop(hours=12)
async def clear_cache():
    print("Cache size:", len(cached_prefixes))
    cached_prefixes.clear()
    print('Cache cleared')
    print("------")


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    bot.db = await aiosqlite.connect('data/prefixes.db')
    await bot.db.execute("CREATE TABLE IF NOT EXISTS prefixes (guild_id INTEGER PRIMARY KEY, prefix TEXT)")
    await bot.db.commit()
    print("Database connection established")
    print("------")


class SupremeHelpCommand(commands.HelpCommand):
    def get_command_signature(self, command):
        return '%s%s %s' % (self.context.clean_prefix, command.qualified_name, command.signature)

    def parse_description(self, text):
        # this function requires blood sacrifice to understand
        # or just a lot of comments
        normal_text = ""  # the text that does not begin with :param: will be added to this
        parameter_names = []  # the names of parameters (after :param) will be added to this list
        parameter_descriptions = []  # the descriptions of parameters (after :param name: ) will be added to this list

        for line in text.splitlines():  # go through each line in the text
            if line.startswith(':param'):  # if the line is a parameter
                line = line.replace(':param', '').replace(":", "").strip()  # remove the :param and : from :param name:
                line = line.split(" ")  # split the line into a list of words (name, description)
                parameter_names.append(line[0])  # add the name to parameter_names
                parameter_descriptions.append(" ".join(line[1:]))  # add the description to parameter_descriptions
            else:  # if the line is not a parameter
                normal_text += line + '\n'  # add it to normal_text with a newline at end

        return f"{normal_text}**Parameters**:\n" + '\n'.join(  # add the parameters to the end of the text
            f"`{name}` – {description}" for name, description in zip(parameter_names, parameter_descriptions))

    async def send_bot_help(self, mapping):  # ?help
        embed = discord.Embed(title="Help", color=discord.Color.blurple())
        for cog, commands in mapping.items():
            filtered = await self.filter_commands(commands, sort=True)
            if command_signatures := [
                self.get_command_signature(c) for c in filtered
            ]:
                cog_name = getattr(cog, "qualified_name", "No Category")
                embed.add_field(name=cog_name, value="\n".join(command_signatures), inline=False)

        channel = self.get_destination()
        await channel.send(embed=embed)

    async def send_command_help(self, command):  # ?help command
        embed = discord.Embed(title=self.get_command_signature(command), color=discord.Color.blurple())
        if command.help:
            try:
                command_help = self.parse_description(command.help)
            except:  # bare except to avoid all kinds of error
                command_help = command.help
            embed.description = command_help
        if alias := command.aliases:
            embed.add_field(name="Aliases", value=", ".join(alias), inline=False)

        channel = self.get_destination()
        await channel.send(embed=embed)

    async def send_help_embed(self, title, description, commands):  # a helper function to add commands to an embed
        embed = discord.Embed(title=title, description=description or "No help found...")

        if filtered_commands := await self.filter_commands(commands):
            for command in filtered_commands:
                embed.add_field(name=self.get_command_signature(command), value=command.help or "No help found...")

        await self.get_destination().send(embed=embed)

    async def send_group_help(self, group):  # ?help group
        title = self.get_command_signature(group)
        await self.send_help_embed(title, group.help, group.commands)

    async def send_cog_help(self, cog):  # ?help cog
        title = cog.qualified_name or "No"
        await self.send_help_embed(f'{title} Category', cog.description, cog.get_commands())


bot.help_command = SupremeHelpCommand()  # set the help command
extensions = [  # list of extensions to load by their filename (.py is removed)
    "settings",
    "meta",
    "polls",
]

for ext in extensions:
    bot.load_extension("cogs." + ext)

# making the bot load all the files in cogs/ could cause beta features to be loaded
# the code below should be uncommented for beta versions of the bot
# for ext in os.listdir("cogs"):
#     if ext.endswith(".py"):
#         bot.load_extension("cogs." + ext[:-3])


# OTHER COMMANDS


@bot.command()
async def ping(ctx):
    await ctx.send(embed=discord.Embed(title="Pong!", description=f"{round(bot.latency * 1000)}ms"))

bot.run(config.token)
