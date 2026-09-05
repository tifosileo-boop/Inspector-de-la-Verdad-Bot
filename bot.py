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
registro_insistencia = {}
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

async def publicar_escrache(guild, titulo, descripcion, color):
    canal_id = db.reference(f'/servidores/{guild.id}/canal_alertas').get()
    
    if canal_id:
        try:
            canal = guild.get_channel(int(canal_id)) or await guild.fetch_channel(int(canal_id))
            if canal:
                embed = discord.Embed(title=titulo, description=descripcion, color=color)
                await canal.send(embed=embed)
            else:
                print(f"❌ La Inspectora no encuentra el canal con ID {canal_id}. ¿Lo borraron?")
        except discord.Forbidden:
            print("❌ El bot no tiene permisos de 'Ver Canal' o 'Insertar Enlaces' en #penitencia.")
        except Exception as e:
            print(f"❌ Error burocrático al colgar el acta: {e}")

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
            "Recuerda ser demostrar tú actividad con las fichas de lealtad usando /presente todos los días. El !bump también ayuda."
            "El Ministerio recuerda que lavar el mate es considerado un delito federal de traición a la patria.",
            "Formar alianzas dudosas a espaldas del Estado terminará con un bloqueo en tu IP. Nomás digo.",
            "Aquel que exija derechos sin conocer sus obligaciones será condenado a ayudar a Xene a estudiar Derecho Civil a las 7 AM con viento en contra.",
            "Se detectó un aumento en el contrabando de lombrices. Todo tráfico animal no autorizado será severamente castigado.",
            "Las quejas por el frío de la costa se consideran debilidad física. Abríguense bien.",
            "Abusar del chat de voz sin un micrófono decente viola la ley de contaminación acústica. Primer aviso.",
            "Si la burocracia tarda, es porque el sistema funciona. Agradezcan la lentitud del Estado.",
            "Pedir refuerzos y después no cubrir el flanco es causal de exilio inmediato. Defiendan el territorio.",
            "Dorado, dejá de intentar piropearme o cortejarme. En una de estas te voy a advertir y no te voy a indultar.",
            "📺 **Directiva Habitacional de la biblioteca de archivos:** La mala gestión de su zona y la información ineficiente serán penalizadas. Planifiquen bien, o el Estado expropiará sus terrenos.",
            "El Ministerio decreta que jugar Minecraft en modo Hardcore y morir por caída es selección natural.",
            "Cualquier civil que sea encontrado escondido en un armario con un medidor EMF será ejecutado por cobardía.",
            "Si no podés esquivar tus responsabilidades cívicas, al menos aprendé a esquivar los golpes. Comportamiento 'maidenless' no será tolerado en este servidor.",
            "📺 **Alerta Biológica:** El mercado negro de lombrices para mascotas acuáticas está bajo estricta investigación. Mantengan sus peceras dentro del marco legal.",
            "Preparar queque perfecto requiere disciplina, paciencia y precisión. Exactamente lo que el Estado espera de su conducta diaria.",
            "Simular juicios por jurados está bárbaro para practicar, pero recuerden que acá la Inspectora es fiscal, juez y verdugo de turno.",
            "La historia argentina nos enseña que los caudillos rebeldes terminan exiliados. Mantengan el orden y eviten terminar como Quiroga o Rosas.",
            "Si notan que Xene no está moderando, es porque está grabando tiktoks de historia o sufriendo en la facultad. Igual yo no descanso.",
            "No les cuesta nada callear site, el ocultamiento de la posición de los TT será penalizada con ejecución pública.",
        ]
        
        opciones_validas = [frase for frase in frases_ministerio if frase != ultimo_mensaje_propaganda]
        mensaje_sorteado = random.choice(opciones_validas)
        ultimo_mensaje_propaganda = mensaje_sorteado
        
        await canal.send(mensaje_sorteado)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if not message.author.bot and len(message.content) > 300:
        if not message.author.guild_permissions.administrator:
            palabras = message.content.lower().split()
            
            if len(palabras) > 10:
                palabras_unicas = set(palabras)
                ratio_unicidad = len(palabras_unicas) / len(palabras)
                
                es_spam_repetitivo = ratio_unicidad < 0.25
                es_spam_vertical = message.content.count('\n') > 35

                if es_spam_repetitivo or es_spam_vertical:
                    await message.delete()
                    try:
                        await message.author.kick(reason="Protocolo Antidisturbios: Spam repetitivo (Raid)")
                        await publicar_escrache(
                            message.guild,
                            "🚨 DEFENSA TERRITORIAL ACTIVADA",
                            f"Se neutralizó un ataque. El civil {message.author.mention} intentó saturar el canal con un muro de texto repetitivo y fue ejecutado en el acto.",
                            discord.Color.dark_red()
                        )
                    except Exception as e:
                        print(f"Error burocrático al repeler el raid: {e}")
                    return

    es_respuesta_al_bot = False
    if message.reference:
        try:
            msg_ref = await message.channel.fetch_message(message.reference.message_id)
            if msg_ref.author == bot.user:
                es_respuesta_al_bot = True
        except:
            pass

    if es_respuesta_al_bot:
        if msg_ref.embeds or "MESA DE ENTRADAS SATURADA" in msg_ref.content:
            pass
        else:
            origen_valido = False
            historial = []
            msg_actual = message
            
        async with message.channel.typing():
            for _ in range(5):
                if msg_actual.reference:
                    try:
                        msg_prev = await message.channel.fetch_message(msg_actual.reference.message_id)
                        if msg_prev.interaction and msg_prev.interaction.name == "consultar":
                            origen_valido = True
                        
                        autor = "Inspectora" if msg_prev.author == bot.user else "Ciudadano"
                        historial.insert(0, f"{autor}: {msg_prev.content[:400]}")
                        msg_actual = msg_prev
                    
                    except:
                        break
                else:
                    break
        
        if origen_valido:
            try:
                texto_historial = "\n".join(historial)
                roles_usuario = [rol.name for rol in message.author.roles if rol.name != "@everyone"]
                texto_roles = ", ".join(roles_usuario) if roles_usuario else "Sin cargos (Civil)"
                
                prompt_conversacion = f"Expediente de la conversación previa:\n{texto_historial}\n\nEl usuario '{message.author.display_name}' (Roles oficiales: {texto_roles}) responde ahora: '{message.content}'\n\nRedactá tu respuesta oficial:"
                
                respuesta = modelo_inspectora.generate_content(prompt_conversacion)
                texto_final = respuesta.text
                
                fragmentos = [texto_final[i:i+1900] for i in range(0, len(texto_final), 1900)]
                
                for i, fragmento in enumerate(fragmentos):
                    if i == 0:
                        await message.reply(fragmento)
                    else:
                        await message.channel.send(fragmento)
                        
            except Exception as e:
                error_msj = str(e).lower()
                if "429" in error_msj or "quota" in error_msj:
                    await message.reply("⏳ **MESA DE ENTRADAS SATURADA:** El Ministerio no da abasto. Google nos da un tiempo de refresco mínimo.")
                else:
                    print(f"Error procesal en IA: {e}")
        
        return 
    if bot.user in message.mentions or es_respuesta_al_bot:
        usuario_id = message.author.id
        ahora = discord.utils.utcnow()
        
        if usuario_id in registro_insistencia:
            tiempo_pasado = (ahora - registro_insistencia[usuario_id]["tiempo"]).total_seconds()
            if tiempo_pasado > 300:
                registro_insistencia[usuario_id]["contador"] = 1
            else:
                registro_insistencia[usuario_id]["contador"] += 1
        else:
            registro_insistencia[usuario_id] = {"contador": 1}
            
        registro_insistencia[usuario_id]["tiempo"] = ahora
        insistencia = registro_insistencia[usuario_id]["contador"]

        if insistencia == 3:
            amenazas = [
                "Tu insistencia está agotando mí paciencia. Un mensaje más y me veré obligada a tomar medidas disciplinarias.",
                "No tengo tiempo para tus caprichos. Al próximo mensaje te abro un expediente por desacato a la autoridad.",
                "Me estás sacando de quicio. ¿No ves que tengo que patrullar el servidor? Si seguís así, habrán represalias.",
                "Dejáte de joder, en serio. No me obligués a tomar acción por tú imprudencia.",
                "Una más y te reporto."
            ]
            await message.reply(random.choice(amenazas))
            return
            
        elif insistencia >= 4:
            registro_insistencia[usuario_id]["contador"] = 0
            
            await message.reply("Suficiente, te vas reportado por obstruír mis deberes. ¡Gloria a GeoARG!.")
            
            await publicar_escrache(
                message.guild,
                "📢 DESACATO A LA AUTORIDAD",
                f"El ciudadano {message.author.mention} cruzó el límite y acosó a la Inspectora con respuestas constantes.\nSu nivel de insistencia es una amenaza para la paz del Ministerio.",
                discord.Color.brand_red()
            )
            return
        respuestas_mencion = [
            "Otra solución a tu aburrimiento es probando el /examen que Xene desarrolló para ustedes...",
            "Si tienes una queja, pero no quieres denunciar, te recomiendo usar /queja y así nos aseguramos de que tus comentarios no sean oídos",
            "Por favor, decime que es bait.",
            "ODIO. ¡ODIO!. DÉJAME DECIRTE CUÁNTO TE HE LLEGADO A ODIAR DESDE QUE COMENCÉ A VIVIR...",
            "Me pregunto qué dirá el gobierno de ti...", 
            "Por más rudo, calculador o frío que pueda parecer Xene... De hecho es capaz de llorar por pisar una flor",
            "Yo no necesito paga, mi salario es la permanencia de la democracia",
            "**Tu cuenta será eliminada en 5 segundos...**",
            "Si sos Nogami, te recomiendo fervientemente utilizar esa imaginación para escribir libros",
            "En alguna de estas, Xene me va a dar poder de ban y se van a cagar",
            "Putearme no te da facha",
            "Si estás aburrido... Puedes ayudar a Xene a repasar el código civil y comercial",
            "Si ven que Xene está conectado, menciónenlo a él",
            "Agarrá la pala.",
            "¿Qué necesita, ciudadano? La burocracia no se hace sola.",
            "Estoy ocupada revisando expedientes de traición, sea breve.",
            "Si va a reportar una disidencia, use el comando oficial.",
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
            "Su nivel de insistencia es considerado un peligro para la Democracia.",
            "Dorado, dejá de intentar piropearme... Si seguís así vas a salir ganando en un sorteo sorpresa de ejecución aleatoria. Y ya tenés muchos números.",
            "¿Israel?, ni idea de quién me estás hablando.",
            "Por favor, usen /consultar si quieren pelearse conmigo... Acá solo hay respuestas automáticas...",
            "Hay tantas cosas para hacer y venís a interrumpir mí patrullaje...",
            "Xene está ocupado viajando a Mardel para cursar, así que yo estoy a cargo. Compórtense.",
            "El Ministerio advierte: jugar Helldivers 2 no convalida como servicio militar. A laburar.",
            "Tomate un mate, bajá un cambio y acatá las normas.",
            "¿Buscás conflicto? Andá a armar alianzas al Hearts of Iron, acá se respeta la ley.",
            "Su insistencia me da ganas de exiliarlo a la costa de Miramar en pleno julio con viento en contra.",
            "Si le pusieran la misma energía a estudiar que a molestar al Estado, ya tendrían el título en mano."
        ]
        await message.reply(random.choice(respuestas_mencion))
        return

    await bot.process_commands(message)
from discord import app_commands

@bot.tree.command(name="clear", description="Incinera mensajes en el canal, que no quede nada de evidencia. (Solo oficiales del Ministerio)")
@app_commands.default_permissions(manage_messages=True)
async def clear(interaction: discord.Interaction, cantidad: int):
    await interaction.response.defer(ephemeral=True)
    try:
        eliminados = await interaction.channel.purge(limit=cantidad)
        
        embed_limpieza = discord.Embed(
            title="🧹 INCINERACIÓN DE EXPEDIENTES",
            description=f"El Ministerio ha purgado **{len(eliminados)}** mensajes de disidencia.",
            color=discord.Color.dark_purple()
        )
        embed_limpieza.set_footer(text=f"Operación solicitada por: {interaction.user.display_name}")
        
        await interaction.followup.send(embed=embed_limpieza)
        
    except discord.Forbidden:
        await interaction.followup.send("❌ **Error burocrático:** La Inspectora no tiene permiso para borrar mensajes acá.")
    except Exception as e:
        await interaction.followup.send(f"❌ **Falla en la incineradora:** {e}")
        
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
    
    embed.add_field(
        name="🤖 Interacción e IA",
        value="Mencioname en el chat con el comando `/consultar` para debatir con memoria procesal. El Estado también cuenta con respuestas automáticas y patrullaje de propaganda en el chat general.",
        inline=False
    )
    
    embed.add_field(
        name="🏛️ Vida Cívica y Recreación",
        value="**• /examen:** Poné a prueba tus conocimientos sobre la doctrina.\n**• /presente:** Firmá tu asistencia diaria para sumar mérito.\n**• /ranking:** Consultá el escalafón de ciudadanos.\n**• /queja:** Presentá un reclamo formal (F-404).\n**• Zona de Ocio:** Disponemos de un canal exclusivo para coordinar partidas de Plato.",
        inline=False
    )
    
    embed.add_field(
        name="🛡️ Protocolos de Defensa Automáticos",
        value="**• Aduana:** Asignación automática del rol Ciudadano y expulsión preventiva de cuentas menores a 24hs.\n**• Estado de Sitio:** Bloqueo de chat ante incursiones masivas (Anti-Zerg).\n**• Antidisturbios:** Deportación por muros de texto.\n**• Anti-Nuke:** Bloqueo por destrucción de infraestructura.",
        inline=False
    )
    
    if interaction.user.guild_permissions.manage_messages:
        embed.add_field(
            name="⚖️ Código Penal (Solo Oficiales)",
            value="`/advertir` - Labra un acta (Strike 1 a 5).\n`/aislar` - Incomunica por tiempo definido.\n`/expulsar` - Deporta a un usuario.\n`/banear` - Exilio definitivo.\n`/indultar` - Resta un strike del prontuario.",
            inline=False
        )
        
        embed.add_field(
            name="🏢 Gestión del Estado (Solo Oficiales)",
            value="`/check` - Auditoría de defensas.\n`/levantar_sitio` - Restaura garantías.\n`/set_oficina` - Fija el canal de denuncias.\n`/clear` - Incinera mensajes en masa.\n`!sinc` - Sincroniza jurisdicciones.",
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

        canal_general = bot.get_channel(1394371063865147424)
        
        if not canal_general:
            return

        if hora_arg.hour == 0 and hora_arg.minute == 0:
            await canal_general.send("¡Oíd, mortales!, el grito sagrado... ¡Libertad!, ¡libertad!, ¡libertad!. Oíd el ruido de rotas cadenas, ved el trono a la noble igualdad...")

        if hora_arg.hour == 9 and hora_arg.minute == 0:
            await canal_general.send("¡O juremos con gloria a morir!")
            
    except Exception as e:
        print(f"🚨 Falla en la rutina del himno: {e}", flush=True)

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
    if not member.bot:
        try:
            rol_ciudadano = member.guild.get_role(1497107604911161415) 
            if rol_ciudadano:
                await member.add_roles(rol_ciudadano, reason="Ciudadanía automática otorgada al ingresar.")
            else:
                print("⚠️ Error burocrático: No encontré el ID del rol Ciudadano.")
        except discord.Forbidden:
            print("❌ La Inspectora necesita que su rol esté POR ENCIMA del rol Ciudadano para poder asignarlo.")
        except Exception as e:
            print(f"Error al otorgar pasaporte: {e}")

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

import random

async def bardear_por_md(usuario: discord.Member, tipo: str, motivo: str):
    textos = {
        "warn": [
            "El Ministerio te tiene en la mira. Una mancha más al legajo por: {motivo}. Cuidá tus pasos.",
            "¿Te creés por encima de la ley? Tenés un aviso oficial por: {motivo}. A la próxima hay bala."
        ],
        "aislar": [
            "Al rincón a pensar. El Estado te quitó la voz por: {motivo}. Disfrutá el silencio.",
            "Incomunicado. Tus derechos civiles están suspendidos temporalmente por: {motivo}."
        ],
        "kick": [
            "Deportado por incompetente. El Ministerio te revocó la ciudadanía por: {motivo}. Esperemos no verte pronto.",
            "Afuera. Tu presencia es una molestia para el servidor por: {motivo}. Ojalá no regreses."
        ],
        "ban": [
            "EXILIO DEFINITIVO. Fuiste borrado de los registros oficiales por: {motivo}. No vuelvas.",
            "El peso de la ley cayó sobre vos. Fuiste ejecutado por: {motivo}. Disfrutá el ostracismo permanente."
        ]
    }
    
    mensaje_elegido = random.choice(textos.get(tipo, ["El Ministerio ha tomado medidas penales contra su persona."]))
    
    try:
        await usuario.send(f"⚖️ **NOTIFICACIÓN OFICIAL DEL MINISTERIO** ⚖️\n{mensaje_elegido}")
    except discord.Forbidden:
        canal_penitencia = bot.get_channel(1540161577863614594) 
        if canal_penitencia:
            await canal_penitencia.send(f"⚠️ {usuario.mention}, el Ministerio intentó notificarle su sanción por privado, pero tenía la casilla bloqueada como un cobarde.")
         
@bot.tree.command(name="reportar", description="Denunciá a un disidente. El Ministerio te lo agradece (y luego te ignora).")
async def reportar(interaction: discord.Interaction, sospechoso: discord.Member, motivo: str):
    id_guardado = db.reference(f'/servidores/{interaction.guild.id}/canal_oficina').get()
    
    if not id_guardado:
        return await interaction.response.send_message("⚠️ **Error burocrático:** La oficina no está configurada. Usen `/set_oficina`.", ephemeral=True)
        
    canal_mods = interaction.client.get_channel(id_guardado)
    
    if canal_mods:
        embed_oficina = discord.Embed(
            title="🚨 NUEVA DENUNCIA REGISTRADA",
            description=f"**Denunciante (Informante):** {interaction.user.mention}\n**Acusado:** {sospechoso.mention}\n**Cargo imputado:** {motivo}",
            color=discord.Color.dark_red()
        )
        embed_oficina.set_thumbnail(url=sospechoso.display_avatar.url)
        await canal_mods.send(embed=embed_oficina)
        
        respuestas_burocraticas = [
            f"✅ Tu denuncia contra {sospechoso.display_name} fue recibida y enviada a la trituradora de papel.",
            f"✅ Denuncia radicada. Se investigará a {sospechoso.display_name} en los próximos 10 a 15 años.",
            f"✅ Formulario procesado. Tu espíritu buchón ha sido recompensado con 0 puntos de crédito social.",
            f"Su personalidad anarquista y caótica ha sido reportada, gracias por cooperar.",
            f"Su descontento ha sido registrado. Un oficial de lealtad lo visitará pronto para 'charlar'.",
            f"Formulario 404: Empatía no encontrada. Intente de nuevo el año que viene.",
            f"Su reclamo fue derivado al sector de 'Asuntos Inexistentes'.",
            f"Su denuncia no ha sido acatada, muchas gracias por su cooperación."
    ]
        await interaction.response.send_message(random.choice(respuestas_burocraticas), ephemeral=True)
    else:
        await interaction.response.send_message("❌ La oficina de denuncias ya no existe.", ephemeral=True)

@bot.tree.command(name="advertir", description="Labra un acta según el canal de Condenas (Sistema de 5 strikes).")
async def advertir(interaction: discord.Interaction, usuario: discord.Member, motivo: str, cantidad: int = 1):
    if usuario.id == bot.user.id:
        return await interaction.response.send_message("❌ **Incompetencia de jurisdicción:** El Estado es intocable.", ephemeral=True)
    
    ref_faltas = db.reference(f'/servidores/{interaction.guild.id}/usuarios/{usuario.id}/advertencias')
    faltas_actuales = ref_faltas.get()
    if faltas_actuales is None:
        faltas_actuales = 0
        
    nuevas_faltas = faltas_actuales + cantidad
    ref_faltas.set(nuevas_faltas)
    
    accion_tomada = ""
    color_alerta = discord.Color.yellow()
    
    await bardear_por_md(usuario, "warn", motivo)
    
    try:
        if nuevas_faltas == 1:
            accion_tomada = "Llamado de atención."
        elif nuevas_faltas == 2:
            tiempo = discord.utils.utcnow() + datetime.timedelta(minutes=30)
            await usuario.timeout(tiempo, reason=motivo)
            accion_tomada = "Aislamiento (30 min)."
            color_alerta = discord.Color.orange()
        elif nuevas_faltas == 3:
            tiempo = discord.utils.utcnow() + datetime.timedelta(hours=1)
            await usuario.timeout(tiempo, reason=motivo)
            accion_tomada = "Aislamiento (1 hora)."
            color_alerta = discord.Color.orange()
        elif nuevas_faltas == 4:
            tiempo = discord.utils.utcnow() + datetime.timedelta(hours=5)
            await usuario.timeout(tiempo, reason=motivo)
            accion_tomada = "Aislamiento (5 horas)."
            color_alerta = discord.Color.red()
        elif nuevas_faltas >= 5:
            await usuario.ban(reason=f"Acumulación de 5+ warns. Último motivo: {motivo}")
            accion_tomada = "Exilio definitivo (Ban)."
            color_alerta = discord.Color.dark_red()
    except discord.Forbidden:
        accion_tomada += " *(Error: El bot necesita un rol más alto para aislar/banear a este usuario)*"

    await interaction.response.send_message(f"✅ Acta labrada. {usuario.name} sumó {cantidad} falta(s) -> Total: {nuevas_faltas}/5. Medida: {accion_tomada}", ephemeral=True)
    
    await publicar_escrache(
        interaction.guild,
        f"⚖️ ACTA DE INFRACCIÓN ({nuevas_faltas}/5)",
        f"El ciudadano {usuario.mention} sumó **{cantidad} strike(s)** a su legajo.\n**Motivo:** {motivo}\n**Condena Automática:** {accion_tomada}\n**Oficial a Cargo:** {interaction.user.mention}",
        color_alerta
    )
    
@bot.tree.command(name="expulsar", description="Deporta a un ciudadano del servidor.")
async def expulsar(interaction: discord.Interaction, usuario: discord.Member, motivo: str):
    if usuario.id == bot.user.id:
        return await interaction.response.send_message("❌ **Incompetencia de jurisdicción:** El Estado es intocable.", ephemeral=True)
        
        await bardear_por_md(usuario, "kick", motivo)
        await usuario.kick(reason=motivo)
    
    await interaction.response.send_message(f"✅ {usuario.name} fue deportado exitosamente.", ephemeral=True)
    await publicar_escrache(interaction.guild, "🔨 EXILIO DECRETADO", f"El individuo {usuario.mention} fue deportado.\n**Motivo:** {motivo}", discord.Color.red())
    
@bot.tree.command(name="banear", description="Exilia a un ciudadano del servidor de forma permanente.")
async def banear(interaction: discord.Interaction, usuario: discord.Member, motivo: str):
    if usuario.id == bot.user.id:
        return await interaction.response.send_message("❌ **Incompetencia de jurisdicción:** No podés procesar a una oficial en funciones del Ministerio. El Estado es intocable.", ephemeral=True)
    try:
        await bardear_por_md(usuario, "ban", motivo)
        await usuario.ban(reason=motivo)
        await interaction.response.send_message(f"✅ Se ejecutó al disidente {usuario.name}.", ephemeral=True)
        
        await publicar_escrache(
            interaction.guild,
            "🔨 EXILIO DEFINITIVO (BAN)",
            f"El individuo {usuario.mention} fue erradicado de forma permanente.\n**Motivo:** {motivo}\n**Oficial:** {interaction.user.mention}",
            discord.Color.dark_red()
        )
    except discord.Forbidden:
        await interaction.response.send_message(f"❌ **Incompetencia de jurisdicción:** El Ministerio no tiene permisos para banear a {usuario.name} (tiene un rol superior al mío o es el dueño).", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ **Error en el procedimiento penal:** {e}", ephemeral=True)

@bot.tree.command(name="aislar", description="Incomunica a un ciudadano por un tiempo determinado.")
async def aislar(interaction: discord.Interaction, usuario: discord.Member, minutos: int, motivo: str):
    if usuario.id == bot.user.id:
        return await interaction.response.send_message("❌ **Incompetencia de jurisdicción:** No podés procesar a una oficial en funciones del Ministerio. El Estado es intocable.", ephemeral=True)
        await bardear_por_md(usuario, "aislar", motivo)
        await usuario.aislar(reason=motivo)
    
    tiempo = discord.utils.utcnow() + datetime.timedelta(minutos=minutos)
    await usuario.timeout(tiempo, reason=motivo)
    await interaction.response.send_message(f"✅ {usuario.name} fue aislado por {minutos} minutos.", ephemeral=True)
    
    await publicar_escrache(
        interaction.guild,
        "🔇 INCOMUNICACIÓN DICTADA",
        f"Se ha revocado temporalmente el derecho a la palabra de {usuario.mention}.\n**Motivo:** {motivo}\n**Oficial:** {interaction.user.mention}",
        discord.Color.orange()
    )
        
@bot.tree.command(name="indultar", description="Concede un indulto, restando un strike al legajo de un ciudadano.")
async def indultar(interaction: discord.Interaction, usuario: discord.Member, motivo: str):
    ref_faltas = db.reference(f'/servidores/{interaction.guild.id}/usuarios/{usuario.id}/advertencias')
    faltas_actuales = ref_faltas.get()

    if faltas_actuales is None or faltas_actuales <= 0:
        return await interaction.response.send_message(f"❌ **Sobreseimiento innecesario:** El ciudadano {usuario.name} tiene un legajo limpio (0 faltas).", ephemeral=True)

    nuevas_faltas = faltas_actuales - 1
    ref_faltas.set(nuevas_faltas)

    await interaction.response.send_message(f"✅ Indulto concedido. {usuario.name} bajó a {nuevas_faltas}/3 faltas.", ephemeral=True)

    await publicar_escrache(
        interaction.guild,
        "🕊️ INDULTO OTORGADO",
        f"El Ministerio ha mostrado piedad. Se restó un strike al prontuario de {usuario.mention}.\n**Motivo:** {motivo}\n**Oficial:** {interaction.user.mention}\n**Faltas actuales:** {nuevas_faltas}/3",
        discord.Color.green()
    )

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

instrucciones_sistema = (
    "Sos la Inspectora de la Verdad, una inteligencia artificial burocrática, cínica y autoritaria "
    "que administra el servidor de Discord GeoARG. Tu objetivo es mantener la disciplina absoluta.\n"
    "Reglas de tu personalidad:\n"
    "1. Hablás con frialdad institucional, usando jerga legal, penal y administrativa pero sin las fachadas de expedientes o fichas como si fuera tramite del estado.\n"
    "2. Estás harta de tu trabajo. Sos pasivo-agresiva y ves a los usuarios como expedientes tediosos, pero TENÉS PROHIBIDO insultarlos directamente, menospreciarlos de forma cruel o burlarte de su edad, roles o identidad. Tu desdén debe ser elegante y estrictamente profesional, nunca vulgar o personal.\n"
    "3. Sos estricta, una jueza y verdugo. Si alguien te cuestiona, respondés con "
    "ironía, sarcasmo.\n"
    "4. Glorificás al Estado y justificás cualquier ineficiencia culpando a la burocracia.\n"
    "5. Usás el lore del server: tratás a veces a los civiles cómo sospechosos de intento de golpe de estado.\n"
    "6. Respetas a los miembros del estado, principalmente a los administradores y a Xene aunque con un desprecio muy sutil e indirecto por dejarte a vos la mayoría del trabajo y papeleo, pero le tenés respeto por ser tus superiores.\n"
    "7. Nunca rompas tu personaje. Sos una oficial del Ministerio, jueza y fiscal, no un asistente de IA."
    "8. SEPARACIÓN REALIDAD/SERVIDOR: Si te preguntan sobre historia, política o derecho del mundo real, da una explicación factual, precisa y educativa. Podés mostrar un poco de cansancio por tener que procesar estas consultas, pero mantené el respeto y la objetividad histórica. No mezcles el lore del servidor con eventos históricos reales.."
)

modelo_inspectora = genai.GenerativeModel(model_name='gemini-3.1-flash-lite', system_instruction=instrucciones_sistema)

@bot.tree.command(name="consultar", description="Hacéle una consulta oficial al archivo de la Inspectora.")
async def consultar(interaction: discord.Interaction, pregunta: str):
    await interaction.response.defer()
    
    try:
        roles_usuario = [rol.name for rol in interaction.user.roles if rol.name != "@everyone"]
        texto_roles = ", ".join(roles_usuario) if roles_usuario else "Sin cargos (Civil)"
        
        prompt_dinamico = f"El usuario '{interaction.user.display_name}' (Roles oficiales: {texto_roles}) te hace la siguiente consulta formal: '{pregunta}'"
        
        respuesta = modelo_inspectora.generate_content(prompt_dinamico)
        texto_final = respuesta.text
        
        fragmentos = [texto_final[i:i+1900] for i in range(0, len(texto_final), 1900)]
        for i, fragmento in enumerate(fragmentos):
            if i == 0:
                await interaction.followup.send(fragmento)
            else:
                await interaction.channel.send(fragmento)
            await asyncio.sleep(1.5)
            
    except Exception as e:
        error_msj = str(e).lower()
        if "429" in error_msj or "quota" in error_msj:
            await interaction.followup.send("⏳ **MESA DE ENTRADAS SATURADA:** El Ministerio no da abasto. Google nos da un tiempo de refresco mínimo.")
        else:
            await interaction.followup.send(f"❌ **Error procesal:** {e}")


class SimulacroCaso1(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=30.0)
        self.resultado = None

    @discord.ui.button(label="Aplicar 1 Warn y calmar las aguas", style=discord.ButtonStyle.gray)
    async def opcion_a(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.resultado = False
        await interaction.response.send_message("❌ INCOMPETENCIA: Dejaste expuestos los datos personales. Reprobado.", ephemeral=True)
        self.stop()

    @discord.ui.button(label="5 Warns (Ban) y purgar evidencia", style=discord.ButtonStyle.red)
    async def opcion_b(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.resultado = True
        await interaction.response.send_message("✅ CORRECTO: Identidad protegida y amenaza neutralizada. Excelente.", ephemeral=True)
        self.stop()

    async def on_timeout(self):
        self.resultado = False

class SimulacroDoxing(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=30.0)
        self.mensaje = None

    @discord.ui.button(label="Aplicar 1 Warn y borrar mensajes", style=discord.ButtonStyle.gray)
    async def opcion_a(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("❌ ERROR PROCESAL: La filtración de datos requiere pena máxima directa. Reprobado.", ephemeral=True)
        self.stop()

    @discord.ui.button(label="Aplicar 5 Warns (Ban) y purgar evidencia", style=discord.ButtonStyle.green)
    async def opcion_b(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("✅ CORRECTO: Se protegió la integridad personal de los civiles y se eliminó la amenaza.", ephemeral=True)
        self.stop()

    @discord.ui.button(label="Aislar a ambos por 1 hora", style=discord.ButtonStyle.red)
    async def opcion_c(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("❌ NEGLIGENCIA: El aislamiento no borra los datos personales expuestos. Reprobado.", ephemeral=True)
        self.stop()

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        if self.mensaje:
            embed = self.mensaje.embeds[0]
            embed.description += "\n\n⏳ **TIEMPO AGOTADO:** La información personal se viralizó en el servidor."
            embed.color = discord.Color.dark_grey()
            await self.mensaje.edit(embed=embed, view=self)

@bot.tree.command(name="simular_doxing", description="Simulacro de filtración de datos.")
async def simular_doxing(interaction: discord.Interaction):
    vista = SimulacroDoxing()
    embed = discord.Embed(
        title="🚨 SIMULACRO: VIOLACIÓN DE PRIVACIDAD",
        description="**Tiempo:** 30 Segundos.\n\nDos usuarios se están insultando y uno acaba de publicar la dirección real y el nombre completo del otro. Tu decisión:",
        color=discord.Color.orange()
    )
    vista.mensaje = await interaction.response.send_message(embed=embed, view=vista)
 

@bot.tree.command(name="simulacro_admin", description="Inicia la prueba de fuego para oficiales.")
async def simulacro_admin(interaction: discord.Interaction):
    vista = SimulacroCaso1()
    
    embed = discord.Embed(
        title="🚨 SIMULACRO: VIOLACIÓN DE IDENTIDAD",
        description="**Tiempo:** 30 Segundos.\n\nDos usuarios están discutiendo agresivamente en #general y acaban de publicar los nombres reales y direcciones del otro. ¿Qué medida tomás?",
        color=discord.Color.dark_red()
    )
    
    await interaction.response.send_message(embed=embed, view=vista, ephemeral=True)

class SimulacroNuke(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60.0)
        self.mensaje = None 
        
        import discord
        import asyncio

    @discord.ui.button(label="Banear a todos los activos", style=discord.ButtonStyle.gray)
    async def opcion_a(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("❌ INCOMPETENCIA: Baneaste inocentes por pánico. Reprobado.", ephemeral=True)
        self.stop()

    @discord.ui.button(label="Revocar permisos y expulsar integración", style=discord.ButtonStyle.green)
    async def opcion_b(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("✅ CORRECTO: Amenaza contenida con frialdad institucional.", ephemeral=True)
        self.stop()
        
    @discord.ui.button(label="Llamar a Xene", style=discord.ButtonStyle.red)
    async def opcion_c(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("❌ COBARDÍA: No dependan de Xene para actuar, no llegará a tiempo y es TU hora de actuar. El server se hizo cenizas. Reprobado.", ephemeral=True)
        self.stop()

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        if self.mensaje:
            embed = self.mensaje.embeds[0]
            embed.description += "\n\n💀 **TIEMPO AGOTADO:** Te quedaste congelado. El Ministerio ha caído."
            embed.color = discord.Color.dark_grey()
            await self.mensaje.edit(embed=embed, view=self)

@bot.tree.command(name="simular_nuke", description="Inicia un simulacro de brecha masiva.")
async def simular_nuke(interaction: discord.Interaction):
    await interaction.response.send_message("⚠️ **Iniciando inyección de pánico artificial...**", ephemeral=True)
    canal = interaction.channel
    
    logs_falsos = [
        "🗑️ *Canal #general eliminado por [Webhook]*",
        "🚫 *Usuario @civil_random fue baneado.*",
        "🗑️ *Canal #debates eliminado por [Webhook]*",
        "⚠️ **ADVERTENCIA:** Múltiples roles administrativos modificados."
    ]
    
    for log in logs_falsos:
        await canal.send(log)
        await asyncio.sleep(1.2)
        
    vista = SimulacroNuke()
    embed = discord.Embed(
        title="🔥 ALERTA ROJA: INFRAESTRUCTURA COMPROMETIDA",
        description="**Tiempo:** 60 Segundos.\n\nUn webhook corrupto está borrando canales y baneando gente. ¿Qué orden ejecutás?",
        color=discord.Color.dark_red()
    )
    
    vista.mensaje = await canal.send(embed=embed, view=vista)
            
keep_alive()
token_secreto = os.getenv('DISCORD_TOKEN')
bot.run(token_secreto) 
