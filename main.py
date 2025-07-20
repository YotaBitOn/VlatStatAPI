#imports
import os
import random

import discord
from discord import app_commands
from discord.ext import commands


import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
#plot customization

#img = mpimg.imread("bg.jpg")


sns.set(rc={
    'axes.facecolor': '#111111',
    'figure.facecolor': '#111111',
    'text.color': 'white',
    'axes.labelcolor': 'white',
    'xtick.color': 'white',
    'ytick.color': 'white'
})
#token
DISCORD_TOKEN = ""

#bot initialization
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.guilds = True

bot = commands.Bot(command_prefix="/", intents=intents)

#variables

plot_color = ['orange','red','cyan','yellow','green','blue','magenta','violet','pink']

#functions
def delete_file(file_path):
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Файл {file_path} успішно видалено.")
        else:
            print(f"Файл {file_path} не знайдено.")
    except Exception as e:
        print(f"Сталася помилка: {e}")


def channel_activity_plot(channel_id, top:10):
    filename = f'{channel_id}_chanell_activity.png'
    df = pd.read_csv(f'{channel_id}_data.csv')

    dates = []
    for n in range(len(df.created_at)):
        year = df.created_at[n].split('-')[0]
        mounth = df.created_at[n].split('-')[1]

        dates.append(f'{year}.{mounth}')

    amount = len(pd.Series(dates).value_counts().values.tolist())
    dates_counts = pd.Series(dates).value_counts().sort_index().iloc[amount-top:amount]

    x_sa = dates_counts.index.tolist()
    y_sa = dates_counts.values.tolist()

    fig, ax = plt.subplots()

    sns.barplot(x=x_sa, y=y_sa, color = random.choice(plot_color), ax=ax)


    #xlim = ax.get_xlim()
    #ylim = ax.get_ylim()
    #ax.imshow(img, extent=[xlim[0], xlim[1], ylim[0], ylim[1]], aspect='auto', zorder=0)

    plt.xticks(rotation=90)
    plt.savefig(filename, bbox_inches='tight')
    plt.clf()

    return filename

#bot events
def user_frequency_plot(channel_id, top:10):
    filename = f'{channel_id}user_frequency_plot.png'
    df = pd.read_csv(f'{channel_id}_data.csv')  # data preparation

    df = df[~df['author'].str.contains('#', na=False)]

    author_counts = df['author'].value_counts(ascending=False).head(top)  # user_frequency

    sns.barplot(x=author_counts.index, y=author_counts.values, color=random.choice(plot_color))

    plt.tight_layout()  # result photo setting
    plt.xticks(rotation=90)
    plt.savefig(filename, bbox_inches='tight')

    return filename
    plt.clf()

def user_month_activity_plot(channel_id, user, top):
    user = str(user)
    filename = f'{channel_id}user_month_activity_plot.png'
    df = pd.read_csv(f'{channel_id}_data.csv')
    df = df[df['author'] == user]['created_at'].reset_index(drop=True)

    #for i in range(len(df['created_at'])):d
    #    print(df['created_at'][i])
    for i in range(len(df)):
        df[i] = '-'.join(df[i].split(' ')[0].split('-')[0:2])
    y = df.value_counts().sort_index().values.tolist()
    x = df.value_counts().sort_index().index.tolist()

    sns.barplot(x=x, y=y, color=random.choice(plot_color))

    plt.title(f"{user} month activity")
    plt.tight_layout()  # result photo setting
    plt.xticks(rotation=90)
    plt.savefig(filename, bbox_inches='tight')
    plt.clf()
    return filename




@bot.event
async def on_ready(): #log check
    print(f'Logged in as {bot.user}')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands.")
    except Exception as e:
        print(e)

@bot.tree.command(name='scan', description='scan chat history')
async def scan(interaction: discord.Interaction): #current channel history scan and return in file

    channel_id = interaction.channel.id
    channel = bot.get_channel(channel_id)
    messages = [] #store all history here

    m_created_at =[]
    m_author = []
    m_content = []

    await interaction.response.send_message(f"Scanning🔎...")

    # storing process
    async for msg in channel.history(limit=None, oldest_first=True):

        created_at_fixed = str(msg.created_at.strftime('%Y-%m-%d %H:%M:%S')) #removing miliseconds

        messages.append(f"{created_at_fixed} | {msg.author}: {msg.content}")

        m_created_at.append(created_at_fixed)
        m_author.append(msg.author)
        m_content.append(msg.content)

# creating csv and txt
    chat_history_data = pd.DataFrame({
        'created_at': m_created_at,
        'author': m_author,
        'content': m_content
    })
    print(chat_history_data)
    txt_file_name = str(channel_id) + "_history.txt"
    csv_file_name = str(channel_id) + '_data.csv'

    chat_history_data.to_csv(csv_file_name, index=False)

    with open(txt_file_name, "w", encoding="utf-8") as f:
        f.write("\n".join(messages))

    await interaction.followup.send(file=discord.File(txt_file_name))


@bot.tree.command(name='user_frequency', description='shows users activity in chat')
async def user_frequency(interaction: discord.Interaction, top: int = 10):
    channel_id = interaction.channel.id
    try:
        file_ = user_frequency_plot(channel_id, top)
    except:
        await interaction.response.send_message('you should /scan this channel first!')
        return
    await interaction.response.send_message(file=discord.File(file_))
    delete_file(f'{channel_id}user_frequency_plot.png')


@bot.tree.command(name='channel_activity', description='shows channel activity per moutn')
async def channel_activity(interaction: discord.Interaction, top: int = 10):
    channel_id = interaction.channel.id
    try:
        file_ = channel_activity_plot(channel_id, top)
    except:
        await interaction.response.send_message('you should /scan this channel first!')
        return
    await interaction.response.send_message(file=discord.File(file_))
    delete_file(f'{channel_id}_chanell_activity.png')

@bot.tree.command(name='user_mouth_activity', description='shows user`s activity per month')
async def user_mouth_activity(interaction: discord.Interaction, user : discord.Member ,top: int = 10):
    channel_id = interaction.channel.id
    try:
        file_ = user_month_activity_plot(channel_id, user = user, top = top)
    except:
        await interaction.response.send_message('you should /scan this channel first!')
        return
    await interaction.response.send_message(file=discord.File(file_))
    delete_file(f'{channel_id}user_month_activity_plot.png')



@bot.tree.command(name='clear_data', description='clears all data collected by a bot')
async def clear_data(interaction: discord.Interaction):
    channel_id = interaction.channel.id
    delete_file(f'{channel_id}_history.txt')
    delete_file(f'{channel_id}_data.csv')


    await interaction.response.send_message('All channel data deleted and is no longer available for VlatStat')

bot.run(DISCORD_TOKEN)