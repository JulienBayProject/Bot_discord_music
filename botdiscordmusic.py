# importation
import discord, youtube_dl, asyncio, os
from discord.ext import commands
from dotenv import load_dotenv

bot = commands.Bot(command_prefix="!",description="Bot pour jouer de la musique")
musics = { }
ytdl = youtube_dl.YoutubeDL()

# chargement d'une variable d'environment
load_dotenv(dotenv_path="config")


@bot.event
async def on_ready():
    print("ready!")
    
class Video:
    def __init__(self, link):
        video = ytdl.extract_info(link, download=False)
        video_format = video["formats"][0]
        self.url = video["webpage_url"]
        self.stream_url = video_format["url"]

# commande permettant de skip une musique 
@bot.command()
async def skip(ctx):
    client = ctx.guild.voice_client
    client.stop()

# commande permettant de quitter un bot discord
@bot.command()
async def leave(ctx):
    client = ctx.guild.voice_client
    await client.disconnect()
    musics[ctx.guild] = []
    await ctx.send(f"je pars parce que {ctx.message.author.mention} veut que je me casse")
    
# commande permettant relancer une musique si elle a été mise en pause
@bot.command()
async def resume(ctx):
    client = ctx.guild.voice_client
    if client.is_paused():
        client.resume()

# commande permettant de mettre sur pause 
@bot.command()
async def pause(ctx):
    client = ctx.guild.voice_client
    if not client.is_paused():
        client.pause()

def play_song(client, queue, song):
    source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(song.stream_url
        , before_options = "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"))

    def next(_):
        if len(queue) > 0:
            new_song = queue[0]
            del queue[0]
            play_song(client, queue, new_song)
        else:
            asyncio.run_coroutine_threadsafe(client.disconnect(), bot.loop)

    
    client.play(source, after=next)

# commande pour jouer de la musique
@bot.command()
async def play(ctx, url):
    print("play!")
    client = ctx.guild.voice_client
    
    if client and client.channel :
        video = Video(url)
        musics[ctx.guild].append(video)
    else :    
        channel = ctx.author.voice.channel
        video = Video(url)
        musics[ctx.guild] = []
        client = await channel.connect()
        
        # suppression du message de commande
        messages = await ctx.channel.history(limit=1).flatten()
        
        for each in messages:
            await each.delete()
        
        await ctx.send(f"```je lance : {video.url}```")        
        play_song(client, musics[ctx.guild], video)

bot.run(os.getenv("TOKEN"))