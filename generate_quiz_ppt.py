#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor

# Vytvoř prezentaci
prs = Presentation()
prs.slide_width = Inches(10)
prs.slide_height = Inches(7.5)

# Definuj barvy
COLOR_MAIN = RGBColor(44, 62, 80)      # Tmavě modrá
COLOR_ACCENT = RGBColor(231, 76, 60)   # Oranžová-červená
COLOR_LIGHT = RGBColor(236, 240, 241)  # Světlá
COLOR_GREEN = RGBColor(46, 204, 113)   # Zelená
COLOR_GOLD = RGBColor(241, 196, 15)    # Zlatá

def add_title_slide(prs, title, subtitle=""):
    """Přidej titulní slide"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # Blank layout
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = COLOR_MAIN
    
    # Titel
    title_box = slide.shapes.add_textbox(Inches(0.5), Inches(2.5), Inches(9), Inches(2))
    title_frame = title_box.text_frame
    title_frame.word_wrap = True
    p = title_frame.paragraphs[0]
    p.text = title
    p.font.size = Pt(60)
    p.font.bold = True
    p.font.color.rgb = RGBColor(255, 255, 255)
    p.alignment = PP_ALIGN.CENTER
    
    # Subtitle
    if subtitle:
        subtitle_box = slide.shapes.add_textbox(Inches(0.5), Inches(4.8), Inches(9), Inches(2))
        subtitle_frame = subtitle_box.text_frame
        p = subtitle_frame.paragraphs[0]
        p.text = subtitle
        p.font.size = Pt(28)
        p.font.color.rgb = COLOR_GOLD
        p.alignment = PP_ALIGN.CENTER
    
    return slide

def add_content_slide(prs, title, content_items, bg_color=RGBColor(255, 255, 255)):
    """Přidej slide s obsahem"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = bg_color
    
    # Nadpis
    title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.4), Inches(9), Inches(0.8))
    title_frame = title_box.text_frame
    p = title_frame.paragraphs[0]
    p.text = title
    p.font.size = Pt(44)
    p.font.bold = True
    p.font.color.rgb = COLOR_MAIN
    
    # Obsah
    content_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.4), Inches(8.4), Inches(5.5))
    text_frame = content_box.text_frame
    text_frame.word_wrap = True
    
    for i, item in enumerate(content_items):
        if i > 0:
            text_frame.add_paragraph()
        
        p = text_frame.paragraphs[i]
        p.text = item
        p.font.size = Pt(20)
        p.font.color.rgb = RGBColor(50, 50, 50)
        p.space_before = Pt(12)
        p.space_after = Pt(12)
        p.level = 0
    
    return slide

# ============================================================================
# SLIDES
# ============================================================================

# Slide 1: Titulní
add_title_slide(prs, "🎬 RODINNÝ VĚDOMOSTNÍ MARATON 🎮", "Quiz Night - Rodinná Edice")

# Slide 2: Co je to?
add_content_slide(prs, "🎯 Co je Rodinný Vědomostní Maraton?", [
    "✨ Interaktivní quiz pro celou rodinu",
    "👨‍👩‍👧‍👦 Pro všechny věkové kategorie (děti, rodiče, babičky)",
    "🎪 5-6 různorodých herních kol (~60 minut)",
    "🏆 Týmová hra s bodovacím systémem",
    "📺 Zaměření na české pohádky a bajky"
])

# Slide 3: Základní info
add_content_slide(prs, "📋 Základní pravidla", [
    "⏱️ Doba hry: cca 45-60 minut",
    "👥 Počet týmů: 2-3 (rodiče vs. děti nebo smíšené)",
    "🎲 Počet kol: 5-6 s různými formáty",
    "🎁 Vítěz: Tým s nejvíce body",
    "🎉 Atmosféra: Zábava a kooperace na prvním místě!"
])

# Slide 4: Věkové kategorie
add_content_slide(prs, "👧 👦 👨 👩 Přizpůsobení věku", [
    "🍎 Malé děti (4-6 let): Obrázky s tipy, zvuky zvířat",
    "📚 Střední věk (7-10 let): Klasické pohádky bez tipů",
    "🎬 Starší děti (11+): Tvůrci, citáty, hluboké znalosti",
    "👴 👵 Dospělí: Zastalejší pohádky, klíčové postavy"
])

# Slide 5: Kolo 1 - Pohádkové obrázky
add_content_slide(prs, "🖼️ KOLO 1: Pohádkové obrázky", [
    "5-8 otázek - Poznej pohádku z obrázku",
    "🎨 Junior: 3 možnosti na výběr",
    "🎨 Senior: Čistě memory test bez tipů",
    "⭐ Příklady: Popelka, Červená Karkulka, Zvídavý Jiřích",
    "💡 TIP: Obrázky jsou stylizované, ne přesné!"
])

# Slide 6: Kolo 2 - Audio detektiv
add_content_slide(prs, "🔊 KOLO 2: Audio detektiv", [
    "4-5 otázek - Poslouchej a hádej",
    "🎵 Hudba z intro filmů",
    "🎤 Charakteristické věty postav",
    "🐺 Zvuky: zvonění, zvířata, efekty",
    "✅ Děti často poznavají lépe než rodiče"
])

# Slide 7: Kolo 3 - Popis postav
add_content_slide(prs, "🔍 KOLO 3: Kdo jsem? (Popis postav)", [
    "Tipy od nejtěžších k nejzjevnějším:",
    "Tip 1: Vágní/záhadný popis",
    "Tip 2: Konkrétnější informace",
    "Tip 3: Zřejmá vlastnost",
    "Odpověď: Postavy z pohádek"
])

# Slide 8: Kolo 4 - Typovačky
add_content_slide(prs, "🎲 KOLO 4: Typovačky", [
    "📊 Nejčastější/nejméně se opakující:",
    "   - Která pohádka je nejznámější?",
    "🔗 Párování postav s pohádkami",
    "🗝️ Která slova odemykají/zavírají?",
    "⚡ BONUS: Hádej množství (kolik sester, bratrů...)"
])

# Slide 9: Kolo 5 - Bonus režimy
add_content_slide(prs, "🎪 KOLO 5+: BONUS REŽIMY", [
    "🎭 Pantomima: Jeden hraje, ostatní hádají",
    "📝 Napravuj historku: Chybky v příběhu",
    "🧩 Skladanka postav: Složit a identifikovat",
    "🎬 Video/GIF - Doplň repliku"
])

# Slide 10: Skórování
add_content_slide(prs, "🏆 Skórování", [
    "✅ Správná odpověď: 1 bod",
    "⭐ Bez tipů: +1 bonus bod",
    "⚡ Nejrychlejší odpověď: +1 bod",
    "🎭 Pantomima (skvělý výkon): 2-3 body",
    "🥇 🥈 🥉 Vítěz: Medaile/Diplom/Pohádkový dort!"
])

# Slide 11: Praktické tipy
add_content_slide(prs, "💡 Praktické tipy na realizaci", [
    "📝 Obrázky: Stáhni z Pinterstu, Canvy",
    "🎵 Zvuky: YouTube, Spotify (intro filmů)",
    "📊 Tabla: Google Slides pro livescore",
    "🎁 Cena: Pohádkový dort, bonbóny, diplom",
    "⏰ Příprava: 2-3 hodiny včetně shromažďování materiálu"
])

# Slide 12: Příklad otázky - Obrázek
add_content_slide(prs, "📌 PŘÍKLAD: Pohádkové obrázky", [
    "OTÁZKA: Která pohádka to je?",
    "[OBRÁZEK - silueta se zlatými vlasy]",
    "A) Popelka",
    "B) Zlatovláska",
    "C) Červená Karkulka",
    "✅ ODPOVĚĎ: B - Zlatovláska"
])

# Slide 13: Příklad otázky - Popis
add_content_slide(prs, "📌 PŘÍKLAD: Popis postav", [
    "🔍 KDO JSEM? (Postupné tipy)",
    "Tip 1: Přepadám ponocné (těžko)",
    "Tip 2: Mám zlaté vlasy a bydlím v peci",
    "Tip 3: Moje sestra se jmenuje Růženka",
    "✅ ODPOVĚĎ: Božena z 'Zlatovlásky'"
])

# Slide 14: Příklad typovačka
add_content_slide(prs, "📌 PŘÍKLAD: Typovačka", [
    "OTÁZKA: Kolik měla Popelka sester?",
    "A) 1 sestra",
    "B) 2 sestry",
    "C) 3 sestry",
    "D) 4 sestry",
    "✅ ODPOVĚĎ: B - 2 sestry"
])

# Slide 15: Příklad audio
add_content_slide(prs, "📌 PŘÍKLAD: Audio detektiv", [
    "🔊 Poslouchej a hádej:",
    "[ZVUK - charakteristická věta postav]",
    "Která pohádka to je?",
    "A) Budulínek",
    "B) Tři oříšky",
    "C) Zvídavý Jiřích",
    "✅ ODPOVĚĎ: (dle audio ukázky)"
])

# Slide 16: Příklad - Pantomima
add_content_slide(prs, "📌 PŘÍKLAD: Pantomima", [
    "🎭 Jeden z týmu hraje bez slov",
    "Ostatní mají 5 minut na hádání",
    "Příklady:",
    "   - Popelka s dýní",
    "   - Zvídavý Jiřích lezoucí po stromě",
    "   - Tři oříšky padající ze stromu"
])

# Slide 17: Harmonogram
add_content_slide(prs, "⏱️ Doporučený harmonogram (60 minut)", [
    "🕐 0:00-0:05 - Úvod, rozdělení týmů",
    "🕐 0:05-0:15 - Kolo 1: Obrázky",
    "🕐 0:15-0:25 - Kolo 2: Audio",
    "🕐 0:25-0:35 - Kolo 3: Popis postav",
    "🕐 0:35-0:45 - Kolo 4: Typovačky",
    "🕐 0:45-0:55 - Kolo 5: Pantomima",
    "🕐 0:55-1:00 - Vyhlášení vítěze"
])

# Slide 18: Checklist
add_content_slide(prs, "✅ Přípravný checklist", [
    "☐ Sbering obrázků z pohádek (10-15 fotek)",
    "☐ Audio úryvky (5-8 souborů)",
    "☐ Vytvoření otázek a odpovědí",
    "☐ Tabulka pro skórování (Excel/Google Sheets)",
    "☐ Příprava cen/diplom",
    "☐ Zkušební běh (5-10 minut)"
])

# Slide 19: Závěrečná slide
add_title_slide(prs, "🎉 Ať se daří! 🎉", "Vzorný Rodinný Vědomostní Maraton")

# Ulož prezentaci
output_path = r"C:\naucse-python\Rodinny_Vedomostni_Maraton.pptx"
prs.save(output_path)
print("PowerPoint prezentace vytvorena: " + output_path)
print("Pocet slidu: " + str(len(prs.slides)))
