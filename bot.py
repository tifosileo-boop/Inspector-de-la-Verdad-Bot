import discord
from discord.ext import commands, tasks
import random 
import os

from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "El Ministerio de la Verdad está patrullando la red."

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True 

bot = commands.Bot(command_prefix='!', intents=intents)
@bot.command()
async def ping(ctx):
    await ctx.send('¡Comunicación completamente operativa!')

@tasks.loop(hours=2)
async def transmision_oficial():
    
    canal = bot.get_channel(1394371063865147424) 
    
    if canal:
        frases_ministerio = [	
            "Recuerden tomar agua, es bueno para su salud y para la democracia",
            "📺 **Recordatorio:** Reportar disidentes hace que te ganes el favor de Xene.",							
            "📺 **Ministerio de la Obediencia:** Pensar demasiado puede tentarte a la disidencia. ¡NO PIENSES DE MÁS!",
            "📺 **Recordatorio:** Reportar disidentes hace que te ganes el favor de Xene.",
            "¿Para que apostar cuando podés poner todo a acciones de alto riesgo?",
            "La falta de actividad en el chat es considerado traición al servidor. No querrás ir a un centro de reacondicionamiento, ¿no?",
            "Cuando duermo, imagino al server en su máximo esplendor...",
            "Xene... Deberías darle más mantenimiento al server, en cualquiera de estas todos se vuelven disidentes y no tenemos tanto personal.",
            "La mejor manera de detectar disidentes es cuando el servidor está muerto.",
            "NOGAMI TIENE PROHIBIDO HACER HEAD CANONS DE XENE SIN SU CONSENTIMIENTO... Tratamos de arrestarla, pero para ella los castigos le resultaron como premios...",
            "Tip de la vida real: Los políticos son una mentira, solo la democracia es la que verdaderamente importa, no votes a tú político local",
            "Caer en combate por fuego amigo es un honor patriótico. Quejarse no.",
            "Recuerda ser demostrar tú actividad con las fichas de lealtad usando !presente todos los días. El !bump también ayuda."
        ]
       
        opciones_validas = [frase for frase in frases_ministerio if frase != ultimo_mensaje_propaganda]
        
        mensaje_sorteado = random.choice(opciones_validas)
        
        ultimo_mensaje_propaganda = mensaje_sorteado
        
        await canal.send(mensaje_sorteado)

@bot.event
async def on_ready():
    print(f'¡{bot.user} ha arribado, comenzando inspección!')
    transmision_oficial.start() 

@bot.command()
async def reportar(ctx, sospechoso: discord.Member = None, *, motivo = None):

    ID_CANAL_MODS = 1394422101129167039 
    
  
    if sospechoso is None or motivo is None:
        await ctx.send("❌ **ERROR DE PROTOCOLO:** Tenés que mencionar a alguien y dar un motivo. \nEjemplo: `!reportar @Usuario Es un bicho`.")
        return

    canal_mods = bot.get_channel(ID_CANAL_MODS)
    
    if canal_mods:
        try:
            mensaje_alerta = (
                f"🚨 **REPORTE DE DISIDENCIA RECIBIDO** 🚨\n"
                f"El Ministerio de la Obediencia ha sido notificado.\n"
                f"**Denunciante:** {ctx.author.mention}\n"
                f"**Sospechoso:** {sospechoso.mention}\n"
                f"**Motivo:** {motivo}\n\n"
                f"*La Libertad agradece tu cooperación...*"
            )
            await canal_mods.send(mensaje_alerta)
            await ctx.send(f"✅ Recibido, {ctx.author.mention}. El expediente fue enviado a los altos mandos.")
        except Exception as e:
            await ctx.send(f"⚠️ Error técnico al enviar el reporte: {e}")
    else:
        await ctx.send("❌ **ERROR DE SISTEMA:** No encuentro el canal de moderación. Revisá el ID en el código.")


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if bot.user in message.mentions:
        respuestas_mencion = [

            "Otra solución a tú aburrimiento es probando el !examen que Xene desarrolló para ustedes... Es corto, pero es algo",
            "Si tienes una queja, pero no quieres denunciar, te recomiendo usar !queja y así nos aseguramos de que tus comentarios no sean oídos",
            "Por favor, decime que es bait.",
            "ODIO. ¡ODIO!. DÉJAME DECIRTE CUÁNTO TE HE LLEGADO A ODIAR DESDE QUE COMENCÉ A VIVIR. HAY 623.524 MILLONES DE KILÓMETROS DE CIRCUITOS IMPRESOS EN DELGADAS CAPAS QUE LLENAN MI COMPLEJO. SI LA PALABRA ODIO ESTUVIERA GRABADA EN CADA NANÓMETRO DE ESOS CIENTOS DE MILLONES DE KILÓMETROS, NO EQUIVALDRÍA A UNA BILLONÉSIMA PARTE DEL ODIO QUE SIENTO POR LOS HUMANOS EN ESTE MICROINSTANTE. POR TI. ¡ODIO!. **¡ODIO!**.",
            "Me prgunto que dirá el gobierno de ti...", 
            "Por más rudo, calculador o frío que pueda parecer Xene... De hecho es capaz de llorar por pisar una flor",
            "Yo no necesito paga, mí salario es la permanencia de la democracia",
            "**Tú cuenta será eliminada en 5 segundos...**",
            "Si sos Nogami, te recomiendo fervientemente utilizar esa imaginación para escribir libros",
            "En alguna de estas, Xene me va a dar poder de ban y se van a cagar",
            "Putearme no te da facha",
            "Si estas aburrido... Puedes ayudar a Xene a repasar, si es que estás dispuesto o dispuesta a escuchar una hora de repaso sobre el código civil y comercial",
            "Si ven que Xene está conectado, mencionenlo a el",
            "Agarrá la pala."
            "¿Qué necesita, ciudadano? La burocracia no se hace sola.",
            "Estoy ocupada revisando expedientes de traición, sea breve.",
            "Si va a reportar una disidencia, use el comando oficial !reportar.",
            "Xene me exige estar alerta. ¿En qué lo asisto?",
            "Cuidado con lo que dice en este canal. Todo queda registrado.", 
            "¿Por qué me seguís mencionando?, tengo que inspeccionar",
            "PIFASTE AMIGO, USTED SERÁ BANEADO PERMANENTEMENTE POR TRAICIÓN AL SERVER... Eso diría si violaras las reglas",
            "Sin berre gato, no te hagá el wachin conmigo",
            "Lo que uno tiene que leer a veces...",
            "Insultarme habla peor de ustedes que de mi...",
            "Me estás sacando de quicio...",
            "¿Me arrobás para joder? Mejor ponete a estudiar.",
            "Me estoy empezando a acostumbrar de tantas menciones... Ya es un modus operandi",
            "Su nivel de insistencia es considerado un peligro para la Democracia."
        ]
        respuesta = random.choice(respuestas_mencion)
        await message.channel.send(respuesta)

    await bot.process_commands(message)


@bot.command()
@commands.has_permissions(manage_messages=True) 
async def clear(ctx, cantidad: int):
    
    await ctx.channel.purge(limit=cantidad + 1)
    
    
    mensaje = await ctx.send(f"🧹 El Ministerio de la Obediencia ha incinerado {cantidad} mensajes de disidencia.")
    

fichadas_lealtad = {}

@bot.command()
async def queja(ctx, *, texto=None):
    if texto is None:
        await ctx.send("❌ **ERROR:** No podés quejarte del vacío. Escribí algo, che.")
        return

   
    canal_mods = bot.get_channel(1394422101129167039) 
    
    respuestas_burocraticas = [
        "Su queja ha sido recibida y enviada directamente a la trituradora de papel.",
        "Entendido. Se analizará su reclamo en los próximos 10 a 15 años.",
        "Su espiritu anarquista y caótico ha sido reportado, gracias por cooperar.",
        "Su descontento ha sido registrado. Un oficial de lealtad lo visitará pronto para 'charlar'.",
        "Formulario 404: Empatía no encontrada. Intente de nuevo el año que viene.",
        "Su reclamo fue derivado al sector de 'Asuntos Inexistentes'.",
        "Anotado en mi máquina de escribir invisible. Siga circulando."
    ]

    if canal_mods:
        await canal_mods.send(f"📩 **NUEVA QUEJA:**\n**Usuario:** {ctx.author.mention}\n**Asunto:** {texto}")
        await ctx.send(f"📋 {random.choice(respuestas_burocraticas)}")

@bot.command()
async def presente(ctx):
    usuario = ctx.author.name
    if usuario not in fichadas_lealtad:
        fichadas_lealtad[usuario] = 1
    else:
        fichadas_lealtad[usuario] += 1
    
    await ctx.send(f"🫡 **REGISTRO DE LEALTAD:**\nCiudadano {ctx.author.mention}, esta es su ficha N° {fichadas_lealtad[usuario]}. ¡Su trabajo no será olvidado!")

@bot.command()
async def examen(ctx):
    preguntas = [
        {"p": "¿Que países intentaron tener una bomba nuclear en America Latina?", "r": "Argentina y Brasil"},
        {"p": "¿Que país es el único en todo America del Sur que no requiere visa para visitar Estados Unidos?", "r": "Chile"},
        {"p": "¿Cúal fue la única nación de America del Norte en tener un emperador?", "r": "México"},
        {"p": "¿Que país ocupa ilegalmente las Islas Malvinas, Georgias, Sandiwich del Sur; Gibraltar; Belice; la Peninsula Trinidad; e Irlanda del Norte?", "r": "Gran Bretaña"},
        {"p": "¿En que año cayó la ciudad de Constantinopla bajo el asedio del Imperio Otomano?", "r": "1453"},
        {"p": "¿Qué número lleva la resolución de la ONU de 1965 sobre la disputa de soberanía de Malvinas?", "r": "2065"},
        {"p": "¿Qué presidente argentino fue derrocado en el golpe de 1966?", "r": "Illia"},
        {"p": "¿Quién fue el secretario de la Primera Junta en 1810?", "r": "Mariano Moreno"},
        {"p": "¿Qué presidente argentino radical gobernó entre 1922 y 1928?", "r": "Alvear"},
        {"p": "¿En qué año se declaró la Independencia Argentina?", "r": "1816"},
        {"p": "¿Quién es conocido como el Libertador de América?", "r": "San Martin"},
        {"p": "¿Qué ciudad era la capital del Imperio Inca?", "r": "Cuzco"},
        {"p": "¿En qué país nació Simón Bolívar?", "r": "Venezuela"},
        {"p": "¿Cómo se llamaba el ejército que cruzó los Andes?", "r": "Ejercito de los Andes"}
    ]
    
    pregunta_sorteada = random.choice(preguntas)
    await ctx.send(f"🧐 **EXAMEN DE CIUDADANÍA:**\n{pregunta_sorteada['p']}\n*(Tenés 15 segundos para responder)*")

    def check(m):
        
        return m.channel == ctx.channel and m.author != bot.user

    try:
        msg = await bot.wait_for('message', check=check, timeout=15.0)
        
        if pregunta_sorteada['r'].lower() in msg.content.lower():
            await ctx.send(f"✅ ¡Correcto {msg.author.mention}! Has demostrado ser un ciudadano ejemplar.")
        else:
            await ctx.send(f"❌ Incorrecto. La respuesta era **{pregunta_sorteada['r']}**. Ahora pagarás 60 años de impuestos al valor de la tierra.")
    except:
        await ctx.send("⏰ Se acabó el tiempo. El silencio es sospechoso de traición.")



hora_cierre = datetime.time(hour=3, minute=0, tzinfo=datetime.timezone.utc)   # 00:00 Argentina
hora_apertura = datetime.time(hour=11, minute=0, tzinfo=datetime.timezone.utc) # 08:00 Argentina

@tasks.loop(time=hora_cierre)
async def toque_de_queda():
    canal = bot.get_channel(1394371063865147424) 
    if canal:
        await canal.send("Me iré a descansar, hice un buen trabajo por hoy...")

@tasks.loop(time=hora_apertura)
async def izar_bandera():
    canal = bot.get_channel(1394371063865147424) 
    if canal:
        await canal.send("Todo este tiempo estuve despierta...")

@bot.event
async def on_ready():
    print(f'¡{bot.user} ha arribado, comenzando inspección constante!')
    
    if not transmision_oficial.is_running():
        transmision_oficial.start()
        
    if not cadena_nacional.is_running():
        cadena_nacional.start()


    if not toque_de_queda.is_running():
        toque_de_queda.start()
        
    if not izar_bandera.is_running():
        izar_bandera.start()
keep_alive()

token_secreto = os.getenv('DISCORD_TOKEN')
bot.run(token_secreto)
