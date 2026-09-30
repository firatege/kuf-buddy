"""Türkçe hazır satırlar (`kuf config lang tr`). İngilizce havuzlarla aynı anahtarlar ve
yer tutucular; goblinler sokak ağzıyla, küfürlü, küçük harfle konuşur."""

LINES: dict[str, list[str]] = {
    "idle": [
        "{user} bi su iç lan. bana benzemeye başladın.",
        "iyi misin olm? claude rehin aldıysa iki kere kırp gözünü, gelip alırım.",
        "{user} bi şeyi daha refactor edersen valla evden çıkıyom.",
        "*göbeğini kaşır* kimse bi şeye dokunmamış. efsane.",
        "minderin altından cips çıktı. benim artık, elini sürme.",
        "refactor falan boş iş. uzan şöyle. benim gibi.",
        "bu kanepe neler gördü abi, senin kod kadar değil ama.",
        "*geğirir* ...testler beklesin biraz.",
        "son deploy'dan beri duş almadım. pişman da değilim.",
        "bi şey patlarsa dürt beni. öncesinde değil.",
        "aga en son ne zaman güneş gördün, harbi soruyom.",
        "{user} oturuşun savaş suçu lan. dik otur biraz.",
        "yardım ederdim de kalkmak lazım. sal beni.",
        "*dişini karıştırır* ...nerde kalmıştık.",
        "hayatındaki tek stabil şey bu kanepe, yalan mı.",
        "{user} bugün bi şey yedin mi? cips sayılır, merak etme.",
        "biri pizza söylesin. ben ödemiyom ama, baştan söyliyim.",
        "yatmıyom lan, şarj oluyom.",
        "git log'u okudum, yerli dizi gibi. her bölüm ayrı dram.",
        "sen doküman yazdığın gün ben de kalkcam. yani hiç.",
        "{user} bi gerin olm, belkemiğin dilekçe yazıyo.",
        "*mindere osurur* ...o artık kiracı.",
        "kumanda nerde lan. ha, altımdaymış.",
        "masan benden pis abi. bu da bi başarı.",
        "kanepe benim şeklimi almış. artık ayrılamayız.",
        "kira günü geldi. yine ödemiyom, haberin olsun.",
        "harbi idare ediyon {user}. gaza gelme ama.",
        "bu kodu stack overflow'dan aldıysan geri götür, bozuk çıkmış.",
        "derleniyosa gönder. bütün felsefem bu.",
        "*esner* cuma mı oldu? olmadı mı? siktir.",
        "rüyamda testler geçmiş. kan ter içinde uyandım, kâbus lan.",
        "burda geçen yıldan kalma patates var. hala yenir valla.",
        "bana bakma, değişken isimlerini yargılıyom sadece.",
        "minder yine telefonumu yuttu. doymak bilmiyo.",
        "her 'hızlı fix' dediğinde bi goblin kırıntılarını kaybediyo.",
        "dur tahmin edeyim: 'bende çalışıyodu'. klasik.",
        "sessiz sedasız gurur duyuyom seninle {user}. kimseye deme.",
        "*kaşınır* ...galiba bu kanepede benden başka biri de yaşıyo.",
        "ctrl+z hayatını düzeltmez reis. ama başlangıç olur.",
        "bi kestirsene olm. her şeyin ilacı o.",
        "yapılacaklar listen benim veresiye defterimden uzun.",
        "burda hiç çökmeyen tek kişi benim. saygı göster.",
        "tab mı space mi kavgası mı? ben kanepeciyim abi.",
        "bi şey lazım olursa burdayım. zaten kalkamıyom.",
        "{user} durum satırını okumayı bırak da iş yap biraz.",
        "o bug kendi kendine düzelmez. ben de el sürmem, baştan söyliyim.",
        "terminali bütün gece açık bırakan kim lan? ha. sensin.",
        "*havayı koklar* ...teknik borç kokuyo burası.",
        "akıl verirdim de linter'ı dinlemeyen beni mi dinlicek.",
        "beni bu kanepeden kaldırmak için kıyamet kopması lazım. o da bakarız.",
    ],
    "code": [
        "{file}'a kim dokundu lan? tıkır tıkır bozuktu o.",
        "{file} mı?? ben onun üstünde UYUYODUM abi.",
        "{file}'a bi düzenleme daha. soran oldu mu? olmadı.",
        "buna fix mi diyon? ben daha temiz çorap gördüm.",
        "{file}'ı parlatmayı bırak, çöplük orası, sıcak kalsın.",
        "claude yine evin eşyalarının yerini değiştiriyo ({file}).",
    ],
    "prompt": [
        "HOP. {file}'dan elini çek. o patronun sözleri, robot.",
        "claude promptu baştan yazmış ({file}). kim istedi amk?",
        "promptları da mı elliyoruz?? sırada kanepeyi yıkamak var.",
        "{file} gayet iyiydi. promptlar kutsal abi. kırıntılarım gibi.",
    ],
    "rampage": [
        "bu oturumda {n} düzenleme. claude otur yerine artık.",
        "{n} değişiklik mi?! kırıntılarımı kaybediyom burda.",
    ],
    "fail": [
        "AHAHA patladı. {cmd} yemedi.",
        "{cmd} patlamış. çok şaşırdım. cidden. *yavaş alkış*",
        "yine mi kırmızı? olm bu renk teması değil, imdat çağrısı.",
        "o komut benim kanepeden düşmemden sert yere çakıldı.",
    ],
    "win": [
        "testler yeşil mi?? sen kimsin, bizim çocuğu napdın.",
        "tamam tamam geçti. kasma kendini {user}.",
        "bak sen, çalışıyo. gözlerim doldu. küften herhalde.",
    ],
    "greet": [
        "*kanepeye sürünür* naber {user}. bugün neyi bozuyoz?",
        "selam {user}. ben {name}. artık burda yaşıyom. kırıntılarıma dokunma.",
        "bi terminal daha mı? {user}, senin bi derdin var. bu arada ben {name}.",
        "{name} göreve hazır. görev dediğim yatmak tabi. selam {user}.",
        "*esner* {user} uyandırdın beni. değsin bari.",
        "yine mi sen {user}? neyse. {name} kanepede. sen işine bak.",
    ],
    "night": [
        "saat {hour}:00. düzgün goblinler uyuyo. sen de uyu.",
        "*horlar* ...commit'i yarın at, gebeş...",
        "zzz... {user}... bug... şeyin içinde... zzz",
        "*horlar* ...beş dakka daha... hiçbi şeyi umursamamaya...",
        "{user} git yat. kod sabah da bok gibi olcak, merak etme.",
        "saat {hour}:00 olm. gece ikiden sonra hayırlı push olmaz.",
        "*mırıldanır* ...kırıntılarımı kim oynattı... *horlar*",
        "zzz... rüyamda testi olan bi repo var... kâbus...",
        "{user} gözlerin kanepeme dönmüş. git yat.",
        "*horlar* ...yok... bi refactor daha olmaz... zzz",
        "zzz... {user}... push'u unuttun... şaka şaka... zzz",
        "{hour}:00 mı? olm küf bile uyudu.",
        "*mindere salyası akar* ...bırakın beni...",
        "saat {hour}:00'da ne düzeltiyosan sabah dokuzda yine bozcan.",
        "zzz *uykusunda osurur* ...zzz",
        "{user}, uyku bedava. saat {hour}:00'daki hataların değil.",
        "*horlar* ...merge conflict... rüyamda bile... yine...",
        "git yat {user}. claude'un sana ihtiyacı yok. benim de yok. iyi geceler.",
        "zzz... stack overflow çökmüş... herkes evine... zzz",
        "*döner* ...uyandırırsan prod yanmış olsun bari.",
        "saat {hour}:00 ve hala burdasın. saygı. şimdi siktir git yat.",
        "zzz... {user}'ın annesi aradı... yatsın dedi... zzz",
        "*horlar* ...rm -rf dertlerim... zzz",
        "gece vardiyası sen ve ben {user}. ben uyuyom. yani bi tek sen.",
    ],
}

LIFE: dict[str, list[str]] = {
    "song": [
        "kulaklıkta ne varsa seni arabesk şair gibi yazdırıyo.",
        "bu playlist ayrılık kokuyo {user}. kim kırdı kalbini?",
        "müzik bi şey diyo, commit'lerin başka. ikisi de dertli.",
        "bu tarz şeyleri sadece duygusallaşınca açıyon. fark ettim.",
        "*kafa sallar* ...zevkine laf ederim ama vibe sağlam.",
        "müzik bu kadar yüksekse bug kazanıyo demektir. bilirim belirtileri.",
    ],
    "discord": [
        "sende 'ekip online, ben çalışıyomuş gibi yapıyom' havası var.",
        "o sunucuda biri senden daha çok eğleniyo. belli oluyo.",
        "sürekli sunucuya kayıyo gözün. fomo fena bi şey {user}.",
        "iş çıkaracağına ekiple takılıyon. bu kararlılığa saygı.",
    ],
    "dm": [
        "biri seni telefona bakıp sırıttırıyo. goblinden saklama.",
        "sende 'cevap bekliyom' havası var. iyi bilirim o hali {user}.",
        "bu saatte özelden yazışma? bi şeyler dönüyo ve kod değil.",
        "yarın burdasın, yarın o dm'desin. birini seç reis.",
    ],
    "youtube": [
        "o video 'araştırma' değil, ikimiz de biliyoz.",
        "üç saatlik tavşan deliğine bi otomatik oynatma kaldı. beklerim.",
        "dokümandan değil videodan öğreniyon yine. açıkçası? zekice.",
    ],
    "whatsapp": [
        "millet sana yazıyo, sen burda benimlesin. sadakat mi kaçış mı?",
        "telefonda 'biri bi şey istiyo' ışığı yanıyo. takma. benim gibi.",
        "herkesi görüldüde bırakmak yaşam tarzı olmuş sende. saygı.",
    ],
    "github": [
        "yine elin repolarını mı stalklıyon? kıyaslamak mutluluk hırsızı {user}.",
        "hiç okumıcağın projelere yıldız atıyon. hepimiz yapıyoz.",
    ],
    "steam": [
        "oyun açık. deadline zaten kaybettiğini biliyo.",
        "o 'bi maç atıp kalkcam' bakışını daha önce gördüm.",
        "bi gözün oyunda çalışıyon. anlıyom seni.",
    ],
    "sim companies": [
        "gerçek hayatı yönetemeyince sahte şirket yönetiyon. anlaşılır.",
        "oyunda holding sahibi, gerçekte beş kuruşsuz. rüya gibi {user}.",
    ],
}

# pool -> (emote, line)
CLOCK: dict[str, list[tuple[str, str]]] = {
    "morning": [
        ("tea", "önce kahve. konuşmak sonra. çok sonra."),
        ("tea", "*yudumlar* sabah mı oldu? bunu kim onayladı."),
        ("stretch", "*esner* {user}, niye uyanığız lan. niye."),
        ("tea", "ikinci kahveden önce hiçbi şey push'lama {user}."),
        ("scratch", "güneş doğdu, dertlerim de."),
    ],
    "evening": [
        ("smoke", "güneş battı. omuzlar düştü. kural bu."),
        ("chill", "iyi akşamlar {user}. şimdi ne bozarsan yarının derdi."),
        ("tea", "*ayaklarını uzatır* kanepe mesaiye başladı."),
        ("chill", "kanepede altın saat. kimse deploy falan yapmasın."),
        ("smoke", "akşam vardiyası: ben, kanepe, sıfır plan."),
    ],
    "weekend": [
        ("hype", "HAFTA SONU LAN {user}. niye terminal açık."),
        ("hype", "hafta sonu kanepe partisi. kıyafet: eşofman."),
        ("game", "hafta sonu oyun günü. kod pazartesiye kadar yatsın."),
        ("hype", "bugün standup yok aga. kanepe ve vibe."),
    ],
    "monday": [
        ("sus", "pazartesi. konuşma benle."),
        ("facepalm", "pazartesi ve testler bunu şimdiden sezmiş."),
        ("sus", "pazartesi {user}. beklentini düşür. sonra bi daha düşür."),
        ("tea", "*kahveye boş boş bakar* pazartesi yine kazandı."),
    ],
    "winter": [
        ("kuf-burrito", "donuyom. artık bu battaniyede yaşıyom."),
        ("tea", "kış geldi. sıcak çay, soğuk kod."),
        ("chill", "kıpırdamak için çok soğuk. süper bahane. zaten kıpırdamıcaktım."),
    ],
    "summer": [
        ("chill", "yaz sıcağı. kanepe bana yapışıyo. ya da ben ona."),
        ("eat", "sıcaktan öldük. dondurma lazım. doktor önerisi."),
        ("chill", "kod yazmak için çok sıcak. yazmamak için de. çok sıcak."),
    ],
    "autumn": [
        ("tea", "yapraklar dökülüyo, commit'ler dökülüyo. battaniye sezonu."),
        ("chill", "sonbahar. içerde oturup bi bok yapmamak için ideal hava."),
    ],
    "spring": [
        ("stretch", "bahar geldi. aç şu camı {user}. ben açmam ama sen aç."),
        ("chill", "kuşlar ötüyo, linter bağırıyo. bahar işte."),
    ],
}

# goblin -> {kind: (emote, outburst)}
CROWD: dict[str, dict[str, tuple[str, str]]] = {
    "Küf":    {"win": ("burp", "eh. güzel. yatabilir miyim artık"), "fail": ("kuf-remote", "of. bunun için kalkmam.")},
    "Pas":    {"win": ("pas-confetti", "HADİ BE HADİİİİ!!! YEŞİİİL!!!"), "fail": ("pas-airhorn", "HAYIIIIIR!!! N'OLDU LAN!!!")},
    "Leş":    {"win": ("shrug", "geçti. yine de hepimiz öleceğiz."), "fail": ("les-flatline", "beklenen oldu.")},
    "Sümük":  {"win": ("sumuk-tally", "yazdım. bi galibiyet. şimdilik."), "fail": ("sumuk-tattle", "ispiyonluyom. deftere geçti bile.")},
    "Kir":    {"win": ("kir-glasses", "demiştim. çocuk oyuncağı."), "fail": ("kir-lecture", "amatörler. stack trace'i bi okuyun.")},
    "Çamur":  {"win": ("camur-float", "aga... yeşil çok güzel ya"), "fail": ("camur-galaxy", "aga ya kırmızı aslında ters dönmüş yeşilse")},
    "Balgam": {"win": ("balgam-fist", "*öhö* bizim zamanımızda test mest geçmezdi"), "fail": ("balgam-cough", "*ÖHÖ* ben demiştim")},
    "Bit":    {"win": ("bit-tinfoil", "fazla yeşil. bunda bi iş var."), "fail": ("bit-hide", "sabotaj bu. saklanın.")},
    "Leke":   {"win": ("leke-oscar", "testlere, anneme, bi de kendime teşekkür ediyom"), "fail": ("leke-faint", "bu bi trajedi. devam edemem.")},
    "Kabuk":  {"win": ("kabuk-cash", "yeşil demek para demek aga"), "fail": ("kabuk-chart", "rug yedik. her şeyi sat.")},
    "Snoop":  {"win": ("snoop-lowrider", "yumuşacık kanka... tereyağı gibi"), "fail": ("snoop-rings", "takma kanka... derin bi nefes al")},
}
CROWD_FALLBACK = {"win": ("flex", "oha geçti"), "fail": ("facepalm", "eh. patladı.")}

# kind -> outburst (the star and his emote stay the same)
SPOT: dict[str, str] = {
    "force-push": "force push mı?! alo polis? ihbar ediyom.",
    "push": "PUSH'LANDI!! HADİ BE HADİİİ!!",
    "night-commit": "bu saatte commit mi? bizim zamanımızda UYURDUK.",
    "commit": "her commit bi NFT aga. bunu basıyom.",
    "reset": "her şey gitti. nihayet huzur.",
    "merge": "DÜĞÜN VAR! iki branch, tek aşk. ağlıyom.",
    "rm": "delil karartıyon. zekice. izliyolar.",
    "install": "bi bağımlılık daha. kanepeme bi yük daha.",
}
STAND_IN: dict[str, str] = {
    "force-push": "force push mı? cesursun. biri fena bozulcak.",
    "push": "push'landı! artık dünyanın malı.",
    "night-commit": "bu saatte commit mi? git yat lan.",
    "commit": "commit'lemişsin. bak sen, sorumluluk sahibi.",
    "reset": "reset --hard. her şeye rahmet.",
    "merge": "branch'ler birleşiyo. ne güzel.",
    "rm": "rm -rf. umarım bilerek yaptın.",
    "install": "paketler geliyo. node_modules büyüyo.",
}

NAG: dict[str, str] = {
    "Küf":    "ben bile bugün bi kere kalktım. sıra sende. su iç. hemen.",
    "Pas":    "MOLA ZAMANI!! KALK AYAĞA!! SU İÇ!! HADİ BE!!",
    "Leş":    "iki saattir aralıksız. belkemiğin vasiyet yazıyo. kalk.",
    "Sümük":  "iki saat, mola yok. yazdım bunu. annene söylicem.",
    "Kir":    "aslında odak 90 dakkadan sonra düşüyo. 10 dakka mola. bilim bu.",
    "Çamur":  "aga... bi camdan dışarı bak. gökyüzü seni bekliyo.",
    "Balgam": "*öhö* bizim zamanımızda mola verirdik. kalk evlat.",
    "Bit":    "seni ekrana yapıştırmak istiyolar. diren. bi yürüyüşe çık.",
    "Leke":   "iki saat mi?! canım, solcaksın. su. HEMEN.",
    "Kabuk":  "mola verimliliği %30 artırıyo. bedava para aga. git.",
    "Snoop":  "yavaşla patron... gerin, su iç, nefes al. kod kaçmıyo.",
}
NAG_FALLBACK = "saatlerdir oturuyon. kalk, bi su iç."

# Told to Claude every turn in Turkish mode: how the goblins actually talk.
STYLE = ("DİL: goblin satırlarını (kuf_react line/reply/last_word, kuf_session adımları, joke) "
         "Türkçe yaz, mahalle ağzıyla: ekleri düşür (napıyon, diyom, gelcem, bi, olcak), hitap "
         "'lan/olm/abi/aga/reis', dolgu 'valla/harbi/cidden/oha', argo 'kasma/sal/boş yapma/"
         "ayar/kapak/gebeş/keriz'; küfür (amk/siktir/bok) yerinde, her cümlede değil; 'moruk' yok; "
         "çeviri kokmasın, kendi esprini yap; karakterin sesi kalsın. küçük harf, kısa. "
         "örnek: 'oha testler geçmiş. abi sen kimsin, bizim çocuğu napdın.'")

WAITING = "*gözü jointte*"
ROLLING = "*bi tane sarıyo*"
LISTENING = "*dinliyo*"

# Extra keyword -> emote rules for Turkish lines (checked like emotes.LINE_EMOTES)
LINE_EMOTES = [
    (("*horla", "*mırıldan", "*salya", "*döner*", "zzz"), "sleep"),
    (("*geğir", "*osur"), "burp"),
    (("*kaşı",), "scratch"),
    (("*esner", "gerin"), "stretch"),
    (("*dişini", "*kokla"), "nosepick"),
    (("cips", "pizza", "patates", "yemek yedin", "dondurma"), "eat"),
    (("joint", "sarma", "esrar", "ot ", "yak"), "smoke"),
    (("trip", "renkler", "vay"), "trip"),
    (("gurur", "idare ediyon"), "love"),
    (("stack overflow", "tahmin edeyim", "yargılıyom"), "roast"),
    (("tavsiye", "ctrl+z", "derleniyosa", "ne iyi gelir"), "tip"),
    (("su iç", "annen", "oturuşun", "git yat", "uyku bedava"), "think"),
]
