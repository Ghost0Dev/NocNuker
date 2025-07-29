import discord
from discord.ext import commands
import os
import asyncio
import json
import threading

with open('config.json') as f:
    config = json.load(f)

bot_token = config['bot_token']
servers = config['servers']
MENU_COLOR = config.get('menu_color', '#0099ff')  
CREATOR = config.get('creator', 'ghost0dev')


ASCII_ART = """
 ███▄    █  █    ██  ██ ▄█▀▓█████  ██▀███
 ██ ▀█   █  ██  ▓██▒ ██▄█▒ ▓█   ▀ ▓██ ▒ ██▒
▓██  ▀█ ██▒▓██  ▒██░▓███▄░ ▒███   ▓██ ░▄█ ▒
▓██▒  ▐▌██▒▓▓█  ░██░▓██ █▄ ▒▓█  ▄ ▒██▀▀█▄
▒██░   ▓██░▒▒█████▓ ▒██▒ █▄░▒████▒░██▓ ▒██▒
░ ▒░   ▒ ▒ ░▒▓▒ ▒ ▒ ▒ ▒▒ ▓▒░░ ▒░ ░░ ▒▓ ░▒▓░
░ ░░   ░ ▒░░░▒░ ░ ░ ░▒ ▒░ ░ ░  ░  ░▒ ░ ▒░
   ░   ░ ░  ░░░ ░ ░ ░ ░░ ░    ░     ░░   ░
         ░    ░     ░  ░      ░  ░   ░
"""


def hex_to_ansi(hex_color):
    hex_color = hex_color.lstrip('#')
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    return f'\033[38;2;{r};{g};{b}m'

MENU_COLOR_ANSI = hex_to_ansi(MENU_COLOR)
RESET_COLOR_ANSI = '\033[0m'


intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)


def find_guild(bot, name_or_id):
    for guild in bot.guilds:
        if str(guild.id) == name_or_id or guild.name == name_or_id:
            return guild
    return None

def run_async_action(coro):
    future = asyncio.run_coroutine_threadsafe(coro, bot.loop)
    try:
        future.result()
    except Exception as e:
        print(f"An error occurred: {e}")

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    clear_screen()
    print(f'{MENU_COLOR_ANSI}{ASCII_ART}{RESET_COLOR_ANSI}')
    print(f'{MENU_COLOR_ANSI}by {CREATOR}{RESET_COLOR_ANSI}')

def interactive_menu():
    current_guild = None
    while True:
        print_header()
        if not current_guild:
            current_guild = server_selection_menu()
            if not current_guild:
                break # Exit
        else:
            if not action_menu(current_guild):
                current_guild = None 


def server_selection_menu():
    print(f'{MENU_COLOR_ANSI}Choose a server:{RESET_COLOR_ANSI}')
    for idx, server in enumerate(servers, start=1):
        print(f'{MENU_COLOR_ANSI}{idx}. {server["name"]} (ID: {server["id"]}){RESET_COLOR_ANSI}')
    print(f'{MENU_COLOR_ANSI}0. Exit{RESET_COLOR_ANSI}')

    server_choice = input("Enter your choice: ")

    if server_choice == '0':
        print(f'{MENU_COLOR_ANSI}Exiting...{RESET_COLOR_ANSI}')
        run_async_action(bot.close())
        return None

    try:
        server_choice = int(server_choice)
        if 1 <= server_choice <= len(servers):
            selected_server = servers[server_choice - 1]
            guild = find_guild(bot, selected_server['id'])
            if guild:
                print(f'{MENU_COLOR_ANSI}Selected server: {guild.name} (ID: {guild.id}){RESET_COLOR_ANSI}')
                return guild
            else:
                print(f'{MENU_COLOR_ANSI}Server not found.{RESET_COLOR_ANSI}')
                return None
        else:
            print(f'{MENU_COLOR_ANSI}Invalid choice.{RESET_COLOR_ANSI}')
            return None
    except ValueError:
        print(f'{MENU_COLOR_ANSI}Invalid input. Please enter a number.{RESET_COLOR_ANSI}')
        return None

def action_menu(guild):
    while True:
        print_header()
        print(f'{MENU_COLOR_ANSI}Current Server: {guild.name} (ID: {guild.id}){RESET_COLOR_ANSI}')
        print(f'{MENU_COLOR_ANSI}Choose a category:{RESET_COLOR_ANSI}')
        print(f'{MENU_COLOR_ANSI}1. Channel Actions{RESET_COLOR_ANSI}')
        print(f'{MENU_COLOR_ANSI}2. Member Actions{RESET_COLOR_ANSI}')
        print(f'{MENU_COLOR_ANSI}3. Server Actions{RESET_COLOR_ANSI}')
        print(f'{MENU_COLOR_ANSI}0. Back to server selection{RESET_COLOR_ANSI}')

        category_choice = input("Enter your choice: ")

        if category_choice == '0':
            return False # Go back

        if category_choice == '1':
            channel_actions_menu(guild)
        elif category_choice == '2':
            member_actions_menu(guild)
        elif category_choice == '3':
            server_actions_menu(guild)
        else:
            print(f'{MENU_COLOR_ANSI}Invalid choice.{RESET_COLOR_ANSI}')

def channel_actions_menu(guild):
    while True:
        print_header()
        print(f'{MENU_COLOR_ANSI}Channel Actions for: {guild.name}{RESET_COLOR_ANSI}')
        print(f'{MENU_COLOR_ANSI}1. Delete All Channels{RESET_COLOR_ANSI}')
        print(f'{MENU_COLOR_ANSI}2. Create Channels{RESET_COLOR_ANSI}')
        print(f'{MENU_COLOR_ANSI}3. Spam Messages{RESET_COLOR_ANSI}')
        print(f'{MENU_COLOR_ANSI}4. Create & Spam{RESET_COLOR_ANSI}')
        print(f'{MENU_COLOR_ANSI}5. Send Embed{RESET_COLOR_ANSI}')
        print(f'{MENU_COLOR_ANSI}6. Tag @everyone{RESET_COLOR_ANSI}')
        print(f'{MENU_COLOR_ANSI}0. Back to categories{RESET_COLOR_ANSI}')

        choice = input("Enter your choice: ")

        if choice == '0':
            break

        if choice == '1':
            async def delete_all_channels():
                await asyncio.gather(*[channel.delete() for channel in guild.channels])
            run_async_action(delete_all_channels())
        elif choice == '2':
            channel_name = input("Enter the channel name: ")
            channel_count = int(input("Enter the number of channels to create: "))
            async def create_channels():
                await asyncio.gather(*[guild.create_text_channel(channel_name) for _ in range(channel_count)])
            run_async_action(create_channels())
        elif choice == '3':
            channel_name = input("Enter the channel name (or 'all' for all channels): ")
            message_content = input("Enter the message content: ")
            async def spam_messages():
                if channel_name.lower() == 'all':
                    await asyncio.gather(*[channel.send(message_content) for channel in guild.text_channels])
                else:
                    channel = discord.utils.get(guild.channels, name=channel_name)
                    if channel:
                        message_count = int(input("Enter the number of messages to spam: "))
                        await asyncio.gather(*[channel.send(message_content) for _ in range(message_count)])
                    else:
                        print(f'{MENU_COLOR_ANSI}Channel not found.{RESET_COLOR_ANSI}')
            run_async_action(spam_messages())
        elif choice == '4':
            channel_name = input("Enter the channel name: ")
            message_content = input("Enter the message content: ")
            channel_count = int(input("Enter the number of channels to create: "))
            message_count = int(input("Enter the number of messages to spam per channel: "))
            async def create_and_spam():
                for _ in range(channel_count):
                    new_channel = await guild.create_text_channel(channel_name)
                    await asyncio.gather(*[new_channel.send(message_content) for _ in range(message_count)])
            run_async_action(create_and_spam())
        elif choice == '5':
            channel_name = input("Enter the channel name (or 'all' for all channels): ")
            embed_title = input("Enter the embed title: ")
            embed_description = input("Enter the embed description: ")
            embed = discord.Embed(title=embed_title, description=embed_description)
            async def send_embeds():
                if channel_name.lower() == 'all':
                    await asyncio.gather(*[channel.send(embed=embed) for channel in guild.text_channels])
                else:
                    channel = discord.utils.get(guild.channels, name=channel_name)
                    if channel:
                        await channel.send(embed=embed)
                    else:
                        print(f'{MENU_COLOR_ANSI}Channel not found.{RESET_COLOR_ANSI}')
            run_async_action(send_embeds())
        elif choice == '6':
            async def tag_everyone():
                await asyncio.gather(*[channel.send("@everyone") for channel in guild.text_channels])
            run_async_action(tag_everyone())
        else:
            print(f'{MENU_COLOR_ANSI}Invalid choice.{RESET_COLOR_ANSI}')

        print(f'{MENU_COLOR_ANSI}Action completed.{RESET_COLOR_ANSI}')
        input("Press Enter to continue...")

def member_actions_menu(guild):
    while True:
        print_header()
        print(f'{MENU_COLOR_ANSI}Member Actions for: {guild.name}{RESET_COLOR_ANSI}')
        print(f'{MENU_COLOR_ANSI}1. Ban All Members{RESET_COLOR_ANSI}')
        print(f'{MENU_COLOR_ANSI}2. Kick All Members{RESET_COLOR_ANSI}')
        print(f'{MENU_COLOR_ANSI}3. Send Message to All Members{RESET_COLOR_ANSI}')
        print(f'{MENU_COLOR_ANSI}0. Back to categories{RESET_COLOR_ANSI}')

        choice = input("Enter your choice: ")

        if choice == '0':
            break

        if choice == '1':
            async def ban_all_members():
                await asyncio.gather(*[member.ban() for member in guild.members])
            run_async_action(ban_all_members())
        elif choice == '2':
            async def kick_all_members():
                await asyncio.gather(*[member.kick() for member in guild.members])
            run_async_action(kick_all_members())
        elif choice == '3':
            message_content = input("Enter the message content: ")
            async def message_all_members():
                await asyncio.gather(*[member.send(message_content) for member in guild.members], return_exceptions=True)
            run_async_action(message_all_members())
        else:
            print(f'{MENU_COLOR_ANSI}Invalid choice.{RESET_COLOR_ANSI}')

        print(f'{MENU_COLOR_ANSI}Action completed.{RESET_COLOR_ANSI}')
        input("Press Enter to continue...")

def server_actions_menu(guild):
    while True:
        print_header()
        print(f'{MENU_COLOR_ANSI}Server Actions for: {guild.name}{RESET_COLOR_ANSI}')
        print(f'{MENU_COLOR_ANSI}1. Change Server Name{RESET_COLOR_ANSI}')
        print(f'{MENU_COLOR_ANSI}2. Remove all Roles{RESET_COLOR_ANSI}')
        print(f'{MENU_COLOR_ANSI}0. Back to categories{RESET_COLOR_ANSI}')

        choice = input("Enter your choice: ")

        if choice == '0':
            break

        if choice == '1':
            new_name = input("Enter the new server name: ")
            async def change_server_name():
                await guild.edit(name=new_name)
            run_async_action(change_server_name())
        elif choice == '2':
            async def delete_all_roles():
                await asyncio.gather(*[role.delete() for role in guild.roles if role.name != "@everyone"])
            run_async_action(delete_all_roles())
        else:
            print(f'{MENU_COLOR_ANSI}Invalid choice.{RESET_COLOR_ANSI}')

        print(f'{MENU_COLOR_ANSI}Action completed.{RESET_COLOR_ANSI}')
        input("Press Enter to continue...")

@bot.event
async def on_ready():
    print_header()
    print(f'{MENU_COLOR_ANSI}Bot is logged in as {bot.user}{RESET_COLOR_ANSI}')
    thread = threading.Thread(target=interactive_menu, daemon=True)
    thread.start()

async def main():
    async with bot:
        await bot.start(bot_token)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot is shutting down.")
