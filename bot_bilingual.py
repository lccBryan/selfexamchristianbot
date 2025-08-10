# bot_bilingual.py
import os
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, ApplicationBuilder, CommandHandler,
    CallbackQueryHandler, ContextTypes
)

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# -------------------- Localization --------------------

UI = {
    "en": {
        "choose_lang": "Please choose your language",
        "lang_en": "English",
        "lang_zh": "中文",
        "welcome": (
            "Welcome! I can help you reflect on your spiritual health.\n\n"
            "Use /check to choose a questionnaire:\n"
            "• Pride check\n"
            "• Repentance check\n"
            "• Full check (both)\n\n"
            "Scoring: Always=3, Often=2, Occasionally=1, Never=0."
        ),
        "choose_quiz": "Which would you like to do?",
        "btn_pride": "Pride check",
        "btn_repentance": "Repentance check",
        "btn_both": "Full check (both)",
        "start_next": "Starting the next part...",
        "session_expired": "Session expired. Use /check to start again.",
        "choose_one": "Choose one:",
        "section": "Section",
        "result_word": "result",
        "assessment_word": "Assessment",
        "help": "Commands:\n/start – intro\n/check – choose a questionnaire\n/lang – change language",
        "cmd_again": "Type /check to take another assessment or /start for help.",
        "humility_index": "Humility index",
        "repentance_index": "Repentance index",
        "snapshot_title": "Spiritual health snapshot",
        "lang_set": "Language set to English.",
    },
    "zh": {
        "choose_lang": "请选择语言 / Choose language",
        "lang_en": "English",
        "lang_zh": "中文",
        "welcome": (
            "欢迎！我可以帮助你反思灵命健康。\n\n"
            "使用 /check 选择问卷：\n"
            "• 骄傲自省\n"
            "• 悔改自省\n"
            "• 全部（两份问卷）\n\n"
            "评分：经常3分，有时2分，偶尔1分，从不0分。"
        ),
        "choose_quiz": "你想做哪一份问卷？",
        "btn_pride": "骄傲自省",
        "btn_repentance": "悔改自省",
        "btn_both": "全部（两份）",
        "start_next": "进入下一部分……",
        "session_expired": "会话过期，请使用 /check 重新开始。",
        "choose_one": "请选择：",
        "section": "部分",
        "result_word": "结果",
        "assessment_word": "评估",
        "help": "命令：/start — 介绍\n/check — 选择问卷\n/lang — 切换语言",
        "cmd_again": "输入 /check 可再次评估，或输入 /start 查看帮助。",
        "humility_index": "谦卑指数",
        "repentance_index": "悔改指数",
        "snapshot_title": "灵命健康快照",
        "lang_set": "语言已切换为中文。",
    },
}

SCALES = {
    "en": [("Always", 3), ("Often", 2), ("Occasionally", 1), ("Never", 0)],
    "zh": [("经常", 3), ("有时", 2), ("偶尔", 1), ("从不", 0)],
}

# Questionnaires in both languages
QUIZZES: Dict[str, Dict[str, dict]] = {
    "en": {
        "pride": {
            "title": "Self‑Examination: Am I Proud?",
            "max": 45,
            "sections": [
                {
                    "name": "Attitude toward God",
                    "items": [
                        "I often make decisions by myself rather than seeking God’s guidance and will.",
                        "When things don’t go my way, I complain in my heart and doubt God’s goodness.",
                        "I often neglect a life of prayer, thinking I don’t need God’s help.",
                        "I think my success comes from my own effort, not from God’s grace.",
                    ],
                },
                {
                    "name": "Attitude toward other people",
                    "items": [
                        "I often feel I’m smarter, more spiritual, or more capable than others.",
                        "I’m quick to criticize or judge others’ behavior or spiritual condition.",
                        "I dislike being corrected—especially when my spiritual shortcomings are pointed out.",
                        "In a disagreement I find it hard to admit I was wrong.",
                        "I like to draw attention or take credit for what I’ve done, even in church service.",
                    ],
                },
                {
                    "name": "Self‑awareness and reflection",
                    "items": [
                        "I find it hard to accept advice from others, especially from those I consider less experienced than me.",
                        "I look down on some people, thinking they are not as good as I am.",
                        "When others succeed or are affirmed, I feel uneasy or jealous.",
                        "I find it difficult to apologize and ask for forgiveness.",
                        "When I’ve done well, I expect others to recognize and praise me.",
                        "Deep down I’m reluctant to admit I have a problem with pride.",
                    ],
                },
            ],
            "bands": [
                (0, 10, "You’re alert to pride and willing to depend on the Lord to walk humbly."),
                (11, 25, "There may be hidden attitudes of pride. Seek deeper reflection before God; ask the Spirit to reshape you."),
                (26, 45, "Pride appears in several areas. Pray with a trusted mentor/companion; seek repentance and renewal."),
            ],
            "reflection": [
                "Which item struck you most? Why?",
                "How does pride show up in you (e.g., inferiority, comparison, control, fear)?",
                "How will you respond to what God highlighted to you?",
            ],
        },
        "repentance": {
            "title": "Self‑Examination: Have I Truly Repented?",
            "max": 54,
            "sections": [
                {
                    "name": "Understanding of and attitude toward sin",
                    "items": [
                        "When I sin, I clearly realize that I have offended God.",
                        "I feel sorrow over sin itself, not merely fear its consequences.",
                        "I grieve and confess my sins rather than making light, casual apologies.",
                        "I admit my sins on my own instead of waiting for others to point them out.",
                        "I bring my sins into the light—opening up to God and to trustworthy people.",
                    ],
                },
                {
                    "name": "Heart toward God and obedience",
                    "items": [
                        "I genuinely choose to obey God’s will even when it makes me uncomfortable.",
                        "I deny myself and face old patterns and habits, taking action instead of staying stuck.",
                        "I forsake hidden sins rather than secretly cherishing them.",
                        "I’m willing to pay the price to obey God, even when the cost is high.",
                        "I seek lasting change by God’s Word and Spirit, not just temporary emotion.",
                    ],
                },
                {
                    "name": "Relationships and restoration",
                    "items": [
                        "After hurting someone, I take the initiative to apologize and ask for forgiveness.",
                        "I’m willing to repair broken relationships rather than avoid or blame.",
                        "I’m willing to forgive those who hurt me, because God has forgiven me.",
                        "I correct wrong actions with concrete steps, not just say 'sorry'.",
                    ],
                },
                {
                    "name": "Renewal of spiritual life",
                    "items": [
                        "Repentance leads me to a deeper desire to draw near to God.",
                        "Repentance brings holier daily habits.",
                        "Repentance makes me more compassionate, humble, and loving.",
                        "My repentance is ongoing and consistent, not just occasional.",
                    ],
                },
            ],
            "bands": [
                (0, 18, "You may not yet have experienced true repentance, or your sense of sin is dull. Ask the Lord for a repentant heart."),
                (19, 35, "There are signs of genuine repentance, but it’s not yet consistent in daily life. Seek steady growth with a spiritual companion."),
                (36, 54, "You show fruits of true repentance and ongoing renewal. Keep watch and continue."),
            ],
            "reflection": [
                "When was your most recent deep repentance? What happened?",
                "Are there sins you are still rationalizing instead of decisively forsaking?",
                "What area did God highlight through this check?",
                "Will you find a trusted companion to share and pray with regularly?",
            ],
        },
    },
    "zh": {
        "pride": {
            "title": "基督徒自我检视：我是否骄傲？",
            "max": 45,
            "sections": [
                {
                    "name": "对神的态度",
                    "items": [
                        "我是否常常凭自己决定事情，而不是寻求神的引导和旨意？",
                        "当事情未如我愿时，我是否心中埋怨神、不信神的美意？",
                        "我是否经常忽视祷告的生活，觉得自己不需要神的帮助？",
                        "我是否认为自己的成功是靠自己努力而来，而非神的恩典？",
                    ],
                },
                {
                    "name": "对他人的态度",
                    "items": [
                        "我是否常常觉得自己比别人更聪明、更属灵、更有能力？",
                        "我是否容易批评、论断他人的行为或信仰状况？",
                        "我是否讨厌被劝勉、纠正，尤其是指出我属灵上的缺点？",
                        "我是否在与人争论时，很难承认自己的错误？",
                        "我是否渴望别人注意、称赞我所做的，甚至在教会服事中？",
                    ],
                },
                {
                    "name": "自我认识与反省",
                    "items": [
                        "我是否不容易接受别人的建议，尤其是来自比我“资浅”的人？",
                        "我是否在心里看轻某些人，觉得他们“不如我”？",
                        "我是否在别人成功或受肯定时感到不安或嫉妒？",
                        "我是否很难向人道歉，请求饶恕？",
                        "当我做对事时，我是否期待别人承认我的功劳或赞许？",
                        "我是否在心中不愿意承认自己有骄傲的问题？",
                    ],
                },
            ],
            "bands": [
                (0, 10, "你对骄傲的问题有自知与警觉，愿意倚靠主谦卑行事。"),
                (11, 25, "可能有些隐藏的骄傲态度，需要在神面前更深省察，求圣灵提醒与塑造。"),
                (26, 45, "在多个方面显出骄傲的倾向。建议与信任的属灵同伴或导师一起祷告、分享，寻求悔改与更新。"),
            ],
            "reflection": [
                "哪一题最触动你？为什么？",
                "骄傲在你身上的样貌是什么？（如：自卑、比较、掌控欲、恐惧等）",
                "你愿意如何回应神在这次检视中对你说的话？",
            ],
        },
        "repentance": {
            "title": "基督徒自我检视：我是否真的悔改了？",
            "max": 54,
            "sections": [
                {
                    "name": "对罪的认识与态度",
                    "items": [
                        "当我犯罪得罪神时，我是否清楚意识到这是得罪了神？",
                        "我是否感到对罪的忧伤，而不是只怕后果？",
                        "我是否常常为罪忧伤、认罪，而不是轻描淡写地道歉？",
                        "我是否愿意主动承认自己的罪，而不是等别人指出？",
                        "我是否愿意把罪带到光中，向神和可信赖的人敞开？",
                    ],
                },
                {
                    "name": "对神的心意与顺服",
                    "items": [
                        "我是否真心愿意顺服神的旨意，即使这会让我不舒服？",
                        "我是否愿意否定旧我，面对旧有的习惯和问题，而不是反复挣扎却不行动？",
                        "我是否不仅感到内疚，更是决心弃绝隐藏的罪，不再“心存喜爱”？",
                        "我是否愿意为顺服神付代价，即使代价很高？",
                        "我是否渴望在神的话语与圣灵里持续改变，而不仅是一时情绪的悔恨？",
                    ],
                },
                {
                    "name": "人际关系与修复",
                    "items": [
                        "我是否在伤害他人之后主动道歉、求饶恕？",
                        "我是否愿意修复破裂的关系，而不是逃避或责怪？",
                        "我是否愿意饶恕伤害我的人，因为神也赦免了我？",
                        "我是否在行为上作出应当纠正的事，而不是仅仅说“对不起”？",
                    ],
                },
                {
                    "name": "属灵生命的更新",
                    "items": [
                        "我的悔改是否让我更渴慕亲近神？",
                        "我的悔改是否带来更圣洁的生活习惯？",
                        "我的悔改是否让我更有怜悯、谦卑和爱心？",
                        "我的悔改是否是持续的，而非偶尔的感动？",
                    ],
                },
            ],
            "bands": [
                (0, 18, "可能尚未经历真实的悔改，或对罪缺乏敏感。求主赐下悔改的心。"),
                (19, 35, "已有真实悔改的迹象，但尚未在生活中持续展开。建议与属灵同伴一同追求稳健成长。"),
                (36, 54, "生命中显出真实悔改的果子，并持续在圣灵引导下更新。请继续警醒，不放松。"),
            ],
            "reflection": [
                "最近一次深刻认罪悔改是什么时候？发生了什么？",
                "是否仍在合理化某些罪，而非断然离弃？",
                "这次检视中神光照了哪些需要调整的领域？",
                "是否愿意找一位属灵同伴定期分享与代祷？",
            ],
        },
    },
}

def flatten(lang: str, quiz_key: str) -> List[Tuple[str, str]]:
    pairs = []
    for section in QUIZZES[lang][quiz_key]["sections"]:
        for item in section["items"]:
            pairs.append((section["name"], item))
    return pairs

# Precompute flattened questions per language
FLAT = {lang: {k: flatten(lang, k) for k in v.keys()} for lang, v in QUIZZES.items()}

# -------------------- Session state --------------------

@dataclass
class Session:
    lang: str
    queue: List[str]
    current: str
    idx: int = 0
    answers: Dict[str, List[int]] = field(default_factory=dict)

    def total_questions(self) -> int:
        return len(FLAT[self.lang][self.current])

    def add_answer(self, pts: int):
        self.answers.setdefault(self.current, []).append(pts)

    def next_question(self) -> bool:
        self.idx += 1
        return self.idx < self.total_questions()

    def switch_next_quiz(self) -> bool:
        if len(self.queue) <= 1:
            return False
        self.queue.pop(0)
        self.current = self.queue[0]
        self.idx = 0
        return True

SESSIONS: Dict[int, Session] = {}

# -------------------- Helpers --------------------

def get_lang(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    lang = context.user_data.get("lang")
    if lang:
        return lang
    # Fallback to Telegram's language; default to English if not zh
    tg_lang = (update.effective_user.language_code or "").lower()
    lang = "zh" if tg_lang.startswith("zh") else "en"
    context.user_data["lang"] = lang
    return lang

def t(lang: str, key: str) -> str:
    return UI[lang][key]

def scale_keyboard(lang: str) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(f"{label} ({pts})", callback_data=f"ans:{pts}")]
        for label, pts in SCALES[lang]
    ]
    return InlineKeyboardMarkup(buttons)

async def send_question(update: Update, context: ContextTypes.DEFAULT_TYPE, sess: Session):
    q = QUIZZES[sess.lang][sess.current]
    section, text = FLAT[sess.lang][sess.current][sess.idx]
    q_num = sess.idx + 1
    total = sess.total_questions()
    msg = (
        f"{q['title']}\n"
        f"{t(sess.lang, 'section')}: {section}\n"
        f"Q{q_num}/{total}: {text}\n\n"
        f"{t(sess.lang, 'choose_one')}"
    )
    if update.callback_query:
        await update.callback_query.edit_message_text(msg, reply_markup=scale_keyboard(sess.lang))
    else:
        await update.message.reply_text(msg, reply_markup=scale_keyboard(sess.lang))

def band_message(points: int, bands: List[Tuple[int, int, str]]) -> str:
    for lo, hi, msg in bands:
        if lo <= points <= hi:
            return msg
    return ""

def analyze_quiz(lang: str, key: str, points: int) -> str:
    q = QUIZZES[lang][key]
    pct = round(points / q["max"] * 100)
    return (
        f"{q['title']} {t(lang, 'result_word')}\n"
        f"- Score: {points} / {q['max']} ({pct}%)\n"
        f"- {t(lang, 'assessment_word')}: {band_message(points, q['bands'])}"
    )

def combine_snapshot(lang: str, pride_total: int | None, repentance_total: int | None) -> str:
    parts = []
    if pride_total is not None:
        humility_index = round((1 - (pride_total / QUIZZES[lang]['pride']['max'])) * 100)
        parts.append(f"{t(lang, 'humility_index')}: {humility_index}/100")
    if repentance_total is not None:
        repentance_index = round((repentance_total / QUIZZES[lang]['repentance']['max']) * 100)
        parts.append(f"{t(lang, 'repentance_index')}: {repentance_index}/100")
    if pride_total is not None and repentance_total is not None:
        overall = round(((1 - pride_total/QUIZZES[lang]['pride']['max']) + (repentance_total/QUIZZES[lang]['repentance']['max']))/2 * 100)
        parts.append(f"{t(lang, 'snapshot_title')}: {overall}/100")
    return "\n".join(parts)

def reflection_text(lang: str, key: str) -> str:
    qs = "\n".join([f"- {x}" for x in QUIZZES[lang][key]["reflection"]])
    return f"Reflection / 反思\n{qs}"

# -------------------- Handlers --------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Offer language selection on start
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(UI["en"]["lang_en"], callback_data="lang:en"),
         InlineKeyboardButton(UI["zh"]["lang_zh"], callback_data="lang:zh")]
    ])
    await update.message.reply_text(UI["en"]["choose_lang"] + " / " + UI["zh"]["choose_lang"], reply_markup=kb)

async def set_lang(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cq = update.callback_query
    await cq.answer()
    lang = cq.data.split(":")[1]
    context.user_data["lang"] = lang
    await cq.edit_message_text(UI[lang]["lang_set"])
    await cq.message.reply_text(UI[lang]["welcome"])

async def lang_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(UI["en"]["lang_en"], callback_data="lang:en"),
         InlineKeyboardButton(UI["zh"]["lang_zh"], callback_data="lang:zh")]
    ])
    await update.message.reply_text(UI["en"]["choose_lang"] + " / " + UI["zh"]["choose_lang"], reply_markup=kb)

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(update, context)
    await update.message.reply_text(UI[lang]["help"])

async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(update, context)
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(UI[lang]["btn_pride"], callback_data="start:pride"),
         InlineKeyboardButton(UI[lang]["btn_repentance"], callback_data="start:repentance")],
        [InlineKeyboardButton(UI[lang]["btn_both"], callback_data="start:both")],
    ])
    await update.message.reply_text(UI[lang]["choose_quiz"], reply_markup=kb)

async def on_start_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cq = update.callback_query
    await cq.answer()
    user_id = cq.from_user.id
    lang = context.user_data.get("lang") or "en"
    choice = cq.data.split(":")[1]
    queue = ["pride", "repentance"] if choice == "both" else [choice]
    sess = Session(lang=lang, queue=queue, current=queue[0])
    SESSIONS[user_id] = sess
    await send_question(update, context, sess)

async def on_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cq = update.callback_query
    await cq.answer()
    user_id = cq.from_user.id
    sess = SESSIONS.get(user_id)
    if not sess:
        lang = get_lang(update, context)
        await cq.edit_message_text(UI[lang]["session_expired"])
        return
    pts = int(cq.data.split(":")[1])
    sess.add_answer(pts)

    if sess.next_question():
        await send_question(update, context, sess)
        return

    # Finish current quiz
    total = sum(sess.answers[sess.current])
    await cq.edit_message_text(analyze_quiz(sess.lang, sess.current, total))
    await cq.message.reply_text(reflection_text(sess.lang, sess.current))

    # Move to next or finalize
    if sess.switch_next_quiz():
        await cq.message.reply_text(UI[sess.lang]["start_next"])
        await send_question(update, context, sess)
    else:
        pride_total = sum(sess.answers.get("pride", [])) if "pride" in sess.answers else None
        repentance_total = sum(sess.answers.get("repentance", [])) if "repentance" in sess.answers else None
        snapshot = combine_snapshot(sess.lang, pride_total, repentance_total)
        if snapshot:
            await cq.message.reply_text(snapshot)
        await cq.message.reply_text(UI[sess.lang]["cmd_again"])
        SESSIONS.pop(user_id, None)

def main():
    if not BOT_TOKEN:
        raise RuntimeError("Please set BOT_TOKEN environment variable.")
    app: Application = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("lang", lang_cmd))
    app.add_handler(CommandHandler("check", check))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CallbackQueryHandler(set_lang, pattern=r"^lang:"))
    app.add_handler(CallbackQueryHandler(on_start_choice, pattern=r"^start:"))
    app.add_handler(CallbackQueryHandler(on_answer, pattern=r"^ans:"))
    app.run_polling()

if __name__ == "__main__":
    main()
