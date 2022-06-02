import discord
from discord.ext import commands
import aiohttp
import re


class RunFlags(commands.FlagConverter):
    lang: str = None


class Meta(commands.Cog):
    def __init__(self):
        self.regex = re.compile(r"(\w*)\s*(?:```)(\w*)?([\s\S]*)(?:```$)")
        self.session = aiohttp.ClientSession()

    async def _run_code(self, *, lang: str, code: str):

        res = await self.session.post(
            "https://emkc.org/api/v1/piston/execute",
            json={"language": lang, "source": code},
        )
        return await res.json()

    async def _send_result(self, ctx: commands.Context, result: dict):
        if "message" in result:
            return await ctx.reply(
                embed=discord.Embed(
                    title="Uh-oh",
                    description=result["message"],
                    color=discord.Color.red(),
                )
            )
        output = result["output"]
        embed = discord.Embed(
            title=f"Ran your {result['language']} code", color=discord.Color.green()
        )
        output = output[:500].strip()
        shortened = len(output) > 500
        lines = output.splitlines()
        shortened = shortened or (len(lines) > 15)
        output = "\n".join(lines[:15])
        output += shortened * "\n\n**Output shortened**"
        embed.add_field(name="Output", value=output or "**<No output>**")

        await ctx.reply(embed=embed)

    @commands.command()
    async def run(self, ctx: commands.Context, *, code: str):
        """
        Run code and get results instantly
        **Note**: You must use codeblocks around the code
        """
        matches = self.regex.findall(code)
        try:
            lang = matches[0][0] or matches[0][1]
        except IndexError:
            l = code.split(" ", 1)
            lang = l[0] or None
        if not lang:
            return await ctx.reply(
                embed=discord.Embed(
                    title="Oops",
                    description="Couldn't find the language hinted in the codeblock or before it",
                )
            )
        try:
            final_code = matches[0][2]
        except IndexError:
            try:
                final_code = l[1]
            except:
                return await ctx.reply(
                    embed=discord.Embed(
                        title="Oops",
                        description="Improper format. Please use it in this format: `run <language> <code>` or\nrun \`\`\`<language>\n<code>\n\`\`\`",
                    )
                )
        result = await self._run_code(lang=lang, code=final_code)

        await self._send_result(ctx, result)


def setup(bot):
    bot.add_cog(Meta())
