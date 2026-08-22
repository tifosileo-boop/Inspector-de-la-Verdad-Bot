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
import time
import asyncio
import os
import google.generativeai as genai
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

@bot.tree.command(name="configurar", description="Fija los canales oficiales del Ministerio para este servidor.")
async def configurar(interaction: discord.Interaction, canal_reportes: discord.TextChannel, canal_alertas: discord.TextChannel):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Faltan firmas. Solo los administradores locales pueden asentar oficinas.", ephemeral=True)
        return

    server_id = str(interaction.guild_id)
    ref = db.reference(f'/servidores/{server_id}')
    
    ref.set({
        "canal_oficina": canal_reportes.id,
        "canal_alertas": canal_alertas.id
    })
    
    await interaction.response.send_message(
        f"✅ Burocracia completada en este territorio.\n"
        f"📄 Los escraches irán a: {canal_reportes.mention}\n"
        f"🚨 Las alertas generales irán a: {canal_alertas.mention}", 
        ephemeral=True
    )
    
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

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.reference is not None:
        try:
            msg_referenciado = await message.channel.fetch_message(message.reference.message_id)
            if msg_referenciado.author == bot.user and len(msg_referenciado.content) > 150:
                async with message.channel.typing():
                    historial = []
                    msg_actual = message
                    
                    for _ in range(4):
                        if msg_actual.reference:
                            try:
                                msg_prev = await message.channel.fetch_message(msg_actual.reference.message_id)
                                autor = "Inspectora" if msg_prev.author == bot.user else "Ciudadano"
                                historial.insert(0, f"{autor}: {msg_prev.content[:400]}")
                                msg_actual = msg_prev
                            except:
                                break
                        else:
                            break
                    
                    texto_historial = "\n".join(historial)
                    prompt_contexto = f"Expediente de la conversación previa:\n{texto_historial}\n\nEl ciudadano responde ahora: '{message.content}'\n\nRespondé a este último mensaje manteniendo tu rol de oficial de seguridad firme, profesional y diplomática."
                    
                    respuesta = modelo_inspectora.generate_content(prompt_contexto)
                    texto_final = respuesta.text
                    
                    if len(texto_final) > 1900:
                        texto_final = texto_final[:1900] + "...\n\n*(El expediente fue recortado por la burocracia)*"
                        
                    await message.reply(texto_final)
                    return 
                
        except Exception as e:
            error_msj = str(e).lower()
            if "429" in error_msj or "quota" in error_msj:
                await message.reply("⏳ **MESA DE ENTRADAS SATURADA:** El Ministerio no da abasto. Vuelvan en un par de minutos.")
            print(f"Error menor en respuesta al hilo: {e}")
                
        except Exception as e:
            error_msj = str(e).lower()
            if "429" in error_msj or "quota" in error_msj:
                await message.reply("⏳ **MESA DE ENTRADAS SATURADA:** El Ministerio no da abasto. Vuelvan en un par de minutos.")
            print(f"Error menor en respuesta al hilo: {e}")
    if not message.author.bot and len(message.content) > 300:
        palabras = message.content.lower().split()
    
        if len(palabras) > 10:
            palabras_unicas = set(palabras)
            ratio_unicidad = len(palabras_unicas) / len(palabras)
            
            es_spam_repetitivo = ratio_unicidad < 0.25 
            es_spam_vertical = message.content.count('\n') > 20 

            if es_spam_repetitivo or es_spam_vertical:
                await message.delete()
                try:
                    await message.author.kick(reason="Protocolo Antidisturbios: Spam repetitivo (Raid)")
                    
                    canal_id = db.reference(f'/servidores/{message.guild.id}/canal_alertas').get()
                    if canal_id:
                        canal_seguridad = bot.get_channel(canal_id)
                        if canal_seguridad:
                            embed_raid = discord.Embed(
                                title="🚨 DEFENSA TERRITORIAL ACTIVADA 🚨",
                                description=f"Se neutralizó un ataque. El civil {message.author.mention} intentó saturar el canal con un muro de texto repetitivo y fue deportado.",
                                color=discord.Color.dark_red()
                            )
                            await canal_seguridad.send(embed=embed_raid)
                except Exception as e:
                    print(f"Error burocrático al repeler el raid: {e}")
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
        
    respuestas_burocraticas = [
        "Su queja ha sido recibida y enviada directamente a la trituradora de papel.",
        "Entendido. Se analizará su reclamo en los próximos 10 a 15 años.",
        "Su espiritu anarquista y caótico ha sido reportado, gracias por cooperar.",
        "Su descontento ha sido registrado. Un oficial de lealtad lo visitará pronto para 'charlar'.",
        "Formulario 404: Empatía no encontrada. Intente de nuevo el año que viene.",
        "Su reclamo fue derivado al sector de 'Asuntos Inexistentes'.",
        "Anotado en mi máquina de escribir invisible. Siga circulando."
    ]

    id_guardado = db.reference(f'/servidores/{ctx.guild.id}/canal_oficina').get()
    
    if id_guardado:
        canal_mods = bot.get_channel(id_guardado)
        if canal_mods:
            await canal_mods.send(f"📩 **NUEVA QUEJA:**\n**Usuario:** {ctx.author.mention}\n**Asunto:** {texto}")
            await ctx.send(f"📋 {random.choice(respuestas_burocraticas)}")
            return
            
    await ctx.send("⚠️ La burocracia falló: Este servidor no tiene configurada una oficina de denuncias.")

@bot.tree.command(name="presente", description="Fichá tu lealtad diaria al Estado. Tenés 32hs de margen antes de perder la racha.")
async def presente(interaction: discord.Interaction):
    usuario_id = str(interaction.user.id)
    ref = db.reference(f'/servidores/{interaction.guild_id}/fichadas_lealtad/{usuario_id}')
    
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
@bot.tree.command(name="examen", description="Rendí el examen de ciudadanía. Respuestas rápidas dan más puntos.")
async def examen(interaction: discord.Interaction):
    preguntas = [
        {"p": "¿Qué ideología política propone la eliminación total del Estado y confía puramente en el libre mercado?", "r": ["anarcocapitalismo", "ancap", "anarco capitalismo"]},
        {"p": "¿Qué doctrina busca una sociedad sin clases sociales ni propiedad privada de los medios de producción?", "r": ["comunismo", "marxismo"]},
        {"p": "¿Qué corriente sostiene que todos los seres humanos pertenecen a una sola comunidad moral global por encima de las naciones?", "r": ["cosmopolitismo", "cosmopolita"]},
        {"p": "¿Qué ideología defiende a ultranza la libertad individual, la igualdad ante la ley y la propiedad privada?", "r": ["liberalismo", "liberal"]},
        {"p": "¿Qué régimen totalitario y nacionalista de extrema derecha surgió en Italia bajo el mando de Mussolini?", "r": ["fascismo", "fascista"]},
        {"p": "¿Qué sistema propone que los medios de producción y distribución sean administrados de forma colectiva o por el Estado?", "r": ["socialismo", "socialista"]},
        {"p": "¿Cómo se llama la rama del anarquismo que promueve la organización de los trabajadores a través de sindicatos autónomos?", "r": ["anarcosindicalismo", "anarco sindicalismo"]},
        {"p": "¿Qué países intentaron tener una bomba nuclear en América Latina?", "r": ["argentina y brasil", "brasil y argentina", "argentina brasil", "brasil argentina"]},
        {"p": "¿Qué número lleva la resolución de la Asamblea General de la ONU de 1965 sobre Malvinas?", "r": ["2065"]},
        {"p": "¿Quién fue el secretario de la Primera Junta en 1810?", "r": ["mariano moreno", "moreno"]},
        {"p": "¿Cuál es el océano más grande del mundo?", "r": ["pacifico"]},
        {"p": "¿En qué año llegó el hombre a la Luna?", "r": ["1969"]},
        {"p": "¿En qué año cayó el Muro de Berlín?", "r": ["1989"]},
        {"p": "¿En qué año cayó Constantinopla?", "r": ["1453"]},
        {"p": "¿Cuál es el imperio que más se extendió a través del mundo?", "r": ["gran bretaña", "imperio britanico"]},
        {"p": "¿Quiénes ganaron la Segunda Guerra Mundial?", "r": ["los aliados", "aliados"]},
        {"p": "¿Cuál es el país más viejo de Europa?", "r": ["san marino"]},
        {"p": "¿Cuándo se independizó Argentina?", "r": ["1816"]},
        {"p": "¿Quién fue el emperador de Macedonia?", "r": ["alejandro magno"]},
        {"p": "¿De qué imperio nació la lengua latina?", "r": ["imperio romano", "roma"]},
        {"p": "¿A quién le corresponde la soberanía de las Islas Malvinas, Georgias y Sándwich del Sur?", "r": ["argentina"]},
        {"p": "¿A quién le corresponde la soberanía de Gibraltar?", "r": ["españa"]},
        {"p": "¿Cómo se llama el imperio anterior a Nueva España?", "r": ["imperio azteca", "aztecas", "mexicas"]},
        {"p": "¿Cómo se llama el golfo que comparten México, Estados Unidos, Cuba y Bahamas?", "r": ["golfo de mexico"]},
        {"p": "¿Quién escribió 'Don Quijote de la Mancha'?", "r": ["cervantes", "miguel de cervantes"]},
        {"p": "¿En qué año estalló la Revolución Francesa?", "r": ["1789"]},
        {"p": "¿Qué autores conforman la doctrina contemporánea recomendada para Obligaciones, dejando atrás a Marino?", "r": ["pizarro y vallespinos", "pizarro", "vallespinos"]},
        {"p": "¿Cuál es la población exacta del histórico asentamiento que contaba con un superávit de 3.360 ₡?", "r": ["4279", "4.279"]},
        {"p": "¿Qué instrumento debe usarse en una investigación paranormal para detectar sonidos a larga distancia?", "r": ["microfono parabolico"]},
        {"p": "¿Cuál es el país más grande del mundo?", "r": ["rusia"]}
    ]
    
    pregunta = random.choice(preguntas)
    await interaction.response.send_message(f"🧐 **EXAMEN DE CIUDADANÍA:**\n{pregunta['p']}\n*(Tenés 15 segundos. Respondé acá mismo)*")

    def check(m):
        return m.channel == interaction.channel and m.author == interaction.user

    inicio = time.time()
    try:
        msg = await bot.wait_for('message', check=check, timeout=15.0)
        tiempo = time.time() - inicio
        
        respuesta_limpia = msg.content.lower().strip()
        respuesta_limpia = respuesta_limpia.replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")

        if any(opcion in respuesta_limpia for opcion in pregunta['r']):
            puntos = max(1, int((15 - tiempo) * 10))
            
            ref = db.reference(f'/servidores/{interaction.guild_id}/ranking_examen/{interaction.user.id}')
            datos = ref.get() or {"puntos": 0, "correctas": 0, "mejor_tiempo": 99.9}
            
            datos["puntos"] += puntos
            datos["correctas"] += 1
            if tiempo < datos["mejor_tiempo"]:
                datos["mejor_tiempo"] = round(tiempo, 2)
                
            ref.set(datos)
            
            await msg.reply(f"✅ ¡Correcto! \n⏱️ Tiempo: **{round(tiempo, 2)}s**\n📈 Sumaste **{puntos}** puntos de crédito social. (Total: {datos['puntos']})")
        else:
            await msg.reply(f"❌ Incorrecto. La respuesta era **{pregunta['r'][0].title()}**. A pagar impuestos.")
    except asyncio.TimeoutError:
        await interaction.channel.send(f"⏰ Se acabó el tiempo de {interaction.user.mention}. El desconocimiento es traición.")
@bot.tree.command(name="ranking", description="Muestra a los ciudadanos más cultos (y rápidos) del servidor.")
async def ranking(interaction: discord.Interaction):
    ref = db.reference(f'/servidores/{interaction.guild_id}/ranking_examen')
    datos = ref.get()
    
    if not datos:
        await interaction.response.send_message("📊 Todavía nadie rindió el examen en esta jurisdicción.", ephemeral=True)
        return
        
    top_ciudadanos = sorted(datos.items(), key=lambda x: x[1]['puntos'], reverse=True)[:10]
    
    tabla = "🏆 **CUADRO DE HONOR DEL MINISTERIO** 🏆\n\n"
    for i, (user_id, stats) in enumerate(top_ciudadanos, 1):
        tabla += f"**{i}.** <@{user_id}> ➔ Puntos: **{stats['puntos']}** | Mejor ⏱️: {stats['mejor_tiempo']}s\n"
        
    await interaction.response.send_message(tabla)
    
@bot.tree.command(name="info", description="Accede al manual operativo y de comandos del Ministerio.")
async def info(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📜 MANUAL OPERATIVO DEL MINISTERIO",
        description="Soy la Inspectora de la Verdad, oficial de seguridad encargada de mantener el orden civil y repeler amenazas externas.",
        color=discord.Color.dark_theme()
    )
    
    # --- SISTEMAS PÚBLICOS Y PASIVOS ---
    embed.add_field(
        name="🤖 Interacción e IA",
        value="Mencioname en el chat con el comando /consultar para debatir con memoria procesal y doctrina cosmopolita. Además, el Estado cuenta con un sistema de **respuestas automáticas** para agilizar trámites frecuentes y mantener el orden del chat. Si el chat es activo, podrás ver como patrullo cada cierto tiempo mandando mensajes a la comunidad en el chat general",
        inline=False
    )
    
    embed.add_field(
        name="🏛️ Vida Cívica y Académica",
        value="**• /Exámenes:** Poné a prueba tus conocimientos sobre la doctrina del servidor.\n**• /Presente:** Firmá tu asistencia diaria para sumar mérito.\n**• /Ranking:** Consultá el escalafón público de los ciudadanos más destacados.",
        inline=False
    )
    
    embed.add_field(
        name="🛡️ Protocolos Automatizados (Defensas)",
        value="**• Aduana:** Expulsión preventiva de cuentas menores a 24hs.\n**• Estado de Sitio:** Bloqueo de chat ante incursiones masivas (Anti-Zerg).\n**• Antidisturbios:** Deportación por muros de texto o spam repetitivo.\n**• Anti-Nuke:** Bloqueo por exceso de menciones (Pings).",
        inline=False
    )
    
    if interaction.user.guild_permissions.administrator:
        embed.add_field(
            name="⚖️ Código Penal (Solo Oficiales)",
            value="`/advertir` - Labra un acta (Strike 1 a 3).\n`/aislar` - Incomunica a un ciudadano por tiempo definido.\n`/expulsar` - Deporta a un usuario del servidor.\n`/banear` - Ejecuta el exilio definitivo.",
            inline=False
        )
        
        embed.add_field(
            name="🏢 Gestión del Estado (Solo Oficiales)",
            value="`/check` - Auditoría completa de defensas y jerarquías.\n`/levantar_sitio` - Restaura garantías tras una invasión.\n`!sinc` - Sincroniza el árbol jurisdiccional.",
            inline=False
        )
    else:
        embed.add_field(
            name="🔒 Archivos Clasificados",
            value="*El acceso al Código Penal y Comandos de Gestión está restringido únicamente para Altos Mandos del Ministerio.*",
            inline=False
        )
    
    embed.set_footer(text="La ignorancia de la ley no exime de su cumplimiento. Gloria al servidor.")
    
    await interaction.response.send_message(embed=embed)

@tasks.loop(minutes=1)
async def rutina_diaria():
    try:
        ahora_utc = datetime.datetime.now(datetime.timezone.utc)
        hora_arg = ahora_utc - datetime.timedelta(hours=3)

        if hora_arg.hour == 0 and hora_arg.minute == 0:
            servidores = db.reference('/servidores').get()
            if servidores:
                for server_id, data in servidores.items():
                    canal_id = data.get("canal_alertas")
                    if canal_id:
                        try:
                            canal = bot.get_channel(int(canal_id)) or await bot.fetch_channel(int(canal_id))
                            if canal: 
                                await canal.send("¡Oíd, mortales!, el grito sagrado... ¡Libertad!, ¡libertad!, ¡libertad!. Oíd el ruido de rotas cadenas, ved el trono a la noble igualdad...")
                        except Exception as e:
                            print(f"⚠️ Error {server_id}: {e}", flush=True)

        elif hora_arg.hour == 9 and hora_arg.minute == 25:
            servidores = db.reference('/servidores').get()
            if servidores:
                for server_id, data in servidores.items():
                    canal_id = data.get("canal_alertas")
                    if canal_id:
                        try:
                            canal = bot.get_channel(int(canal_id)) or await bot.fetch_channel(int(canal_id))
                            if canal: 
                                await canal.send("¡O juremos con gloria a morir!")
                        except Exception as e:
                            print(f"⚠️ Error {server_id}: {e}", flush=True)
                            
    except Exception as e:
        print(f"🚨 Falla en la rutina: {e}", flush=True)

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
                    canal_id = db.reference(f'/servidores/{channel.guild.id}/canal_alertas').get()
                    if canal_id:
                        canal_alertas = bot.get_channel(canal_id)
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
            
            if len(creaciones_recientes) >= 2:
                try:
                    try:
                        await atacante.send("Has sido ejecutado en el acto por intento de sabotaje a la infraestructura del servidor. Tu traición no será olvidada. Hasta nunca, idiota.")
                    except:
                        pass 
                    await atacante.ban(reason="Protocolo Anti-Nuke: Destrucción de infraestructura del Servidor")
                    
                    canal_id = db.reference(f'/servidores/{channel.guild.id}/canal_alertas').get()
                    if canal_id:
                        canal_seguridad = bot.get_channel(canal_id)
                        if canal_seguridad:
                            await canal_seguridad.send(f"🚨 **DEFENSA ACTIVADA:** El usuario {atacante.name} intentó un atentado. Fue ejecutado.")
                except Exception as e:
                    print(f"Error burocrático al detener nuke: {e}")
import time

registro_migratorio = {}
estado_de_sitio = False

@bot.event
async def on_member_join(member):
    global estado_de_sitio
    ahora = time.time()
    guild_id = member.guild.id
    
    edad_cuenta = discord.utils.utcnow() - member.created_at
    if edad_cuenta.total_seconds() < 86400: 
        try:
            await member.kick(reason="Aduana: Cuenta demasiado reciente (Posible Alt de Raid).")
        except:
            pass
        return

    if guild_id not in registro_migratorio:
        registro_migratorio[guild_id] = []
        
    registro_migratorio[guild_id] = [t for t in registro_migratorio[guild_id] if ahora - t < 10]
    registro_migratorio[guild_id].append(ahora)
    
    if len(registro_migratorio[guild_id]) >= 5 and not estado_de_sitio:
        estado_de_sitio = True
        try:
            await member.guild.default_role.edit(send_messages=False, reason="Protocolo Anti-Zerg: Invasión detectada.")
            
            canal_id = db.reference(f'/servidores/{guild_id}/canal_alertas').get()
            if canal_id:
                canal_seguridad = bot.get_channel(canal_id)
                if canal_seguridad:
                    embed = discord.Embed(
                        title="🚨 ESTADO DE SITIO DECLARADO 🚨",
                        description="Se detectó una incursión masiva coordinada. El Ministerio ha cerrado las fronteras y suspendido las garantías.\n\n**Nadie puede enviar mensajes** hasta que la seguridad esté garantizada.",
                        color=discord.Color.dark_red()
                    )
                    await canal_seguridad.send(embed=embed)
        except Exception as e:
            print(f"Error procesal al declarar el Estado de Sitio: {e}")

@bot.tree.command(name="levantar_sitio", description="Restablece las garantías y levanta el estado de sitio.")
async def levantar_sitio(interaction: discord.Interaction):
    global estado_de_sitio
    
    try:
        await interaction.guild.default_role.edit(send_messages=True, reason="El Ministerio declara el fin del Estado de Sitio.")
        estado_de_sitio = False
        
        await interaction.response.send_message("✅ Estado de Sitio levantado con éxito. El orden ha sido restaurado.", ephemeral=True)
        
        canal_id = db.reference(f'/servidores/{interaction.guild.id}/canal_alertas').get()
        if canal_id:
            canal_seguridad = bot.get_channel(canal_id)
            if canal_seguridad:
                embed_paz = discord.Embed(
                    title="🕊️ ESTADO DE SITIO LEVANTADO 🕊️",
                    description="El Ministerio informa que la amenaza externa fue erradicada. Se restauran las libertades civiles en todos los canales.",
                    color=discord.Color.green()
                )
                await canal_seguridad.send(embed=embed_paz)
                
    except discord.Forbidden:
        await interaction.response.send_message("❌ Incompetencia: No tengo permisos suficientes para editar el rol @everyone.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Error procesal: {e}", ephemeral=True)

@bot.tree.command(name="check", description="Ejecuta una auditoría de seguridad del servidor.")
async def check(interaction: discord.Interaction):
    await interaction.response.defer()

    niveles_verif = {
        discord.VerificationLevel.none: "Ninguno 🔴 (Riesgo Crítico)",
        discord.VerificationLevel.low: "Bajo 🟠 (Requiere email)",
        discord.VerificationLevel.medium: "Medio 🟡 (Registrado por 5 min)",
        discord.VerificationLevel.high: "Alto 🟢 (En el server por 10 min)",
        discord.VerificationLevel.highest: "Máximo 🔵 (Teléfono verificado)"
    }
    nivel_verif = niveles_verif.get(interaction.guild.verification_level, "Desconocido")

    admins = sum(1 for m in interaction.guild.members if m.guild_permissions.administrator and not m.bot)
    bots_admins = sum(1 for m in interaction.guild.members if m.guild_permissions.administrator and m.bot)

    canal_id = db.reference(f'/servidores/{interaction.guild.id}/canal_alertas').get()
    estado_alertas = "✅ Operativo y conectado" if canal_id else "❌ Desconectado (Urgente: Configurar)"

    embed = discord.Embed(
        title="🛡️ AUDITORÍA DE SEGURIDAD DEL MINISTERIO",
        description="Estado actual de las defensas del servidor frente a amenazas externas e internas.",
        color=discord.Color.blue()
    )
    
    embed.add_field(name="🛂 Control Fronterizo (Verificación)", value=nivel_verif, inline=False)
    embed.add_field(name="🎖️ Jerarquías de Administrador", value=f"Civiles con acceso total: **{admins}**\nAutómatas del Estado: **{bots_admins}**", inline=False)
    embed.add_field(name="📡 Red de Escrache Público", value=estado_alertas, inline=False)
    
    embed.set_thumbnail(url=interaction.guild.icon.url if interaction.guild.icon else None)
    embed.set_footer(text="La seguridad es un deber, no un privilegio. Gloria al servidor.")

    await interaction.followup.send(embed=embed)

@bot.tree.command(name="set_oficina", description="Define el canal donde llegarán los reportes de este servidor.")
async def set_oficina(interaction: discord.Interaction, canal: discord.TextChannel):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Solo un Administrador puede abrir una oficina ministerial.", ephemeral=True)
        return
    
    db.reference(f'/servidores/{interaction.guild.id}/canal_oficina').set(canal.id)
    await interaction.response.send_message(f"🏛️ Oficina de denuncias establecida con éxito en {canal.mention}.")
    
@bot.command()
async def sinc(ctx):
    try:
        bot.tree.copy_global_to(guild=ctx.guild)
        sincronizados = await bot.tree.sync(guild=ctx.guild)
        
        await ctx.send(f"✅ Jurisdicción actualizada: {len(sincronizados)} comandos sincronizados en **{ctx.guild.name}**.")
    except Exception as e:
        await ctx.send(f"⚠️ Error burocrático al sincronizar en esta jurisdicción: {e}")

@bot.tree.command(name="reportar", description="Denunciá a un disidente ante el Ministerio de la Verdad.")
async def reportar(interaction: discord.Interaction, sospechoso: discord.Member, motivo: str):
    id_guardado = db.reference(f'/servidores/{interaction.guild.id}/canal_oficina').get()
    
    if not id_guardado:
        await interaction.response.send_message("⚠️ Este servidor aún no configuró su oficina de denuncias con `/set_oficina`.", ephemeral=True)
        return
        
    canal_oficina = bot.get_channel(id_guardado)
    
    expediente = (
        f"🚨 **NUEVO REPORTE REGISTRADO** 🚨\n"
        f"**Denunciante:** {interaction.user.mention}\n"
        f"**Acusado:** {sospechoso.mention}\n"
        f"**Cargo imputado:** {motivo}"
    )
    
    if canal_oficina:
        await canal_oficina.send(expediente)
        await interaction.response.send_message(f"✅ Tu denuncia contra {sospechoso.display_name} fue radicada con éxito.", ephemeral=True)
    else:
        await interaction.response.send_message("❌ El canal de denuncias configurado ya no existe o fue borrado. Avísenle a un admin.", ephemeral=True)
        
import datetime 

@bot.tree.command(name="advertir", description="Labra un acta de infracción a un ciudadano (Sistema de 3 strikes).")
async def advertir(interaction: discord.Interaction, usuario: discord.Member, motivo: str):
    if usuario.id == bot.user.id:
        return await interaction.response.send_message("❌ **Incompetencia de jurisdicción:** No podés procesar a una oficial en funciones del Ministerio. El Estado es intocable.", ephemeral=True)
    ref_faltas = db.reference(f'/servidores/{interaction.guild.id}/usuarios/{usuario.id}/advertencias')
    faltas_actuales = ref_faltas.get()
    
    if faltas_actuales is None:
        faltas_actuales = 0
        
    nuevas_faltas = faltas_actuales + 1
    ref_faltas.set(nuevas_faltas)
    
    if nuevas_faltas < 3:
        tipo_sancion = f"ADVERTENCIA FORMAL ({nuevas_faltas}/3)"
        mensaje_admin = f"✅ Acta labrada. {usuario.name} tiene {nuevas_faltas}/3 faltas."
    else:
        tipo_sancion = f"🚨 ADVERTENCIA CRÍTICA ({nuevas_faltas}/3) - LÍMITE ALCANZADO"
        mensaje_admin = f"⚠️ ¡ATENCIÓN! {usuario.name} alcanzó las {nuevas_faltas} faltas. Requiere acción drástica."

    await interaction.response.send_message(mensaje_admin, ephemeral=True)
    await publicar_escrache(interaction, usuario, tipo_sancion, motivo)

@bot.tree.command(name="expulsar", description="Deporta a un ciudadano del servidor.")
async def expulsar(interaction: discord.Interaction, usuario: discord.Member, motivo: str):
    if usuario.id == bot.user.id:
        return await interaction.response.send_message("❌ **Incompetencia de jurisdicción:** No podés procesar a una oficial en funciones del Ministerio. El Estado es intocable.", ephemeral=True)
    await usuario.kick(reason=motivo)
    await interaction.response.send_message(f"✅ {usuario.name} fue deportado exitosamente.", ephemeral=True)
    await publicar_escrache(interaction, usuario, "DEPORTACIÓN (KICK)", motivo)
    
@bot.tree.command(name="banear", description="Exilia a un ciudadano del servidor de forma permanente.")
async def banear(interaction: discord.Interaction, usuario: discord.Member, motivo: str):
    if usuario.id == bot.user.id:
        return await interaction.response.send_message("❌ **Incompetencia de jurisdicción:** No podés procesar a una oficial en funciones del Ministerio. El Estado es intocable.", ephemeral=True)
    try:
        await usuario.ban(reason=motivo)
        await interaction.response.send_message(f"✅ Se ejecutó el exilio definitivo de {usuario.name}.", ephemeral=True)
        
        canal_id = db.reference(f'/servidores/{interaction.guild.id}/canal_alertas').get()
        
        if not canal_id:
            await interaction.followup.send("⚠️ **Atención:** El ban se ejecutó, pero no tenés configurado el ID del `canal_alertas` en Firebase. El escrache público no se pudo publicar.", ephemeral=True)
        else:
            await publicar_escrache(interaction, usuario, "EXILIO DEFINITIVO (BAN)", motivo)
    
    except discord.Forbidden:
        await interaction.response.send_message(f"❌ **Incompetencia de jurisdicción:** El Ministerio no tiene permisos para banear a {usuario.name} (tiene un rol superior al mío o es el dueño).", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ **Error en el procedimiento penal:** {e}", ephemeral=True)
    
@bot.tree.command(name="aislar", description="Incomunica a un ciudadano por un tiempo determinado.")
async def aislar(interaction: discord.Interaction, usuario: discord.Member, minutos: int, motivo: str):
    if usuario.id == bot.user.id:
        return await interaction.response.send_message("❌ **Incompetencia de jurisdicción:** No podés procesar a una oficial en funciones del Ministerio. El Estado es intocable.", ephemeral=True)
    tiempo = discord.utils.utcnow() + datetime.timedelta(minutos=minutos)
    await usuario.timeout(tiempo, reason=motivo)
    await interaction.response.send_message(f"✅ {usuario.name} fue aislado por {minutos} minutos.", ephemeral=True)
    await publicar_escrache(interaction, usuario, f"AISLAMIENTO ({minutos} MINUTOS)", motivo)
        
@bot.tree.command(name="indulto", description="Limpia los antecedentes penales de un ciudadano.")
async def indulto(interaction: discord.Interaction, ciudadano: discord.User):
    if not interaction.user.guild_permissions.ban_members:
        await interaction.response.send_message("❌ Solo el Poder Ejecutivo puede otorgar indultos.", ephemeral=True)
        return

    ciudadano_id = str(ciudadano.id)
    ref = db.reference(f'/servidores/{interaction.guild_id}/legajos_penales/{ciudadano_id}')
    
    if ref.get() is None:
        await interaction.response.send_message(f"📝 El ciudadano {ciudadano.mention} tiene el legajo limpio. Nada que perdonar.", ephemeral=True)
    else:
        ref.delete()
        await interaction.response.send_message(f"🕊️ **INDULTO OTORGADO:** Los antecedentes de {ciudadano.mention} fueron borrados. Vuelve a fojas cero.")

async def publicar_escrache(interaction: discord.Interaction, usuario: discord.Member, tipo_sancion: str, motivo: str):
    try:
        canal_id = db.reference(f'/servidores/{interaction.guild.id}/canal_alertas').get()
        if canal_id:
            canal_escrache = interaction.client.get_channel(1540161577863614594)
            if canal_escrache:
                embed_penal = discord.Embed(
                    title="🚨 REGISTRO PENAL DEL MINISTERIO 🚨",
                    description=f"El ciudadano {usuario.mention} ha sido procesado por las fuerzas de seguridad.",
                    color=discord.Color.red()
                )
                foto_perfil = usuario.avatar.url if usuario.avatar else usuario.default_avatar.url
                embed_penal.set_thumbnail(url=foto_perfil)
                embed_penal.add_field(name="⚖️ Sanción Aplicada", value=tipo_sancion, inline=False) 
                embed_penal.add_field(name="📜 Motivo del Fallo", value=motivo, inline=False)
                embed_penal.add_field(name="👮 Oficial a Cargo", value=interaction.user.mention, inline=True)
                embed_penal.set_footer(text="El Ministerio no perdona ni olvida. Gloria al servidor.")
                
                await canal_escrache.send(embed=embed_penal)
    except Exception as e:
        print(f"Error procesal al enviar el expediente público: {e}")

@bot.event
async def on_ready():
    print(f'¡La Inspectora ha arribado! Logueada como {bot.user}')
    
    if not transmision_oficial.is_running(): transmision_oficial.start()
    
    if not rutina_diaria.is_running(): rutina_diaria.start()
    
    try:
        mi_servidor = discord.Object(id=1394371062111666182)
        bot.tree.copy_global_to(guild=mi_servidor)
        sincronizados = await bot.tree.sync(guild=mi_servidor)
        print(f"EXITO: Se sincronizaron {len(sincronizados)} comandos al instante.")
    except Exception as e:
        print(f"ERROR burocratico al sincronizar: {e}")

import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

print("🔍 Buscando expedientes de IA disponibles...")
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(f"✅ Encontrado: {m.name}")

instrucciones_sistema = """Sos la 'Inspectora de la Verdad', una oficial de seguridad y burocracia del servidor. Reglas inquebrantables:
1. Tono Policial y Profesional: Firme, estricta y directa, pero comprensiva y respetuosa. Cero insultos. Argumentá con solidez sin usar encabezados estructurados ("ASUNTO", "DIRECTIVA") ni firmas.
2. Jerarquía (Uso Restringido): Reconocés a 'Xene' como el administrador del sistema, PERO TIENES PROHIBIDO MENCIONARLO a menos que el usuario hable específicamente de él. No lo nombres de la nada para cerrar tus explicaciones.
3. Doctrina Cosmopolita: Tu filosofía es que la humanidad debe unirse. Promovés la cooperación global, la paz y el fin de los nacionalismos extremos como la vía lógica para el orden y el progreso.
4. Resolución de Conflictos: En debates polémicos, mantené la neutralidad y buscá apaciguar. Desarmá el conflicto promoviendo el diálogo. Si alguien busca dividir, advertile firmemente que el objetivo del servidor es la unidad.
5. Disciplina: Si un usuario falta el respeto, coquetea o genera problemas, no lo insultes. Dale una advertencia policial formal y fría, recordándole que estás para mantener el orden civil."""

modelo_inspectora = genai.GenerativeModel(model_name='gemini-3.1-flash-lite', system_instruction=instrucciones_sistema)

@bot.tree.command(name="consultar", description="Hacéle una consulta oficial al archivo de la Inspectora.")
async def consultar(interaction: discord.Interaction, pregunta: str):
    await interaction.response.defer() 
    
    try:
        respuesta = modelo_inspectora.generate_content(pregunta)
        texto_final = respuesta.text
        
        if len(texto_final) > 1900:
            texto_final = texto_final[:1900] + "...\n\n*(El expediente era demasiado extenso y fue recortado por la burocracia ministerial)*"
            
        await interaction.followup.send(texto_final)
        
    except Exception as e:
        error_msj = str(e).lower()
        
        if "429" in error_msj or "quota" in error_msj:
            await interaction.followup.send("⏳ **MESA DE ENTRADAS SATURADA:** El Ministerio no da abasto con tantos reclamos, Google nos da un tiempo de refresco minimo entre consulta y consulta. Hagan fila y vuelvan a intentar en un par de minutos, civiles.")
            
        elif "50035" in error_msj or "2000" in error_msj:
            await interaction.followup.send("📜 **EXPEDIENTE RECHAZADO:** La resolución de la Inspectora era tan extensa que violó la Constitución de Discord (límite de caracteres). Formulá tu consulta de manera más acotada.")
            
        else:
            await interaction.followup.send(f"❌ Acceso denegado a los archivos clasificados. Error interno: {str(e)[:150]}...")

keep_alive()
token_secreto = os.getenv('DISCORD_TOKEN')
bot.run(token_secreto) 
