import os
import asyncio
import discord
from discord.ext import commands, tasks
from itertools import cycle
from game import UNOGame
from discord.ui import Button, View

with open("token.txt", "r") as f:
    token = f.read()

bot=commands.Bot(command_prefix='u!',intents=discord.Intents.all())
uno_game = UNOGame()

bot_status=cycle(["Waiting for a ping...","AFK but never away!","Always watching","Chilling in the server"])
@tasks.loop(seconds=30)
async def change_bot_status():
    await bot.change_presence(activity=discord.Game(next(bot_status)))
    

@bot.event
async def on_ready():
    print(f'Logged on as {bot.user}!')
    change_bot_status.start()

@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")
    
@bot.command()
async def echo(ctx, *, message: str):
    await ctx.send(message)
    
@bot.command()
async def create(ctx):
    if not uno_game.game_created:
        uno_game.game_created = True
        uno_game.game_creator = ctx.author.id
        uno_game.players[ctx.author.id] = []
        await ctx.send(f"UNO game has started! Players can join using `u!join`. Game created by {ctx.author.name}.")
    else:
        await ctx.send("A game has already been created. Use `u!reset` to reset the game.")
    
@bot.command()
async def start(ctx):
    if not uno_game.game_created:
        await ctx.send("No game has been created yet.")
        return
    if ctx.author.id != uno_game.game_creator:
        await ctx.send(f"Only {uno_game.game_creator} can start the game.")
        return
    uno_game.start_game()
    
    embed = discord.Embed(
        title="🎉 UNO Game Board 🎉",
        description="The game has started! Here's the current board:",
        color=discord.Color.blue()
    )
    current_card = uno_game.get_current_card().replace(" ", "")
    card_image_path = f"./cards/{current_card}.png"
    embed.add_field(name="Current Card", value=str(current_card), inline=False)
    
    try:
        file = discord.File(card_image_path, filename="card.png")
        embed.set_image(url="attachment://card.png")
    except FileNotFoundError:
        await ctx.send(f"Card image for {current_card} not found.")
        return
    
    players = uno_game.get_players()
    if players:
        player_list = "\n".join([f"- {bot.get_user(player_id).name}" for player_id in players])
        embed.add_field(name="Players", value=player_list, inline=False)
    else:
        embed.add_field(name="Players", value="No players in the game yet.", inline=False)
    
    current_player_id = uno_game.current_player
    if current_player_id:
        current_player_name = bot.get_user(current_player_id).name
        embed.add_field(name="Current Turn", value=f"It's {current_player_name}'s turn!", inline=False)
    else:
        embed.add_field(name="Current Turn", value="No current player yet.", inline=False)
    class CardView(discord.ui.View):
        def __init__(self):
            super().__init__()
        @discord.ui.button(label="View Your Cards", style=discord.ButtonStyle.primary)
        async def view_cards(self, interaction: discord.Interaction, button: discord.ui.Button):
            player_id = interaction.user.id
            player_cards = uno_game.get_player_cards(player_id)
            print(f"Player ID: {player_id}")
            print(f"Player's Cards: {player_cards}")
            self.clear_items()
            for card in player_cards:
                card_button = discord.ui.Button(label=card, style=discord.ButtonStyle.secondary)
                card_button.custom_id = card
                card_button.callback = self.card_button_callback
                self.add_item(card_button)
            await interaction.response.edit_message(content="Your cards:", view=self)
        
        async def card_button_callback(self, interaction: discord.Interaction):
            card_played = interaction.data['custom_id']
            await interaction.response.send_message(f"You played: {card_played}", ephemeral=True)
    view = CardView()
    await ctx.send(embed=embed, file=file, view=view)


@bot.command()
async def join(ctx):
    if uno_game.add_player(ctx.author.id) and uno_game.game_created:
        uno_game.players[ctx.author.id] = []
        await ctx.send(f"{ctx.author.name} has joined the game!")
    elif not uno_game.game_created:
        await ctx.send("The game has not been created yet. Use u!creategame to create a game.")
    else:
        await ctx.send("You're already in the game!")

@bot.command()
async def board(ctx):
    if not uno_game.game_created:
        await ctx.send("No game has been created yet.")
        return

    players = uno_game.get_players()
    if not players:
        await ctx.send("No players have joined the game yet.")
        return
    current_player_id = uno_game.current_player
    embed = discord.Embed(
        title="🎮 Current Players in the UNO Game 🎮",
        description="Here are the players and their remaining cards:",
        color=discord.Color.green()
    )
    embed.add_field(name="Players", value="👥 **Players**", inline=True)
    embed.add_field(name="Cards Left", value="🃏 **Cards Left**", inline=True)
    embed.add_field(name="\u200B", value="---------------------------------", inline=False)
    for player_id, card_count in players.items():
        player = await bot.fetch_user(player_id)
        player_name = player.name
        if player_id == current_player_id:
            player_name = f"→ {player_name} (It's your turn!)"
        embed.add_field(name=f"👤 {player_name}", value=f"{len(card_count)} cards", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def hand(ctx):
    player_id = ctx.author.id
    if not uno_game.game_created:
        await ctx.send("No game has been created yet.")
        return
    if player_id not in uno_game.players:
        await ctx.send("You are not in the game.")
        return
    player_cards = uno_game.get_player_cards(player_id)
    if not player_cards:
        await ctx.send("You have no cards in hand.")
        return
    embed = discord.Embed(
        title=f"{ctx.author.name}'s Hand",
        description="Here are the cards you currently hold:",
        color=discord.Color.blue()
    )
    for card in player_cards:
        embed.add_field(name=card, value="\u200B", inline=True)
    await ctx.send(embed=embed)

@bot.command()
async def play(ctx, card: str):
    if uno_game.play_card(ctx.author.id, card):
        await ctx.send(f"{ctx.author.name} has played {card}")
    else:
        await ctx.send("You can't play that card!")

async def main():
    try:
        async with bot:
            await bot.start(token)
    except Exception as e:
        print(f"Error starting bot: {e}")

@bot.command()
async def reset(ctx):
    if ctx.author.id == uno_game.game_creator:
        uno_game.reset_game()
        await ctx.send("The game has been aborted by the creator. Thanks for playing!")
    else:
        await ctx.send("Only the game creator can abort the game!")

asyncio.run(main())