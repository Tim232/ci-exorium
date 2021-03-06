import gifs
import config
import discord
import random
import requests
import logging
import aiohttp
import json
import discord.opus
import discord.voice_client
import discord.ext
from discord.ext import commands
from collections import Counter
from outsources import functions, util
from requests.auth import HTTPBasicAuth
import asyncio
import re
from datetime import datetime

mydb = config.DBdata
database = mydb.cursor()
database.execute("CREATE TABLE IF NOT EXISTS warnings (id INT AUTO_INCREMENT PRIMARY KEY, user VARCHAR(255), reason VARCHAR(255), serverid VARCHAR(255))")
database.execute("CREATE TABLE IF NOT EXISTS suggestions (id INT AUTO_INCREMENT PRIMARY KEY, user VARCHAR(255), suggestion VARCHAR(255), approved VARCHAR(255), messageid VARCHAR(255))")
logger = logging.getLogger('discord')
intents = discord.Intents.all()

startTime = datetime.now().timestamp()

bot = commands.Bot(command_prefix=["exo ", "Exo ", "p/", "gay "], case_insensitive=True, intents=intents)  # sets the bot prefix
bot.remove_command('help')  # removes the default discord.py help command


@bot.event  # sets the bot status and prints when it has started in console with stats, stats include: The amount of users that are in the total amount of guilds and the discord.py version
async def on_ready():
    activity = discord.Game(name=f'exo help | {len(bot.guilds)} guilds', type=1)
    await bot.change_presence(status=discord.Status.online, activity=activity)
    print('exorium has started successfully')

bot.load_extension('jishaku')


@bot.event
async def on_guild_join(guild):
    print(f"I just joined {guild.name}, ID: {guild.id}")
    e = discord.Embed(title='New server', color=config.green)
    e.add_field(name="Guild", value=guild, inline=True)
    e.add_field(name="Members", value=guild.member_count, inline=True)
    e.add_field(name="Guild ID", value=guild.id, inline=False)
    channel = bot.get_channel(762203326519181312)
    await channel.send(embed=e)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        ie = discord.Embed(color=config.orange)
        ie.add_field(name='error while processing', value='Please fill in all the required arguments.\nUse `exo info <command`> for usage.')
        await ctx.send(embed=ie)

    if isinstance(error, commands.MissingPermissions):
        ie = discord.Embed(color=config.red)
        ie.add_field(name='error while processing', value='You do not have the sufficient permissions.')
        await ctx.send(embed=ie)

    if isinstance(error, commands.NotOwner):
        ie = discord.Embed(color=config.orange)
        ie.add_field(name='error while processing', value='Only bot owners can use this command.')
        await ctx.send(embed=ie)
        

# Use of group decorators for help cmd
support = '<:discordwindows:733855618775121921> [Support](https://discord.gg/CEHkNky)'
invite = '<:discovery:719431405905379358> [Invite exo](https://discordextremelist.xyz/en-US/bots/exorium)'
review = '<:new:736926339113680976> [Review us](https://top.gg/bot/620990340630970425)'
policy = '🔗 [Privacy policy](https://github.com/ThePawKingdom/exorium/blob/master/privacy%20policy.md)'

botdesc = f'{support} | {invite} | {review} | {policy}'


@bot.group()
async def help(ctx):
    stats = f"**statistics:** {str(len(bot.guilds))} guilds | {str(len(bot.users))} users"
    discordpy = f"**discord.py version:** {discord.__version__}"
    news = "[Changed help command completely. Bot was transferred to a new VPS, for issues please join the support server.](https://twitter.com/exoriumbot)"
    if ctx.invoked_subcommand is None:
        e = discord.Embed(title=f'help cmd | prefix: `{ctx.prefix}`', description=botdesc, color=config.color)
        e.add_field(name='info', value=f'**Developers:** [Bluewy](https://discord.com/users/698080201158033409) | [Toothless](https://discord.com/users/341988909363757057)\n{stats}\n{discordpy}', inline=False)
        e.add_field(name='categories', value=f'`{ctx.prefix}help social` - Social commands\n**{ctx.prefix}help mod** - Moderation commands\n`{ctx.prefix}help utils` - Utility commands\n**{ctx.prefix}help exorium** - Bot related\n`{ctx.prefix}help jsk (Dev+)` - Debugging\n**{ctx.prefix}help owner (Dev+)** - Dev only commands\n`{ctx.prefix}help nsfw` - NSFW commands', inline=False)
        e.add_field(name='Latest news', value=news, inline=False)
        await ctx.send(embed=e)


@help.command()
@commands.is_owner()
async def jsk(ctx):
    e = discord.Embed(title='Jishaku help', description='Jishaku debug and diagnostics commands', color=config.color)
    e.add_field(name='Commands', value='```cancel, cat, curl, debug, git, hide, in, load, py, py_inspect, repeat, retain, shell, show, logout, source, su, sudo, tasks, unload, voice```', inline=False)
    e.add_field(name='Relevant links', value='[jsk repo](https://github.com/Gorialis/jishaku)\n[documentation](https://jishaku.readthedocs.io/en/latest/)\n[pypi.org](https://pypi.org/project/jishaku/)', inline=False)
    await ctx.send(embed=e)


@help.command()
async def social(ctx):
    e = discord.Embed(title='Social commands', description="All the bot's social commands, to improve community and chatting!", color=config.color)
    e.add_field(name='Commands', value="```awoo, bellyrub, blush, bonk, boop, cookie, cuddle, feed, glomp, happy, highfive, hug, kiss, lick, pat, rawr, snuggle, wag```", inline=False)
    e.add_field(name='Gifs & images', value="You can help us find more gifs & images for our interaction commands! Just go to [tenor](https://tenor.com) or to [imgur](https://imgur.com) and find us furry, or animal related gifs and make an issue on the [github repository](https://github.com/ThePawKingdom/exorium).", inline=False)
    await ctx.send(embed=e)


@help.command()
async def mod(ctx):
    e = discord.Embed(title='Moderation commands', description="All the moderation commands to make your server a safer place!", color=config.color)
    e.add_field(name='Commands', value="```ban, delwarn, purge, softban, unban, warn, warnings```", inline=False)
    e.add_field(name='Important', value="The ban command is permanent and can not temporarily ban people. We are working on allowing tempbans, and we plan to add more moderation commands in the future.", inline=False)
    await ctx.send(embed=e)


@help.command()
async def utils(ctx):
    e = discord.Embed(title='Utility commands', description="All the useful commands for you to use to enhance your own use of discord!", color=config.color)
    e.add_field(name='Commands', value="```avatar, decide, id, info, poll, random, say, serverinfo, userinfo, variable, animal, image```", inline=False)
    await ctx.send(embed=e)


@help.command()
async def exorium(ctx):
    e = discord.Embed(title='Bot commands', description="All the commands directly related to exorium itself", color=config.color)
    e.add_field(name='Commands', value="```askexo, invite, links, ping, stats, suggest```", inline=False)
    e.add_field(name='Important', value="Please report it to us immediately if one of these commands are outdated, or not functional in our [support server](https://discord.gg/CEHkNky)", inline=False)
    await ctx.send(embed=e)


@help.command()
@commands.is_owner()
async def owner(ctx):
    e = discord.Embed(title='Dev commands', description="The developer and owner commands to manage exorium", color=config.color)
    e.add_field(name='Commands', value="`help jsk` - Jishaku help menu\n**digest** - Review suggestions\n`jsk+` - Debugging/Diagnostics", inline=False)
    await ctx.send(embed=e)


@help.command()
async def nsfw(ctx):
    e = discord.Embed(title='NSFW commands', description="All the Not Safe For Work commands in exorium (NSFW CHANNELS ONLY)", color=config.color)
    e.add_field(name='Commands', value="`e621` - Search the [e621](https://e621.net) API for yiff", inline=False)
    await ctx.send(embed=e)
###############################################################
###############################################################


@bot.command(name="ping", aliases=["pong", "latency"], brief="shows the bot's latency.")  # the ping command, simply shows the latency in an embed
async def latency(ctx):
    embed = discord.Embed(color=config.color)
    embed.add_field(name="<a:loadingbounce:753173725263822858> ping", value=f'**{bot.latency * 1000:.0f}**ms', inline=True)
    await ctx.send(embed=embed)
    await functions.logging(ctx, "ping", bot)

    
@bot.command(name="invite", aliases=["inv", "oauth"], brief="Shows the bot ouath link")  # shows the bot invite with hyperlink in an embed
async def invite(ctx):
    embed = discord.Embed(color=config.color)
    embed.add_field(name="Invites", value="[Add exorium to your server](https://discord.com/api/oauth2/authorize?client_id=620990340630970425&permissions=806218999&scope=bot)\n[Join the support server](https://discord.gg/CEHkNky)")
    await ctx.send(embed=embed)
    await functions.logging(ctx, "invite", bot)


@bot.command()
async def support(ctx):
    e = discord.Embed(color=config.color)
    e.add_field(name='Get support', value='- [Support server](https://discord.gg/CEHkNky)\n- [Github issue](https://github.com/ThePawKingdom/exorium/issues)\n- [DM Azymondias#4612](https://discord.com/users/698080201158033409)', inline=True)
    e.add_field(name='Related commands', value='```exo invite\nexo links```', inline=True)
    e.set_footer(text='Thank you for using exorium!')
    await ctx.send(embed=e)
    await functions.logging(ctx, "support", bot)


@bot.command()  # shows the links related to exorium in an embed
async def links(ctx):
    e = discord.Embed(color=config.color)
    e.add_field(name='Bot lists', value='- [Discordextremelist](https://discordextremelist.xyz/en-US/bots/exorium)\n- [Discordbotlist](https://top.gg/bot/620990340630970425)', inline=True)
    e.add_field(name='Github', value='- [Repository](https://github.com/ThePawKingdom/exorium)', inline=True)
    e.add_field(name='status', value='- [status page](https://exorium.statuspage.io/)', inline=True)
    await ctx.send(embed=e)


@bot.command(name="stats", aliases=["statistics"], brief="shows bot statistics.")  # shows the bot statistics (total amount of users in total amount of guilds) in an embed
async def statistics(ctx):
    print(startTime)
    print(datetime.now().timestamp())
    uptime = datetime.now().timestamp() - startTime
    channel_types = Counter(type(c) for c in bot.get_all_channels())
    voice = channel_types[discord.channel.VoiceChannel]
    text = channel_types[discord.channel.TextChannel]

    embed = discord.Embed(title="exorium statistics", color=config.color)
    embed.add_field(name="Total guilds", value=str(len(bot.guilds)), inline=True)
    embed.add_field(name="Total users", value=str(len(bot.users)), inline=True)
    embed.add_field(name=".py version", value=discord.__version__, inline=True)
    embed.add_field(name="channels", value=f"<:channel:719660740050419935> {text:,} | <:voice:719660766269145118> {voice:,}", inline=True)
    embed.add_field(name="Uptime", value=str((datetime.utcfromtimestamp(uptime).strftime('%H hour(s), %M minute(s) and %S second(s)'))), inline=True)
    await ctx.send(embed=embed)
    await functions.logging(ctx, "stats", bot)

    #embed = discord.Embed(title="exorium statistics", color=config.color)
    #e.description = f"__**About exorium**__\n**Developers:** [Bluewy](https://discord.com/users/698080201158033409) & [Toothless](https://discord.com/users/341988909363757057)\n**Library:** [Discord.py {discord.__version__}]((https://github.com/Rapptz/discord.py))\n**Last boot:** {str((datetime.utcfromtimestamp(uptime).strftime('%H hour(s), %M minute(s) and %S second(s)')))}

@bot.command()  # retrieves the ID of a member. Argument can be an ID, just the user's name or the user mention
async def id(ctx, member: discord.Member):
    await ctx.send(member.id)
    await functions.logging(ctx, "id", bot)


@bot.command(name='animal', help='Generates a random animal!')
async def animal(ctx, *args):
    delmsg = await ctx.send("Awaiting API results...")
    query = ''
    for thing in args:
        query += f"{thing}+"
    if query.endswith('+'):
        query = query[:-1]
    else:
        query = "animal"
    r = requests.get(
        'https://pixabay.com/api/',
        params={'key': config.pixabaykey, 'q': query, "image_type": 'photo', 'category': 'animals'}
    )
    if r.json()["total"] == 0:
        await delmsg.delete()
        await ctx.send("Sadly, no results were found")
        return
    await delmsg.delete()
    finalimg = random.choice(r.json()["hits"])["webformatURL"]
    embed = discord.Embed(title='Random animal', color=config.color)
    embed.set_image(url=finalimg)
    embed.set_footer(text='Powered by pixabay.')
    await ctx.send(embed=embed)
    await functions.logging(ctx, "animal", bot)


@bot.command(name='image', help='Generates a random image!')
async def image(ctx, *args):
    delmsg = await ctx.send("Awaiting API results...")
    query = ''
    for thing in args:
        query += f"{thing}+"
    if query.endswith('+'):
        query = query[:-1]
    r = requests.get(
        'https://pixabay.com/api/',
        params={'key': config.pixabaykey, 'q': query, "image_type": 'photo', 'safesearch': 'true'}
    )
    if r.json()["total"] == 0:
        await delmsg.delete()
        await ctx.send("Sadly, no results were found")
        return
    await delmsg.delete()
    finalimg = random.choice(r.json()["hits"])["webformatURL"]
    embed = discord.Embed(title='Random image', color=config.color)
    embed.set_image(url=finalimg)
    embed.set_footer(text='Powered by pixabay.')
    await ctx.send(embed=embed)
    await functions.logging(ctx, "image", bot)


@bot.command()
async def e621(ctx, *, tags=''):
    if ctx.channel.is_nsfw() or ctx.channel.id in config.nsfwexceptions:
        tagurl = tags.replace(' ', '+')
        delmsg = await ctx.send("Waiting for results <a:loadingbounce:753173725263822858>")
        response = requests.get(
            f'https://e621.net/posts.json?tags={tagurl}',
            headers={'User-Agent': config.e621agent},
            auth=HTTPBasicAuth(config.e621username, config.e621key)
        )
        if not response.json()["posts"]:
            await delmsg.delete()
            await ctx.send(f"Sadly, we couldn't get you `{tags}` - weirdo")
            return
        finalimg = random.choice(response.json()["posts"])["file"]["url"]
        while True:
            if finalimg.endswith(".webm"):
                finalimg = random.choice(response.json()["posts"])["file"]["url"]
            else:
                break
        embed = discord.Embed(title='Random yiff', color=config.color)
        embed.set_image(url=finalimg)
        embed.set_footer(text='Powered by e621.')
        await delmsg.delete()
        await ctx.send(embed=embed)
        await functions.logging(ctx, "e621", bot)
    else:
        await ctx.send("Sorry, you can only use e621 commands in an NSFW channel")
        await functions.logging(ctx, "e621_fail", bot)


@bot.command(aliases=['av'])  # shows the mentioned user's avatar in an embed
async def avatar(ctx, *, user: discord.Member = None):
    if not user:
        user = ctx.author
    ea = discord.Embed(title='Avatar', color=config.color)
    ea.set_author(name=user, icon_url=user.avatar_url)
    if str(user.avatar_url).endswith(".gif?size=1024"):
        ea.set_image(url=user.avatar_url_as(format="gif", size=1024))
    else:
        ea.set_image(url=user.avatar_url_as(format="png", size=1024))
    await ctx.send(embed=ea)
    await functions.logging(ctx, "avatar", bot)


@bot.command(name="serverinfo", aliases=["servinfo", "sinfo"])  # shows info about the server the command was executed, in an embed. Still being worked on.
async def serverinfo(ctx):
    gu = ctx.guild
    features = {
        "VIP_REGIONS": "VIP Voice Servers",
        "VANITY_URL": "Vanity Invite",
        "INVITE_SPLASH": "Invite Splash",
        "VERIFIED": "Verified",
        "PARTNERED": "Partnered",
        "MORE_EMOJI": "More Emoji",
        "DISCOVERABLE": "Server Discovery",
        "FEATURABLE": "Featurable",
        "COMMUNITY": "Community server",
        "COMMERCE": "Commerce",
        "PUBLIC": "Public",
        "NEWS": "News Channels",
        "BANNER": "Banner",
        "ANIMATED_ICON": "Animated Icon",
        "PUBLIC_DISABLED": "Public Disabled",
        "WELCOME_SCREEN_ENABLED": "Welcome Screen"
    }
    embed = discord.Embed(color=config.color)
    embed.add_field(name="Server Name", value=str(gu.name), inline=True)
    embed.add_field(name="Membercount", value=gu.member_count, inline=True)
    embed.add_field(name="Owner", value=ctx.guild.owner, inline=True)
    embed.add_field(name="Creation Date", value=f"{gu.created_at.strftime('%d.%m.%Y %H:%M')}", inline=True)
    embed.add_field(name="Server ID", value=str(gu.id), inline=True)
    embed.add_field(name="Region", value=str(gu.region), inline=True)
    embed.add_field(name="Verification Level", value=str(gu.verification_level), inline=True)
    featurestext = ''
    for feature in gu.features:
        featurestext += f"\n{features[feature]}"
    if ctx.guild.features:
        embed.add_field(name="Server Features", value=featurestext, inline=True)
    embed.add_field(name="AFK Channel", value=f"`{gu.afk_channel}`\nTimeout {gu.afk_timeout}s", inline=False)
    if str(gu.icon_url).endswith(".gif?size=1024"):
        embed.set_author(name=ctx.guild.name + " information", url=gu.icon_url_as(format="gif", size=1024), icon_url=gu.icon_url_as(format="gif", size=1024))
        embed.set_thumbnail(url=gu.icon_url_as(format="gif", size=1024))
    else:
        embed.set_author(name=ctx.guild.name + " information", url=gu.icon_url_as(format="png", size=1024), icon_url=gu.icon_url_as(format="png", size=1024))
        embed.set_thumbnail(url=gu.icon_url_as(format="png", size=1024))
    await ctx.send(embed=embed)
    await functions.logging(ctx, "serverinfo", bot)


@bot.command()
async def userinfo(ctx, *, user: discord.Member = None):
    if not user:
        user = ctx.author
    roles = ''
    for role in reversed(user.roles):
        if role.name != "@everyone":
            roles += f" {role.mention}"
    createday = user.created_at.weekday()
    joinday = user.joined_at.weekday()
    embed = discord.Embed(color=user.color, description=f"{user.mention} {util.statusemoji.get(str(user.status))}")
    if str(user.avatar_url).endswith(".gif?size=1024"):
        embed.set_author(name=user, icon_url=user.avatar_url_as(format="gif", size=1024), url=user.avatar_url_as(format="gif", size=1024))
        embed.set_thumbnail(url=user.avatar_url_as(format="gif", size=1024))
    else:
        embed.set_author(name=user, icon_url=user.avatar_url_as(format="png", size=1024), url=user.avatar_url_as(format="png", size=1024))
        embed.set_thumbnail(url=user.avatar_url_as(format="png", size=1024))
    embed.add_field(name="Joined:", value=f"{util.weekdays[joinday]} {user.joined_at.strftime('%d.%m.%Y %H:%M')}", inline=True)
    embed.add_field(name="Created At:", value=f"{util.weekdays[createday]} {user.created_at.strftime('%d.%m.%Y %H:%M')}", inline=True)
    if roles:
        embed.add_field(name=f"Roles [{len(user.roles)-1}]:", value=roles, inline=False)
    if user.voice:
        embed.add_field(name="Voice Channel:", value=user.voice.channel.name, inline=False)
    embed.set_footer(text=f"ID: {user.id}")
    await ctx.send(embed=embed)
    await functions.logging(ctx, "userinfo", bot)


@bot.command(name='variable', brief='test variables')  # to test things. Currently a way to bully people who arent a fan of furries.
async def variables(ctx):
    embed = discord.Embed(title='variable tests', color=config.color)
    embed.add_field(name='test:', value="Teh fitnyessgwam pacew test is a muwtistage aewobic capacity test that pwogwessivewy gets mowe difficuwt as it continyues. Teh 20 metew pacew test wiww begin owo in 30 seconds. Wine up at teh stawt. Teh wunnying speed stawts swowwy~ but gets fastew each minyute aftew chu heaw dis signyaw. A singwe wap shouwd be compweted each time chu heaw dis sound. Uwu wemembew uwu to wun owo in a gay winye~ and wun as wong as possibwe. Teh second time chu faiw uwu to compwete a wap befowe teh sound~ ur test is ovew. Teh test wiww begin on teh wowd stawt. On ur mawk~ get weady~ stawt.", inline=False)
    embed.set_thumbnail(url="https://www.dropbox.com/s/yx7z6iefnx0q576/Icon.jpg?dl=1")
    embed.set_author(name="The Paw Kingdom Links", url="https://www.dropbox.com/s/yx7z6iefnx0q576/Icon.jpg?dl=1", icon_url="https://www.dropbox.com/s/yx7z6iefnx0q576/Icon.jpg?dl=1")
    await ctx.send(embed=embed)
    await functions.logging(ctx, "variable", bot)


@bot.command(name='snuggle', brief='Snuggling, how sweet')  # interaction command - snuggle someone. gifs are random!
async def snuggle(ctx, members: commands.Greedy[discord.Member], *, reason="being adorable"):
    await functions.interactions(ctx, members, reason, "snuggle", "how cute", "snuggled")
    await functions.logging(ctx, "snuggle", bot)


@bot.command(name='hug', brief='Fandom hug!')  # interaction command - hug someone. gifs are random!
async def hug(ctx, members: commands.Greedy[discord.Member], *, reason="being adorable"):
    await functions.interactions(ctx, members, reason, "hug", "how lovely", "hugged")
    await functions.logging(ctx, "hug", bot)


@bot.command(name='bonk', brief='Bonk naughty person!')  # interaction command - bonk someone. gifs are random!
async def bonk(ctx, members: commands.Greedy[discord.Member], *, reason="bad!"):
    await functions.interactions(ctx, members, reason, "bonk", "how mean", "bonked")
    await functions.logging(ctx, "bonk", bot)


@bot.command(name='pat', brief='Pats, wholesome!')  # interaction command - pat someone. gifs are random!
async def pat(ctx, members: commands.Greedy[discord.Member], *, reason="being adorable"):
    await functions.interactions(ctx, members, reason, "pat", "how beautiful", "pat")
    await functions.logging(ctx, "pat", bot)


@bot.command(name='boop', aliases=['bp'], brief='Boop!')  # interaction command - boop someone. gifs are random!
async def boop(ctx, members: commands.Greedy[discord.Member], *, reason="being adorable"):
    await functions.interactions(ctx, members, reason, "boop", "so soft", "booped")
    await functions.logging(ctx, "boop", bot)


@bot.command(name='kiss', aliases=['smooch'], brief='Smooch!')  # interaction command - kiss someone. gifs are random!
async def kiss(ctx, members: commands.Greedy[discord.Member], *, reason="being lovely"):
    await functions.interactions(ctx, members, reason, "smooch", "lovely", "smooched")
    await functions.logging(ctx, "kiss", bot)


@bot.command(name="lick", brief='Licking, lol')  # interaction command - lick someone. gifs are random!
async def lick(ctx, members: commands.Greedy[discord.Member], *, reason="being adorable"):
    await functions.interactions(ctx, members, reason, "lick", "tasty", "licked")
    await functions.logging(ctx, "lick", bot)


@bot.command(name="bellyrub")  # interaction command - bellyrub someone. gifs are random!
async def bellyrub(ctx, members: commands.Greedy[discord.Member], *, reason="being adorable"):
    await functions.interactions(ctx, members, reason, "bellyrub", "lovely", "bellyrubbed")
    await functions.logging(ctx, "bellyrub", bot)


@bot.command(name="cuddle")  # interaction command - cuddle someone. gifs are random!
async def cuddle(ctx, members: commands.Greedy[discord.Member], *, reason="being adorable"):
    await functions.interactions(ctx, members, reason, "cuddle", "heartwarming", "cuddled")
    await functions.logging(ctx, "cuddle", bot)


@bot.command(name="rawr")  # interaction command - rawr at someone. gifs are random!
async def rawr(ctx, members: commands.Greedy[discord.Member], *, reason="Rawr!"):
    giflist = gifs.rawr
    gif = random.choice(giflist)
    if not members:
        embed = discord.Embed(title="", color=config.color, description=(ctx.message.author.mention + " " + "**rawred, cute!**\nFor: " + reason))
        embed.set_image(url=gif)
        await ctx.send(embed=embed)
        return
    embed = discord.Embed(title="", color=config.color, description=(ctx.message.author.mention + " " + "**rawred at**" + " " + '**,** '.join(x.mention for x in members) + "**, cute!**\nFor: " + reason))
    embed.set_image(url=gif)
    await ctx.send(embed=embed)
    await functions.logging(ctx, "rawr", bot)


@bot.command(name="awoo")  # interaction command - awoo at someone. gifs are random!
async def awoo(ctx, members: commands.Greedy[discord.Member], *, reason="Awoo!"):
    giflist = gifs.awoo
    gif = random.choice(giflist)
    if not members:
        embed = discord.Embed(title="", color=config.color, description=(ctx.message.author.mention + " " + "**awoo'd, chilling!**\nFor: " + reason))
        embed.set_image(url=gif)
        await ctx.send(embed=embed)
        return
    embed = discord.Embed(title="", color=config.color, description=(ctx.message.author.mention + " " + "**awoo'd at**" + " " + '**,** '.join(x.mention for x in members) + "**, chilling!**\nFor: " + reason))
    embed.set_image(url=gif)
    await ctx.send(embed=embed)
    await functions.logging(ctx, "awoo", bot)


@bot.command(name="blush")  # interaction command - blush (because of) someone. gifs are random!
async def blush(ctx, members: commands.Greedy[discord.Member], *, reason="Makes them kyooter!"):
    giflist = gifs.blush
    gif = random.choice(giflist)
    if not members:
        embed = discord.Embed(title="", color=config.color, description=(ctx.message.author.mention + " " + "**blushed**\nFor: " + reason))
        embed.set_image(url=gif)
        await ctx.send(embed=embed)
        return
    embed = discord.Embed(title="", color=config.color, description=(ctx.message.author.mention + " " + "**blushed because of**" + " " + '**,** '.join(x.mention for x in members) + "**, kyoot!**\nFor: " + reason))
    embed.set_image(url=gif)
    await ctx.send(embed=embed)
    await functions.logging(ctx, "blush", bot)


@bot.command(name="feed")  # interaction command - feed someone. Gifs are random
async def feed(ctx, members: commands.Greedy[discord.Member], *, reason="Hungwy"):
    await functions.interactions(ctx, members, reason, "feed", "sweet!", "fed")
    await functions.logging(ctx, "feed", bot)


@bot.command()
async def cookie(ctx, members: commands.Greedy[discord.Member]):
    e = discord.Embed(title='A cookie has been given!', description=f'{ctx.author.mention} gave {members[0].mention} a cookie', color=config.green)
    await ctx.send(embed=e)


@bot.command(name="glomp")  # interaction command - glomp someone. gifs are random!
async def glomp(ctx, members: commands.Greedy[discord.Member], *, reason="Love!"):
    giflist = gifs.glomp
    gif = random.choice(giflist)
    embed = discord.Embed(title="", color=config.color, description=(ctx.message.author.mention + " " + "**glomped on**" + " " + '**,** '.join(x.mention for x in members) + "**, chilling!**\nFor: " + reason))
    embed.set_image(url=gif)
    await ctx.send(embed=embed)
    await functions.logging(ctx, "glomp", bot)


@bot.command(name="happy")  # interaction command - be happy (because of someone). gifs are random!
async def happy(ctx, members: commands.Greedy[discord.Member], *, reason="Vibing"):
    giflist = gifs.happy
    gif = random.choice(giflist)
    if not members:
        embed = discord.Embed(title="", color=config.color, description=(ctx.message.author.mention + " " + "**Is happy**\nFor: " + reason))
        embed.set_image(url=gif)
        await ctx.send(embed=embed)
        return
    embed = discord.Embed(title="", color=config.color, description=(ctx.message.author.mention + " " + "**Is happy because of**" + " " + '**,** '.join(x.mention for x in members) + "**, kyoot!**\nFor: " + reason))
    embed.set_image(url=gif)
    await ctx.send(embed=embed)
    await functions.logging(ctx, "happy", bot)


@bot.command(name="highfive")  # interaction command - highfive someone. Gifs are random
async def highfive(ctx, members: commands.Greedy[discord.Member], *, reason="being adorable"):
    await functions.interactions(ctx, members, reason, "highfive", "awesome!", "high fived")
    await functions.logging(ctx, "highfive", bot)


@bot.command(name="wag")  # interaction command - wag (because of someone). gifs are random!
async def wag(ctx, members: commands.Greedy[discord.Member], *, reason="Rawr!"):
    giflist = gifs.wag
    gif = random.choice(giflist)
    if not members:
        embed = discord.Embed(title="", color=config.color, description=(ctx.message.author.mention + " " + "**wags their tail, kyoot!**\nFor: " + reason))
        embed.set_image(url=gif)
        await ctx.send(embed=embed)
        return
    embed = discord.Embed(title="", color=config.color, description=(ctx.message.author.mention + " " + "**wags their tail because of**" + " " + '**,** '.join(x.mention for x in members) + "**, cute!**\nFor: " + reason))
    embed.set_image(url=gif)
    await ctx.send(embed=embed)
    await functions.logging(ctx, "wag", bot)


@bot.command(name='random', brief='Randomness!')  # Let exorium choose for you!
async def randomchoice(ctx, *args):
    await ctx.send(random.choice(args), allowed_mentions=discord.AllowedMentions(roles=False, users=False, everyone=False))
    await functions.logging(ctx, "random", bot)


@bot.command(name="info")  # Gives information about the mentioned command
async def info(ctx, arg):
    embed = discord.Embed(title=arg, color=config.color)
    embed.add_field(name="Information", value=getattr(CommandInfo, arg), inline=False)
    embed.add_field(name="Syntax", value=getattr(CommandSyntax, arg), inline=False)
    embed.set_footer(text="Do exo help for all available commands.")
    await ctx.send(embed=embed)
    await functions.logging(ctx, "info", bot)


@bot.command(name="askexo", aliases=["askexorium"])  # Lets you ask something to exorium, he will answer with a random answer listed in gifs.py
async def askexorium(ctx, *, arg):
    answers = gifs.Askexorium
    answer = random.choice(answers)
    embed = discord.Embed(color=config.color)
    embed.add_field(name=arg, value=f"Exo says {answer}", inline=False)
    await ctx.send(embed=embed)
    await functions.logging(ctx, "askexo", bot)


@bot.command(name="ban")  # Permanently bans the user that was mentioned (user must be in guild)
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    if member == ctx.message.author:
        await ctx.send("You can't ban yourself, derp!")
        return
    botmember = ctx.guild.me
    if not botmember.top_role > member.top_role:
        await ctx.send("Could not ban user due to bot role being too low in role hierarchy. Please move the role above the user's highest role.")
        return
    if reason is None:
        await ctx.send(f"Make sure you provide a reason with this command {ctx.author.mention}.")
        return
    messageok = f"You have been banned from **{ctx.guild.name}** | Reason: `{reason}`\nhttps://media1.tenor.com/images/b90428d4fbe48cc19ef950bd85726bba/tenor.gif?itemid=17178338"
    await member.send(messageok)
    await member.ban(reason=f"{ctx.message.author}: {reason}")
    embed = discord.Embed(title=f"{member} has been casted from {ctx.guild.name}!", color=config.color)
    embed.set_image(url="https://media1.tenor.com/images/b90428d4fbe48cc19ef950bd85726bba/tenor.gif?itemid=17178338")
    embed.set_footer(text=f"Reason: {reason}\nModerator: {ctx.message.author}")
    await ctx.send(embed=embed)
    await functions.logging(ctx, "ban", bot)


@bot.command(name='unban')  # Unbans user with a given ID
@commands.has_permissions(ban_members=True)
async def _unban(ctx, userid: int):
    user = await bot.fetch_user(userid)
    await ctx.guild.unban(user)
    embed = discord.Embed(title=f"Unbanned {user.name}", color=config.color)
    embed.set_footer(text=f"{user}, ID: {user.id}")
    await ctx.send(embed=embed)
    await functions.logging(ctx, "unban", bot)


@bot.command(name="kick")  # Kicks the mentioned user from the guild
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    if member == ctx.author:
        await ctx.send("You can't kick yourself, derp!")
        return
    if reason is None:
        await ctx.send(f"Make sure you provide a reason with this command {ctx.author.mention}.")
        return
    else:
        messageok = f"You have been kicked from **{ctx.guild.name}** | Reason: `{reason}`"
        await member.send(messageok)
        await member.kick(reason=f"{ctx.author}: {reason}")
        embed = discord.Embed(title=f"{member} has been kicked from {ctx.guild.name}!", color=config.color)
        embed.set_image(url="https://media1.tenor.com/images/b90428d4fbe48cc19ef950bd85726bba/tenor.gif?itemid=17178338")
        embed.set_footer(text=f"Reason: {reason}\nModerator: {ctx.author}")
        await ctx.send(embed=embed)
        await functions.logging(ctx, "kick", bot)


@bot.command(name="softban")  # bans and immediately unbans the user mentioned
@commands.has_permissions(ban_members=True)
async def softban(ctx, member: discord.Member, *, reason=None):
    if member == ctx.author:
        await ctx.send("You can't softban yourself, derp!")
        return
    if reason is None:
        await ctx.send(f"Make sure you provide a reason with this command {ctx.author.mention}.")
        return
    else:
        messageok = f"You have been softbanned from **{ctx.guild.name}** | Reason: `{reason}`"
        await member.send(messageok)
        await member.ban(reason=f"{ctx.author}: {reason}")
        await member.unban()
        embed = discord.Embed(title=f"{member} has been softcasted from {ctx.guild.name}!", color=config.color)
        embed.set_image(url="https://media1.tenor.com/images/b90428d4fbe48cc19ef950bd85726bba/tenor.gif?itemid=17178338")
        embed.set_footer(text=f"Reason: {reason}\nModerator: {ctx.author}")
        await ctx.send(embed=embed)
        await functions.logging(ctx, "softban", bot)


@bot.command(name="poll")  # Makes a poll with up to 10 options, seperate choices with ,
async def poll(ctx, *, arg):
    await ctx.message.delete()
    choice = str(arg).split(",")
    n = 1
    reactionlist = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    embed = discord.Embed(title="Poll", color=config.color)
    for x in choice:
        embed.add_field(name="Option " + reactionlist[n-1], value=f"{x}", inline=False)
        n = n+1
    embed.set_footer(text=f"Poll cast by {ctx.author}")
    botmsg = await ctx.send(embed=embed)
    en = 1
    for emoji in reactionlist:
        await botmsg.add_reaction(emoji)
        en = en+1
        if en >= n:
            break
    await functions.logging(ctx, "poll", bot)


@bot.command(name="decide")  # Let people vote for something
async def decide(ctx, *, arg):
    await ctx.message.delete()
    embed = discord.Embed(title=arg, color=config.color)
    embed.set_footer(text=f"Asked by {ctx.author}")
    botmsg = await ctx.send(embed=embed)
    await botmsg.add_reaction("✅")
    await botmsg.add_reaction("❌")
    await functions.logging(ctx, "decide", bot)


@bot.command(name="revive")  # Tags the role that was given with a message.
@commands.has_permissions(manage_messages=True)
async def revive(ctx):
    await ctx.message.delete()
    await ctx.send(f"<@&738356235841175594>! The chat is dead, we need you now! (revived by {ctx.author})")
    await functions.logging(ctx, "revive", bot)


@bot.command()  # In an embed repeats what you said and deletes the original command
async def say(ctx, *, sentence):
    try:
        await ctx.message.delete()
    except discord.Forbidden:
        pass
    except discord.NotFound:
        pass
    embed = discord.Embed(color=config.color)
    embed.add_field(name=sentence, value=f'by {ctx.author}')
    await ctx.send(embed=embed)
    await functions.logging(ctx, "say", bot)


@bot.command()
async def suggest_deprecated(ctx, *, suggestion):
    try:
        await ctx.message.delete()
    except discord.Forbidden:
        pass
    except discord.NotFound:
        pass

    if len(suggestion) > 400:
        ee = discord.Embed(color=config.red)
        ee.add_field(name='error while processing', value='Suggestion exceeds the 400 character limit')
        await ctx.send(embed=ee)
    elif len(suggestion) < 400:
        e = discord.Embed(color=config.green)
        e.add_field(name='Suggestion recorded:', value=f'```{suggestion}```\nJoin [the support server](https://discord.gg/CEHkNky) to see your suggestion status.')
        await ctx.send(embed=e)

        es = discord.Embed(color=config.color)
        es.add_field(name='Suggestion', value=suggestion)
        es.set_footer(text=f'suggested by {ctx.author}')
        channel = bot.get_channel(769132481252818954)
        botsgg = await channel.send(embed=es)
        await botsgg.add_reaction("✅")
        await botsgg.add_reaction("❌")
        await functions.logging(ctx, "suggest", bot)


@bot.command()
@commands.has_permissions(manage_messages=True)
async def purge(ctx, amount=0):
    def ducks_pin_message_check(quacky_bot):
        if quacky_bot.pinned is False:
            return True
        return False

    if amount <= 0:
        return await ctx.send("You can't grow younger either, so neither can I purge negative amounts of messages.")
    if amount <= 1500:
        await ctx.channel.purge(limit=amount + 1, check=ducks_pin_message_check)
        await ctx.send(f'{ctx.author} deleted **{amount}** messages using the purge command.')
        await functions.logging(ctx, f"purge ({amount})", bot)
    if amount >= 1500:
        await ctx.send("You can only purge 1500 messages at a time.")


@bot.command()
@commands.has_permissions(ban_members=True)
async def warn(ctx, member: discord.Member, *, reason="No reason provided"):
    sql = "INSERT INTO warnings (user, reason, serverid) VALUES (%s, %s, %s)"
    val = (member.id, reason, ctx.message.guild.id)
    database.execute(sql, val)
    mydb.commit()
    await ctx.send(f"Warned {member.mention} for {reason}")
    await functions.logging(ctx, "warn", bot)


@bot.command()
@commands.has_permissions(ban_members=True)
async def delwarn(ctx, caseid):
    database.execute("SELECT * FROM warnings WHERE id = %s AND serverid = %s", [caseid, ctx.message.guild.id])
    results = database.fetchall()
    if results:
        database.execute("DELETE FROM warnings WHERE id = %s AND serverid = %s", [caseid, ctx.message.guild.id])
        mydb.commit()
        await ctx.send(f"Removed warning #{caseid}")
        await functions.logging(ctx, "delwarn", bot)
        return
    await ctx.send("No warning with such an ID exists here. Please check again!")


@bot.command()
@commands.has_permissions(ban_members=True)
async def warnings(ctx, member: discord.Member):
    await functions.logging(ctx, "warnings", bot)
    database.execute("SELECT * FROM warnings WHERE user = %s AND serverid = %s", [member.id, ctx.message.guild.id])
    results = database.fetchall()
    if not results:
        return await ctx.send("⚠️ User has no warnings!")
    totalwarns = " "
    i = 0
    while i < len(results):
        totalwarns += f"{i+1}: Reason: {results[i][2]}\nCase #{results[i][0]}\n"
        i += 1

    await ctx.send(f"The user has a total of {len(results)} warnings")

    embed = discord.Embed(title='Warnings for ' + member.name, description=totalwarns, color=config.color)
    await ctx.send(embed=embed)


@bot.command()
async def suggest(ctx, *, suggestiontext):
    database.execute("SELECT id FROM suggestions")
    results = database.fetchall()
    suggestionid = results[-1][0] + 1
    sugchannel = bot.get_channel(769132481252818954)
    embed = discord.Embed(title=suggestiontext, color=config.orange)
    embed.add_field(name="User", value=str(ctx.author))
    embed.add_field(name="Status", value="Pending")
    embed.set_footer(text=f"ID: {suggestionid}")
    botmsg = await sugchannel.send(embed=embed)
    await botmsg.add_reaction("✅")
    await botmsg.add_reaction("❌")
    sql = "INSERT INTO suggestions (user, suggestion, messageid) VALUES (%s, %s, %s)"
    val = (ctx.author.id, suggestiontext, botmsg.id)
    database.execute(sql, val)
    mydb.commit()
    await ctx.send(f'Your suggestion "{suggestiontext}" was recorded!')


@bot.command()
async def suggestions(ctx):
    if ctx.message.content.endswith("clear"):
        botmsg = await ctx.send("Confirm deletion of all your **pending** suggestions?")
        await botmsg.add_reaction("✅")
        await botmsg.add_reaction("❌")
        while True:
            react = await bot.wait_for('reaction_add', timeout=300)
            if react[1].id == ctx.author.id:
                if react[0].emoji == "✅":
                    database.execute("DELETE FROM suggestions WHERE user = %s AND approved IS NULL", [ctx.author.id])
                    mydb.commit()
                    await botmsg.delete()
                    break
                else:
                    await botmsg.delete()
                    await ctx.send("Cancelled deletion!")
                    return
    database.execute("SELECT * FROM suggestions WHERE user = %s", [ctx.author.id])
    results = database.fetchall()
    resultsformat = ''
    if not results:
        await ctx.send("You currently don't have any suggestions! Make some using `exo suggest <suggestion>`")
        return
    for sugg in results:
        if not sugg[3]:
            approval = "Pending"
        else:
            approval = sugg[3]
        resultsformat += f"#{sugg[0]} `{sugg[2]}` | Approved: `{approval}`\n"
    await ctx.send(f"Your suggestions:\n{resultsformat}")


@bot.command()
async def digest(ctx):
    approval = {
        "❌": "Denied",
        "✅": "Approved"
    }
    if ctx.author.id == "341988909363757057" or ctx.author.id == "698080201158033409":
        await ctx.send("You aren't allowed to run this command")
        return
    if not re.findall("\\d+", ctx.message.content):
        database.execute("SELECT * FROM suggestions WHERE approved IS NULL")
        results = database.fetchall()
        suggestionid = results[-1][0]
        if not results:
            await ctx.send("No new suggestions!")
        nextsug = results[0][2]
        user = await bot.fetch_user(results[0][1])
        embed = discord.Embed(title=nextsug, color=config.orange)
        embed.add_field(name="User", value=str(user))
        if not results[0][3]:
            status = "Pending"
        else:
            status = results[0][3]
        embed.add_field(name="Status", value=status)
        embed.set_footer(text=f"ID: {suggestionid}")
        botmsg = await ctx.send(embed=embed)
        await botmsg.add_reaction("✅")
        await botmsg.add_reaction("❌")
        while True:
            react = await bot.wait_for('reaction_add', timeout=300)
            if react[1].id == ctx.author.id:
                break
        approved = approval[react[0].emoji]
        sql = "UPDATE suggestions SET approved = %s WHERE suggestion = %s"
        val = (approved, nextsug)
        database.execute(sql, val)
        mydb.commit()
        if approved == "Approved":
            color = config.green
        else:
            color = config.red
        status = approved
        embed = discord.Embed(title=nextsug, color=color)
        embed.add_field(name="User", value=str(user))
        embed.add_field(name="Status", value=status)
        sugmsg = await bot.get_channel(769132481252818954).fetch_message(results[0][4])
        embed.set_footer(text=f"ID: {suggestionid}")
        await sugmsg.edit(embed=embed)
        await botmsg.delete()
        await ctx.send("Got it!")
    else:
        num = re.findall("\\d+", ctx.message.content)
        sql = "SELECT * FROM suggestions WHERE id = %s"
        val = num[1]
        suggestionid = num[1]
        database.execute(sql, val)
        results = database.fetchall()
        if not results:
            await ctx.send("No suggestion with that ID!")
        nextsug = results[0][2]
        user = await bot.fetch_user(results[0][1])
        if not results[0][3]:
            status = "Pending"
            color = config.orange
        else:
            status = results[0][3]
            if status == "Approved":
                color = config.green
            else:
                color = config.red
        embed = discord.Embed(title=nextsug, color=color)
        embed.add_field(name="User", value=str(user))
        embed.add_field(name="Status", value=status)
        embed.set_footer(text=f"ID: {suggestionid}")
        botmsg = await ctx.send(embed=embed)
        await botmsg.add_reaction("✅")
        await botmsg.add_reaction("❌")
        while True:
            react = await bot.wait_for('reaction_add', timeout=300)
            if react[1].id == ctx.author.id:
                break
        approved = approval[react[0].emoji]
        sql = "UPDATE suggestions SET approved = %s WHERE suggestion = %s"
        val = (approved, nextsug)
        database.execute(sql, val)
        mydb.commit()
        sql = "SELECT * FROM suggestions WHERE id = %s"
        val = num
        database.execute(sql, val)
        results = database.fetchall()
        await ctx.send("Got it!")
        await botmsg.delete()
        if not results[0][3]:
            status = "Pending"
            color = config.orange
        else:
            status = results[0][3]
            if status == "Approved":
                color = config.green
            else:
                color = config.red
        embed = discord.Embed(title=nextsug, color=color)
        embed.add_field(name="User", value=str(user))
        embed.add_field(name="Status", value=status)
        embed.set_footer(text=f"ID: {suggestionid}")
        await ctx.send(embed=embed)
        if approved == "Approved":
            color = config.green
        else:
            color = config.red
        status = approved
        embed = discord.Embed(title=nextsug, color=color)
        embed.add_field(name="User", value=str(user))
        embed.add_field(name="Status", value=status)
        sugmsg = await bot.get_channel(769132481252818954).fetch_message(results[0][4])
        embed.set_footer(text=f"ID: {suggestionid}")
        await sugmsg.edit(embed=embed)
        await botmsg.delete()
        await ctx.send("Got it!")


async def api():
    while True:
        if bot.is_ready() is False:
            await asyncio.sleep(5)
        async with aiohttp.ClientSession() as session:
            async with session.post(f"https://api.discordextremelist.xyz/v2/bot/{bot.user.id}/stats",
                                    headers={'Authorization': config.DELTOKEN, "Content-Type": 'application/json'},
                                    data=json.dumps({'guildCount': len(bot.guilds)})) as r:
                js = await r.json()
                if js['error']:
                    print(f'Failed to post to discordextremelist.xyz\n{js}')
        async with aiohttp.ClientSession() as session:
            async with session.post(f"https://discordbotlist.com/api/v1/bots/{bot.user.id}/stats",
                                    headers={'Authorization': config.DBLTOKEN, "Content-Type": 'application/json'},
                                    data=json.dumps({'guilds': len(bot.guilds), 'users': len(bot.users)})) as r2:
                if not r2.status == 200:
                    print(f'Failed to post to discordbotlist.com')
        async with aiohttp.ClientSession() as session:
            async with session.post(f"https://top.gg/api/bots/{bot.user.id}/stats",
                                    headers={'Authorization': config.TOPTOKEN, "Content-Type": 'application/json'},
                                    data=json.dumps({'server_count': len(bot.guilds)})) as r3:
                if not r3.status == 200:
                    print(f'Failed to post to top.gg')
                activity = discord.Game(name=f'exo help | {len(bot.guilds)} guilds', type=1)
                await bot.change_presence(status=discord.Status.online, activity=activity)
        await asyncio.sleep(300)
bot.loop.create_task(api())


class CommandInfo:
    hug = "Hugs the pinged people, kyoot!"
    snuggle = "Snuggles the pinged people, kyoot!"
    boop = "Boops the pinged people, boop!"
    kiss = "Smooches the pinged people :*"
    pat = "Pats the pinged people, good boy!"
    ping = "Displays the latency of the bot"
    invite = "Displays the invite link to invite exorium to your server"
    stats = "Shows some neat stats about exorium"
    get_id = "Gets a users Discord ID"
    av = "Gets and posts avatar of the pinged person (ID works too)."
    links = "Displays some links to get to The Paw Kingdom, this bots home!"
    random = "Can't make a choice? Use the random command! Only 2 options possible at this point"
    info = "You already know what this does, derp"
    honk = "HONK"
    askexorium = "Ask exorium, and he shall give you an answer"
    unban = "Unbans the given user"
    lick = "Licks the pinged people, yum!"
    ban = "Bans the given user"
    kick = "Kicks the given user"
    softban = "Softbans (bans and unbans) the given user"
    poll = "Cast a poll if you can't agree about something!"
    decide = "Casts a simple yes / no poll"
    cuddle = "Cuddles the pinged people, kyoot!"
    support = "Get information on where/how to get support"
    suggest = "suggest something for exorium!"


class CommandSyntax:
    hug = "`exo hug @user1 @user2... reason`"
    snuggle = "`exo snuggle @user1 @user2... reason`"
    boop = "`exo boop @user1 @user2... reason`"
    kiss = "`exo kiss  @user1 @user2... reason`"
    pat = "`exo pat  @user1 @user2... reason`"
    invite = "`exo invite`"
    get_id = "`exo get_id @user`"
    links = "`exo links`"
    info = "`exo info <command>`"
    honk = "`exo honk`"
    askexo = "`exo askexo <Question>`"
    lick = "`exo lick @user1 @user2... reason"
    ban = "`exo ban @user | ID Reason`"
    kick = "`exo kick @user | ID reason`"
    softban = "`exo softban @user | ID reason"
    poll = "`exo poll choice1, choice2, choice3 [...]`"
    decide = "`exo decide <question>"
    cuddle = "exo cuddle @user1 @user2... reason`"
    support = "`exo support`"
    suggest = "`exo suggestion`"


bot.run(config.token)
