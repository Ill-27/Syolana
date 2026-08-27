import telebot
from github import Github
import json
import re
import uuid

# ==========================================
# 1. НАСТРОЙКИ (ВСТАВЬТЕ СВОИ ДАННЫЕ)
# ==========================================
BOT_TOKEN = "8613760399:AAHKckQcervRuAQleiejcRVYTzParJeObIw"
GITHUB_TOKEN = "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"
REPO_NAME = "syolana/Ill-27.github.io" # Например: "syolana/syolana.github.io"

bot = telebot.TeleBot(BOT_TOKEN)
gh = Github(GITHUB_TOKEN)
repo = gh.get_repo(REPO_NAME)

# ==========================================
# 2. МАТРИЦА ИММЕРСИВНОСТИ (СЕМАНТИКА)
# ==========================================
# Ключевые слова : [Список путей к аудио из ваших папок]
AUDIO_MAP = {
    "зима, снег, мороз, метель, вьюга, холод": ["winter/winter_blizzard.ogg", "winter/snow_crunch.ogg"],
    "дождь, ливень, гроза, капли, гром": ["nature/storm_heavy_rain.ogg", "nature/thunder_claps.ogg"],
    "ночь, темнота, мрак, луна, звезды": ["nature/crickets_chirp.ogg", "music/mystic_secret.ogg"],
    "лес, деревья, чаща, ветки, опушка": ["ambience/deep_forest.ogg", "nature/wind_soft.ogg"],
    "море, океан, прибой, волны, берег": ["nature/ocean_waves.ogg"],
    "утро, рассвет, солнце, птицы, свет": ["nature/forest_morning.ogg", "music/happy_acoustic.ogg"],
    "огонь, костер, пламя, камин, тепло": ["nature/campfire_crackling.ogg"],
    "шаги, пошел, подошел, ступал": ["sfx/footsteps_wood.ogg"],
    "бой, битва, меч, кровь, удар, драка": ["combat/sword_clash.ogg", "music/epic_orchestra.ogg"],
    "выстрел, пистолет, револьвер, курок": ["combat/gunshot_pistol.ogg", "combat/gun_reload.ogg"],
    "страх, паника, ужас, сердце, испуг": ["sfx/heartbeat_fast.ogg", "human/heavy_breathing_run_female.ogg", "music/suspense_strings.ogg"],
    "магия, заклинание, колдовство, исцеление": ["magic/magic_chime_spell.ogg", "music/mystic_secret.ogg"],
    "город, улица, толпа, люди, прохожие": ["city/city_muffled_cold.ogg"],
    "поезд, вагон, рельсы, стук колес": ["ambience/train_cabin.ogg"],
    "лошадь, конь, скачет, копыта, верхом": ["transport/horse_gallop_dirt.ogg"],
    "карета, экипаж, повозка": ["sfx/carriage_leaving.ogg"],
    "таверна, трактир, паб, эль, пинты": ["ambience/tavern_crowd.ogg", "sfx/cutlery_clink.ogg"],
    "бал, танцы, вальс, платье, зал": ["ambience/paris_ballroom.ogg", "music/harpsichord_waltz.ogg"],
    "часы, время, полночь, тик-так": ["ambience/antique_clock_tick.ogg", "sfx/clock_chime.ogg"],
    "смех, хохот, улыбка, радость": ["human/hearty_laugh_male.ogg", "human/hearty_laugh_female.ogg"],
    "плач, слезы, горе, рыдает, печаль": ["human/crying_soft.ogg", "music/grief_cello.ogg"],
    "дверь, скрип, открыл, замок": ["sfx/door_creak_old.ogg"],
    "письмо, бумага, перо, чернила": ["sfx/quill_scratch.ogg", "sfx/paper_crumple.ogg"],
    "карты, колода, игра, азарт": ["sfx/cards_shuffle.ogg", "sfx/cards_slap.ogg"]
}

DEFAULT_AUDIO = "ambience/distant_rumble.ogg" # Звук по умолчанию, если ничего не найдено

def assign_audio(text_chunk):
    """Анализирует текст и возвращает строку с путями к аудио через запятую"""
    text_lower = text_chunk.lower()
    selected_audios = []
    
    for keywords_str, audio_paths in AUDIO_MAP.items():
        keywords = [k.strip() for k in keywords_str.split(',')]
        if any(re.search(r'\b' + re.escape(kw) + r'\b', text_lower) for kw in keywords):
            selected_audios.extend(audio_paths)
            
    # Если нашли звуки, возвращаем максимум 2 (чтобы не было каши)
    if selected_audios:
        return ", ".join(list(set(selected_audios))[:2])
    
    return DEFAULT_AUDIO

# ==========================================
# 3. ЛОГИКА БОТА
# ==========================================
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "🌸 Добро пожаловать в Syolana Publisher!\n\nПросто отправьте мне текстовый файл (.txt) с вашей историей или главой, и я превращу её в иммерсивную веб-книгу.")

@bot.message_handler(content_types=['document'])
def handle_book_file(message):
    try:
        msg = bot.reply_to(message, "⏳ Получил файл. Начинаю семантический анализ и подбор звуков...")
        
        # Скачиваем файл из телеграма
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        # Пытаемся декодировать текст
        try:
            text = downloaded_file.decode('utf-8')
        except UnicodeDecodeError:
            text = downloaded_file.decode('windows-1251')
            
        # Убираем лишние пробелы и бьем на абзацы
        paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
        
        blocks = []
        chunk_size = 3 # Количество абзацев на одной странице (экране)
        
        for i in range(0, len(paragraphs), chunk_size):
            chunk = paragraphs[i:i+chunk_size]
            chunk_text = " ".join(chunk)
            
            block = {
                "type": "stanza",
                "ru": chunk,
                "bg": "rgba(10, 5, 20, 0.85)", # Глубокий темный фон по умолчанию
                "glow": "rgba(177, 143, 255, 0.15)",
                "color": "#ffffff",
                "audio": assign_audio(chunk_text)
            }
            blocks.append(block)
            
            # Добавляем разделитель (звездочки) между экранами, если это не последний блок
            if i + chunk_size < len(paragraphs):
                blocks.append({"type": "break"})
                
        # Генерируем уникальный ID для книги
        book_id = f"book_{uuid.uuid4().hex[:8]}"
        
        book_json = {
            "type": "prose",
            "blocks": blocks,
            "next_chapter": None,
            "prev_chapter": None
        }

        bot.edit_message_text("☁️ Текст обработан. Отправляю данные на GitHub...", chat_id=message.chat.id, message_id=msg.message_id)
        
        # Публикация JSON файла в папку books/
        json_content = json.dumps(book_json, ensure_ascii=False, indent=4)
        repo.create_file(
            path=f"books/{book_id}.json",
            message=f"Auto-publish chapter {book_id} via Telegram",
            content=json_content,
            branch="main"
        )
        
        # Формируем ответ
        success_text = (
            f"✅ **Магия совершена!**\n\n"
            f"Книга успешно разбита на страницы, озвучена и отправлена в базу.\n"
            f"**ID Главы:** `{book_id}`\n\n"
            f"*(Не забудьте добавить этот ID в ваш catalog.json, чтобы книга появилась на главной странице!)*"
        )
        bot.edit_message_text(success_text, chat_id=message.chat.id, message_id=msg.message_id, parse_mode="Markdown")

    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка при обработке: {e}")

print("Бот запущен и ждет тексты...")
bot.polling(none_stop=True)
