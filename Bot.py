import discord
import random
import datetime
import asyncio
from bot_logic import *

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

# Diccionario de comandos y descripciones
commands = {
    '/hello': 'Saludar',
    '/emoji': 'Generar un emoji aleatorio',
    '/coin': 'Lanzar una moneda (cara o cruz)',
    '/pass': 'Generar una contraseña aleatoria',
    '/riddle': 'Obtener un acertijo aleatorio',
    '/calc': 'Calculadora',
    '/reminder': 'Recordar un evento',
    '/events': 'Ver todos los eventos programados'
}

# Diccionario de acertijos y respuestas
riddles = {
    "¿Qué es lo que tiene ojos y no puede ver?": "Una aguja",
    "¿Qué es lo que tiene cabeza y no puede pensar?": "Un clavo",
    "¿Qué cosa es siempre tuya, pero la usan más los demás que tú?": "Tu nombre",
    "Tiene nombre de flor y no es una flor, ¿qué es?": "La rosa",
    "¿Qué pesa más, un kilo de algodón o un kilo de hierro?": "Ambos pesan lo mismo",
    "¿Qué tiene dientes y no puede comer?": "El peine",
    "¿Qué tiene ríos pero no agua, ciudades pero no edificios y bosques pero no árboles?": "Un mapa"
}

# Diccionario para mapear respuestas acertijos
user_answers = {}
# Diccionario para almacenar eventos y sus fechas
eventos = {}

@client.event
async def on_ready():
    print(f'Iniciamos sesión como {client.user}')
    await verificar_eventos()

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('/hello'):
        await message.channel.send('Hi!')
    elif message.content.startswith('/emoji'):
        await message.channel.send(gen_emoji())
    elif message.content.startswith('/coin'):
        await message.channel.send(flip())
    elif message.content.startswith('/pass'):
        await message.channel.send(gen_pass(10))
    elif message.content.startswith('/riddle'):
        await send_riddle(message.channel)
    elif message.content.startswith('/calc'):
        await calcular_expresion(message)
    elif message.content.startswith('/reminder'):
        await recordar_evento(message)
    elif message.content.startswith('/events'):
        await ver_eventos(message.channel)
    elif message.content.startswith('/help'):
        await send_help(message.channel)
    elif message.content in riddles.values():
        await check_answer(message)
    elif message.content in user_answers.keys():
        await check_user_answer(message)
    else:
        await message.channel.send("No puedo procesar este comando, ¡lo siento!")

async def send_riddle(channel):
    random_riddle = random.choice(list(riddles.keys()))
    correct_answer = riddles[random_riddle]
    user_answers[random_riddle] = correct_answer
    await channel.send(f"Aquí tienes un acertijo: {random_riddle}")

async def check_answer(message):
    user_answer = message.content
    riddle = [riddle for riddle, answer in riddles.items() if answer == user_answer]
    if riddle:
        await message.channel.send("¡Correcto! ¡Has resuelto el acertijo!")
        del user_answers[riddle[0]]
    else:
        await message.channel.send("Incorrecto. ¡Sigue intentándolo!")

async def check_user_answer(message):
    user_answer = message.content
    correct_answer = user_answers[user_answer]
    if user_answer == correct_answer:
        await message.channel.send("¡Correcto! ¡Has resuelto el acertijo!")
        del user_answers[user_answer]
    else:
        await message.channel.send("Incorrecto. ¡Sigue intentándolo!")

async def send_help(channel):
    help_message = "Comandos disponibles:\n"
    for command, description in commands.items():
        help_message += f"{command}: {description}\n"
    await channel.send(help_message)

async def calcular_expresion(message):
    expresion = message.content[5:].strip()  # Elimina '/calc' del mensaje
    try:
        resultado = eval(expresion)
        await message.channel.send(resultado)
    except Exception as e:
        await message.channel.send(f"Error: {e}")

async def recordar_evento(message):
    try:
        _, fecha, evento = message.content.split(' ', 2)
        fecha = datetime.datetime.strptime(fecha, "%d/%m/%Y")
        canal_id = message.channel.id  # Obtener el ID del canal
        eventos[evento] = (fecha, canal_id)  # Almacenar la fecha y el ID del canal
        await message.channel.send(f"Evento añadido: {evento}, fecha: {fecha.strftime('%d/%m/%Y')}")
    except ValueError:
        await message.channel.send("Formato de fecha incorrecto. Usa DD/MM/AAAA")

async def ver_eventos(channel):
    if eventos:
        mensaje = "Eventos programados:\n"
        for evento, (fecha, _) in eventos.items():  # Se extrae el ID del canal
            mensaje += f"{evento}: {fecha.strftime('%d/%m/%Y')}\n"
        await channel.send(mensaje)
    else:
        await channel.send("No hay eventos programados.")

async def verificar_eventos():
    while True:
        now = datetime.datetime.now()
        for evento, (fecha, canal_id) in list(eventos.items()):  # Se extrae el ID del canal
            if fecha.date() == now.date():
                canal = client.get_channel(canal_id)  # Obtener el canal a partir del ID
                if canal:
                    await canal.send(f"Hoy es el día del evento: {evento}!")
                del eventos[evento]
        await asyncio.sleep(60)

client.run("token")
