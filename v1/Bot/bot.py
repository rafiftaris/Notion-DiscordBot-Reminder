from datetime import date

import discord
from discord.ext import commands
import os

from prettytable import PrettyTable

from addRecord import addData, addPDF, addGenericFile
import validators
from duplicateCheck import doesItExist, amIThere
from tagGiver import giveTags, get_day_ahead, giveTagsFileUpload
from search import Task, list_tasks_from_notion
from delete import deleteMe
#from uploadFiles import downloadFile
from getTitle import giveTitle
import asyncio

prefix = ""
try:
    print(os.environ['PREFIX'])
    prefix = str(os.environ['PREFIX'])
except:
    prefix = '!'

bot = commands.Bot(command_prefix=prefix, help_command=None)
bot.remove_command('help')

@bot.command(name="list_tasks")
async def list_tasks(ctx, *args):
    """Returns all tasks in specified due date"""
    if (len(args) > 0):
        #Check if the tag exists
        days_ahead = get_day_ahead(args)
        search_results = list_tasks_from_notion(days_ahead)

        if (len(search_results) > 0):
            #Found a result
            embed = discord.Embed(title=f"Task List", description=f"Tasks until {date.today() + days_ahead}", color=discord.Color.green())
            table = PrettyTable()
            table.field_name = ["Task", "Due Date", "Priority", "Labels", "Assigned To"]

            for res in search_results:
                table.add_row([res.title, res.due_date, res.priority, res.labels, res.assignee])
            await ctx.send(embed=f"```\n{table.get_string()}\n```")
        else:
            #No results
            embed = discord.Embed(title="No Results", description="No tasks ahead. Relax Yourself!", color=discord.Color.green())
            await ctx.send(embed=embed)

    else:
        #No tag provided
        embed = discord.Embed(title="Invalid Args", description="Day ahead is not defined", color=discord.Color.red())
        await ctx.send(embed=embed)

@bot.command()
async def help(ctx):
    """Give commands list"""
    commands = {f"```{prefix}list_tasks <DaysAhead>```": "List of tasks with with due date from today until <DaysAhead>"}

    embed = discord.Embed(title="List of commands:", description="These are the commands to use with this bot", color=discord.Color.green())
    count = 1
    for command in commands:
          embed.add_field(name=str(count)+". "+ command, value=commands[command], inline=False)
          count += 1
    await ctx.send(embed=embed)

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=f"{prefix}help"))

#Getting discord token and running the bot
try:
    print(os.environ['DISCORD_AUTH'])
    token = str(os.environ['DISCORD_AUTH'])
    bot.run(token)
except:
    print("Invalid token")
