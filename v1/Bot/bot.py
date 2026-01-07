import asyncio
import datetime
import threading
import time
from datetime import date

import schedule
from dotenv import load_dotenv

import discord
from discord.ext import commands
import os

from prettytable import PrettyTable

from tagGiver import get_days_ahead, get_remind_days, get_remind_time
from search import (
    list_tasks_from_notion,
    filter_due_date_ahead,
    filter_op,
    filter_multiselect,
    filter_select,
    LabelsPropertyKey,
    EventsLabel,
    POLabel
)

load_dotenv()
prefix = ""
timezone='utc'

try:
    print(os.environ['PREFIX'])
    prefix = str(os.environ['PREFIX'])
except:
    prefix = '?'

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=prefix, help_command=None, intents=intents, allowed_mentions=discord.AllowedMentions(everyone=True))
bot.remove_command('help')

@bot.command(name="list_tasks")
async def list_tasks(ctx, *args):
    """Returns all tasks in specified due date"""
    if (len(args) > 0):
        #Check if the tag exists
        days_ahead = get_days_ahead(args)
        await ctx.send(embed=get_task_lists(datetime.timedelta(days=days_ahead)))

    else:
        #No tag provided
        embed = discord.Embed(title="Invalid Args", description="Day ahead is not defined", color=discord.Color.red())
        await ctx.send(embed=embed)

# @bot.command(name="remind")
# async def remind(ctx, *args):
#     """Returns all tasks in specified due date"""
#     if (len(args) <= 3):
#         #Check if the tag exists
#         remind_days = get_remind_days(args)
#         remind_time = get_remind_time(args,1)
#         days_ahead = get_days_ahead(args, 2)
#
#         job_id = schedule.every().minutes.at(":30").do(lambda: scheduled_get_task_list(datetime.timedelta(days=days_ahead)))
#
#         embed = discord.Embed(title="Reminder set", description=f"I will remind you tasks for {days_ahead} days ahead "
#                                                                 f"every {remind_days} days at {remind_time}\n"
#                                                                 f"", color=discord.Color.green())
#         await ctx.send(embed=embed)
#     else:
#         #No tag provided
#         embed = discord.Embed(title="Invalid Args", description=f"Missing arguments, see {prefix}help", color=discord.Color.red())
#         await ctx.send(embed=embed)

@bot.command()
async def help(ctx):
    """Give commands list"""
    commands = {f"```{prefix}list_tasks <DaysAhead>```": "List of tasks with with due date from today until <DaysAhead>"}
                # f"```{prefix}remind <RemindDays> <RemindTime> <DaysAhead>```": "Keep sending reminder of tasks with with due date from today until <DaysAhead>, every <RemindDays> days at <RemindTime>"}

    embed = discord.Embed(title="List of commands:", description="These are the commands to use with this bot", color=discord.Color.green())
    count = 1
    for command in commands:
          embed.add_field(name=str(count)+". "+ command, value=commands[command], inline=False)
          count += 1
    await ctx.send(embed=embed)

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=f"{prefix}help"))
    threading.Thread(target=run_scheduler, daemon=True).start()
    schedule.every().day.at("02:00").do(scheduled_reminder)

def scheduled_reminder():
    asyncio.run_coroutine_threadsafe(async_remind_task_list(), bot.loop)

async def async_remind_task_list():
    channel = bot.get_channel(int(os.environ['CHANNEL_ID']))
    if channel is None:
        return

    try:
        todays_tasks = list_tasks_from_notion(filter_due_date_ahead(5))
        if (len(todays_tasks) > 0):
            # Found a result
            embed = discord.Embed(title=f"Today's Task List", description=f"Hello @everyone! Reminder for today tasks",
                                  color=discord.Color.green())
            table = PrettyTable(["Task", "Due Date", "Priority", "Labels", "Assigned To"])

            for res in todays_tasks:
                table.add_row([res.title, res.due_date, res.priority, res.labels, res.assignee])

            embed.add_field(name="Task Table", value=table, inline=False)
            await channel.send(embed=embed)
    except Exception as e:
        print(e)


    try:
        events_7days_ahead_filter = filter_op("and",filter_due_date_ahead(40),filter_multiselect(LabelsPropertyKey,EventsLabel))
        search_results = list_tasks_from_notion(events_7days_ahead_filter)
        if (len(search_results) > 0):
            # Found a result
            embed = discord.Embed(title=f"Events List", description=f"Hello @everyone! Reminder for upcoming events",
                                  color=discord.Color.green())
            table = PrettyTable(["Task", "Due Date", "Priority", "Labels", "Assigned To"])

            for res in search_results:
                table.add_row([res.title, res.due_date, res.priority, res.labels, res.assignee])

            embed.add_field(name="Task Table", value=table, inline=False)
            await channel.send(embed=embed)
    except Exception as e:
        print(e)

def get_task_lists(days_ahead):
    search_results = list_tasks_from_notion(filter_due_date_ahead(days_ahead))

    if (len(search_results) > 0):
        # Found a result
        embed = discord.Embed(title=f"Task List", description=f"Tasks until {date.today() + days_ahead} @everyone",
                              color=discord.Color.green())
        table = PrettyTable(["Task", "Due Date", "Priority", "Labels", "Assigned To"])

        for res in search_results:
            table.add_row([res.title, res.due_date, res.priority, res.labels, res.assignee])

        embed.add_field(name="Task Table", value=table, inline=False)
    else:
        # No results
        embed = discord.Embed(title="No Results", description="No tasks ahead. Relax Yourself!",
                              color=discord.Color.green())
    return embed

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

#Getting discord token and running the bot
try:
    token = str(os.environ['DISCORD_TOKEN'])
    bot.run(token)
except Exception as e:
    print(e)
