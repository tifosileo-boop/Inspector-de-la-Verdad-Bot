import discord
from discord.ext import commands, tasks
import random 
import os
import datetime
from flask import Flask
from threading import Thread
import json
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
app = Flask('')

@app.route('/')
def home():
    return "El Ministerio de la Verdad está patrullando la red."

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()
credenciales_json = os.getenv('FIREBASE_CREDENTIALS')
firebase_url = os.getenv('FIREBASE_URL')

if credenciales_json and firebase_url:
    cred_dict = json.loads(credenciales_json)
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred, {
        'databaseURL': firebase_url
    })
    print("📂 Base de datos ministerial en línea.")
else:
    print("⚠️ ADVERTENCIA: Faltan credenciales burocráticas de Firebase en Render.")
intents = discord.Intents.default()
intents.message_content = True
intents.members = True 

bot = commands.Bot(command_prefix='!', intents=intents)
@bot.command()
async def ping(ctx):
    await ctx.send('¡Comunicación completamente operativa!')

ultimo_mensaje_propaganda = ""
@tasks.loop(hours=2) 
async def transmision_oficial():
    global ultimo_mensaje_propaganda
    canal = bot.get_channel(1394371063865147424) 
    if canal:
        ahora_utc = datetime.datetime.now(datetime.timezone.utc)
        hora_argentina = (ahora_utc - datetime.timedelta(hours=3)).hour
        if 0 <= hora_argentina < 8:
            return 
        ultimo_mensaje = None
        async for msg in canal.history(limit=1):
            ultimo_mensaje = msg           
        if ultimo_mensaje:
            if ultimo_mensaje.author == bot.user:
                return 
            diferencia = ahora_utc - ultimo_mensaje.created_at 
            if diferencia.total_seconds() > 10800:
                return

        frases_ministerio = [	
            "Recuerden tomar agua, es bueno para su salud y para la democracia",
            "📺 **Recordatorio:** Reportar disidentes hace que te ganes el favor de Xene.",							
            "📺 **Ministerio de la Obediencia:** Pensar demasiado puede tentarte a la disidencia. ¡NO PIENSES DE MÁS!",
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

conteo_reportes = {}

@bot.command()
async def reportar(ctx, sospechoso: discord.Member = None, *, motivo = None):
    ID_CANAL_MODS = 1394422101129167039 

    if sospechoso is None or motivo is None:
        await ctx.send("❌ **ERROR DE PROTOCOLO:** Tenés que mencionar a alguien y dar un motivo. \nEjemplo: `!reportar @Usuario Intento de motín`.")
        return

    if sospechoso.id == ctx.guild.owner_id:
        await ctx.send("❌ **ALERTA DE SEDICIÓN:** ¿Intentando denunciar a Xene? El Presidente es intocable.")
        return

    roles_inmunes = ["『 Presidente 』", "Ministerio de la Verdad", "Jefe de Gabinete", "『 Senadores 』"]
    es_inmune = sospechoso == bot.user or any(rol.name in roles_inmunes for rol in sospechoso.roles)

    if es_inmune:
        await ctx.send("❌ **ALERTA DE SEDICIÓN:** El individuo posee fueros y no puede ser reportado. Cuidado con a quién acusás, ciudadano.")
        return

    if sospechoso == ctx.author:
        await ctx.send("❌ **ERROR:** No podés reportarte a vos mismo. Circule.")
        return

    roles_autorizados = ["『 Presidente 』", "Ministerio de la Verdad", "Ministerio de Seguridad", "Jefe de Gabinete", "『 Senadores 』"]
    tiene_permiso = ctx.author.id == ctx.guild.owner_id or any(rol.name in roles_autorizados for rol in ctx.author.roles)
    
    if not tiene_permiso:
        await ctx.send("❌ **ACCESO DENEGADO:** No tenés la jerarquía para levantar actas. Desista o será reportado.")
        return

    canal_mods = bot.get_channel(1394422101129167039)
    
    try:
        sospechoso_id = str(sospechoso.id)
        ref = db.reference(f'/conteo_reportes/{sospechoso_id}')
        
        cantidad_actual = ref.get()
        if cantidad_actual is None:
            cantidad_actual = 0
            
        nueva_cantidad = cantidad_actual + 1

        if canal_mods:
            if nueva_cantidad >= 3:
                try:
                    await sospechoso.send("🛑 **NOTIFICACIÓN DEL MINISTERIO:** Has acumulado demasiadas denuncias ciudadanas. El Estado ha decidido deportarte temporalmente (Kick).")
                except:
                    pass 
                    
                await sospechoso.kick(reason=f"Acumulación de 3 reportes. Último motivo: {motivo}")
                await canal_mods.send(f"🚨 **¡DEPORTACIÓN AUTOMÁTICA!** 🚨\nEl individuo {sospechoso.mention} acumuló 3 reportes y fue expulsado (Kick) de la red.\n**Último denunciante:** {ctx.author.mention}\n**Último motivo:** {motivo}")
                await ctx.send(f"✅ Recibido, {ctx.author.mention}. El sospechoso superó el límite de faltas y acaba de ser deportado.")
                
                ref.delete()
            else:
                ref.set(nueva_cantidad)
                mensaje_alerta = (
                    f"🚨 **REPORTE DE DISIDENCIA RECIBIDO** 🚨\n"
                    f"El Ministerio de la Obediencia ha sido notificado. (Advertencia {nueva_cantidad}/3)\n"
                    f"**Denunciante:** {ctx.author.mention}\n"
                    f"**Sospechoso:** {sospechoso.mention}\n"
                    f"**Motivo:** {motivo}\n\n"
                    f"*La Libertad agradece tu cooperación...*"
                )
                await canal_mods.send(mensaje_alerta)
                await ctx.send(f"✅ Recibido, {ctx.author.mention}. La infracción (Falta {nueva_cantidad}/3) fue sumada al expediente del ciudadano.")
        else:
            await ctx.send("❌ **ERROR DE SISTEMA:** No encuentro el canal de moderación.")

    except Exception as e:
        await ctx.send(f"⚠️ **Falla crítica en el Archivo General (Firebase):** {e}")
@bot.command()
async def aislar(ctx, alborotador: discord.Member = None, *, motivo="Alteración del orden público"):
    roles_autorizados = ["『 Presidente 』", "Ministerio de Seguridad", "Jefe de Gabinete"]
    tiene_permiso = ctx.author.id == ctx.guild.owner_id or any(rol.name in roles_autorizados for rol in ctx.author.roles)
    
    if not tiene_permiso:
        await ctx.send("❌ **ACCESO DENEGADO:** No tenés la chapa necesaria para aplicar esta medida cautelar.")
        return

    if alborotador is None:
        await ctx.send("❌ **ERROR:** Tenés que mencionar al instigador. \nEjemplo: `!aislar @Usuario Intento de piquete`.")
        return

    roles_inmunes = ["『 Presidente 』", "Jefe de Gabinete", "『 Senadores 』", "Ministerio de la Verdad"]
    es_inmune = alborotador.id == ctx.guild.owner_id or alborotador == bot.user or any(rol.name in roles_inmunes for rol in alborotador.roles)

    if es_inmune:
        await ctx.send("❌ **ERROR:** El ciudadano posee fueros. No podés mandarlo al calabozo.")
        return

    try:
        tiempo_aislamiento = datetime.timedelta(hours=1)
        await alborotador.timeout(tiempo_aislamiento, reason=motivo)
        
        await ctx.send(f"🔒 **CALABOZO ACTIVO:** El ciudadano {alborotador.mention} fue aislado de la sociedad por 1 hora. \n**Motivo:** {motivo}\nQue reflexione sobre su traición al Estado.")
    except Exception as e:
        await ctx.send(f"⚠️ **Error burocrático:** {e}")
@bot.command()
async def indulto(ctx, ciudadano: discord.Member = None):
    roles_autorizados = ["『 Presidente 』", "Jefe de Gabinete"] 
    tiene_permiso = ctx.author.id == ctx.guild.owner_id or any(rol.name in roles_autorizados for rol in ctx.author.roles)
    
    if not tiene_permiso:
        await ctx.send("❌ **ACCESO DENEGADO:** Solo el Poder Ejecutivo puede otorgar indultos.")
        return

    if ciudadano is None:
        await ctx.send("❌ **ERROR:** Tenés que mencionar al ciudadano a indultar. \nEjemplo: `!indulto @Usuario`")
        return

    ciudadano_id = str(ciudadano.id)
    ref = db.reference(f'/conteo_reportes/{ciudadano_id}')
    
    if ref.get() is None:
        await ctx.send(f"📝 El ciudadano {ciudadano.mention} tiene su legajo intachable. No hay faltas que perdonar.")
    else:
        ref.delete()
        await ctx.send(f"🕊️ **INDULTO OTORGADO:** El historial de faltas de {ciudadano.mention} ha sido eliminado. Volvió a ser un ciudadano libre de culpas.")
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if len(message.mentions) > 5:
        await message.delete()
        try:
            await message.author.kick(reason="Protocolo Anti-Nuke: Spam masivo de menciones")
            canal_seguridad = bot.get_channel(1394371063865147424)
            if canal_seguridad:
                await canal_seguridad.send(f"🚨 **DEFENSA ACTIVADA:** El usuario {message.author.name} intentó un ping masivo. Fue ejecutado en el acto.")
        except Exception as e:
            print(f"Error burocrático al expulsar: {e}")
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
            "Agarrá la pala.",
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
        "Anotado en mi máquina de escribir invisible. Siga circulando."]

    if canal_mods:
        await canal_mods.send(f"📩 **NUEVA QUEJA:**\n**Usuario:** {ctx.author.mention}\n**Asunto:** {texto}")
        await ctx.send(f"📋 {random.choice(respuestas_burocraticas)}")

@bot.event
async def on_ready():
    print(f'Inspectora en línea. Logueada como {bot.user}')
    try:
        mi_servidor = discord.Object(id=1394371062111666182) 
        bot.tree.copy_global_to(guild=mi_servidor)
        sincronizados = await bot.tree.sync(guild=mi_servidor)
        print(f"✅ ¡Éxito! Se sincronizaron {len(sincronizados)} comandos en el servidor local.")
    except Exception as e:


@bot.tree.command(name="presente", description="Fichá tu lealtad diaria al Estado. Tenés 32hs de margen antes de perder la racha.")
async def presente(interaction: discord.Interaction):
    usuario_id = str(interaction.user.id)
    ref = db.reference(f'/fichadas_lealtad/{usuario_id}')
    
    datos = ref.get()
    
    zona_arg = datetime.timezone(datetime.timedelta(hours=-3))
    ahora = datetime.datetime.now(zona_arg)
    fecha_hoy = ahora.date()
    
    nueva_cantidad = 1
    mensaje_extra = ""
    
    if datos is not None:
        if isinstance(datos, int):
            cantidad_actual = datos
            nueva_cantidad = cantidad_actual + 1
        else:
            ultima_vez_str = datos.get("ultima_vez")
            cantidad_actual = datos.get("cantidad", 0)
            
            if ultima_vez_str:
                ultima_vez = datetime.datetime.fromisoformat(ultima_vez_str)
                fecha_ultima = ultima_vez.date()
                
                diferencia_horas = (ahora - ultima_vez).total_seconds() / 3600
                
                if fecha_hoy == fecha_ultima:
                    # Ephemeral hace que el mensaje sea "invisible" para el resto
                    await interaction.response.send_message("⏳ **CALMATE, CIUDADANO:** Ya demostraste tu lealtad hoy. Volvé mañana.", ephemeral=True)
                    return
                elif diferencia_horas <= 32:
                    nueva_cantidad = cantidad_actual + 1
                else:
                    nueva_cantidad = 1
                    mensaje_extra = "\n⚠️ **ALERTA DE VAGANCIA:** Pasaron más de 32 horas desde tu última fichada. El Ministerio ha reiniciado tu antigüedad a cero."
            else:
                nueva_cantidad = cantidad_actual + 1

    ref.set({
        "cantidad": nueva_cantidad,
        "ultima_vez": ahora.isoformat()
    })
    
    await interaction.response.send_message(f"🫡 **REGISTRO DE LEALTAD:**\nCiudadano {interaction.user.mention}, esta es su ficha N° {nueva_cantidad}. ¡Su trabajo no será olvidado!{mensaje_extra}")

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



hora_cierre = datetime.time(hour=3, minute=0, tzinfo=datetime.timezone.utc) 
hora_apertura = datetime.time(hour=12, minute=0, tzinfo=datetime.timezone.utc) 

@tasks.loop(time=hora_cierre)
async def toque_de_queda():
    canal = bot.get_channel(1394371063865147424) 
    if canal:
        await canal.send("Me iré a descansar, hice un buen trabajo por hoy...")

@tasks.loop(time=hora_apertura)
async def izar_bandera():
    canal = bot.get_channel(1394371063865147424) 
    if canal:
        await canal.send("Mentí, todo este tiempo estuve despierta... Así que lo leí todo")

@bot.event
async def on_ready():
    print(f'¡{bot.user} ha arribado, comenzando inspección constante!')
    
    if not transmision_oficial.is_running():
        transmision_oficial.start()

    if not toque_de_queda.is_running():
        toque_de_queda.start()
        
    if not izar_bandera.is_running():
        izar_bandera.start()
keep_alive()

acciones_seguridad = {}

@bot.event
async def on_guild_channel_delete(channel):
    async for entry in channel.guild.audit_logs(action=discord.AuditLogAction.channel_delete, limit=1):
        if entry.target.id == channel.id:
            atacante = entry.user
            
            if atacante == bot.user or atacante.id == channel.guild.owner_id:
                return

            tiempo_actual = datetime.datetime.now(datetime.timezone.utc)
            
            if atacante.id not in acciones_seguridad:
                acciones_seguridad[atacante.id] = []
                
            acciones_seguridad[atacante.id].append(tiempo_actual)
            
            acciones_recientes = [t for t in acciones_seguridad[atacante.id] if (tiempo_actual - t).total_seconds() < 10]
            acciones_seguridad[atacante.id] = acciones_recientes
            
            if len(acciones_recientes) >= 2:
                try:
                    await atacante.ban(reason="Protocolo Anti-Nuke: Destrucción de infraestructura del Servidor")
                    canal_alertas = bot.get_channel(1394371063865147424)
                    if canal_alertas:
                        await canal_alertas.send(f"🚨 **¡INTRUSIÓN NEUTRALIZADA!** El individuo {atacante.mention} intentó desmantelar el servidor y fue ejecutado en el acto.")
                except Exception as e:
                    print(f"Error burocrático al detener nuke: {e}")
registro_creacion_canales = {}

@bot.event
async def on_guild_channel_create(channel):
    async for entry in channel.guild.audit_logs(action=discord.AuditLogAction.channel_create, limit=1):
        if entry.target.id == channel.id:
            atacante = entry.user
            if atacante == bot.user or atacante.id == channel.guild.owner_id:
                return
            tiempo_actual = datetime.datetime.now(datetime.timezone.utc)
            if atacante.id not in registro_creacion_canales:
                registro_creacion_canales[atacante.id] = []           
            registro_creacion_canales[atacante.id].append(tiempo_actual)        
            creaciones_recientes = [t for t in registro_creacion_canales[atacante.id] if (tiempo_actual - t).total_seconds() < 15]
            registro_creacion_canales[atacante.id] = creaciones_recientes
            if len(acciones_recientes) >= 2:
                try:
                    try:
                        await atacante.send("Has sido ejecutado en el acto por intento de sabotaje a la infraestructura del servidor. Tu traición no será olvidada. Hasta nunca, idiota.")
                    except:
                        pass 
                    await atacante.ban(reason="Protocolo Anti-Nuke: Destrucción de infraestructura del Servidor")
                    canal_alertas = bot.get_channel(1394371063865147424)
                    if canal_alertas:
                        await canal_alertas.send(f"🚨 **¡INTRUSIÓN NEUTRALIZADA!** El individuo {atacante.mention} intentó desmantelar el servidor y fue ejecutado en el acto.")
                except Exception as e:
                    print(f"Error burocrático al detener nuke: {e}")
            

token_secreto = os.getenv('DISCORD_TOKEN')
bot.run(token_secreto)
