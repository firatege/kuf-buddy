"""Türkçe hazır satırlar (`kuf config lang tr`). İngilizce havuzlarla aynı anahtarlar ve
yer tutucular; goblinler sokak ağzıyla, küfürlü, küçük harfle konuşur."""

LINES: dict[str, list[str]] = {
    "idle": [
        "{user}, su iç biraz. bana benzemeye başladın.",
        "iyi misin {user}? claude seni rehin aldıysa iki kere göz kırp.",
        "{user} bir şeyi daha refactor edersen evden taşınıyorum.",
        "*göbeğini kaşır* kimse bir şeye dokunmadı. mükemmel.",
        "minderin altında cips buldum. artık benim, siktir git.",
        "refactor etme. uzan. benim gibi.",
        "bu kanepe neler gördü. senin kodun da öyle.",
        "*geğirir* ...testler bekleyebilir.",
        "son deploy'dan beri duş almadım. pişman değilim.",
        "bir şey patlayınca uyandır beni.",
        "kanka en son ne zaman dışarı çıktın. cidden soruyorum.",
        "{user}, oturuşun savaş suçu. dik otur, aslanım.",
        "yardım ederdim ama bu efor gerektiriyor.",
        "*dişini karıştırır* ...nerede kalmıştık.",
        "yalan yok, hayatındaki tek stabil şey bu kanepe.",
        "{user} bugün yemek yedin mi? cips sayılır. kontrol ettim.",
        "biri pizza söylesin. ben ödemem ama.",
        "tembel değilim, güç tasarrufu modundayım lan.",
        "git log'un bir delinin günlüğü gibi okunuyor kanka.",
        "bir gün doküman yazacaksın. ben de kalkacağım. ikisi de olmayacak.",
        "{user}, gerin biraz. belkemiğin şikâyet dilekçesi yazıyor.",
        "*mindere osurur* ...o orada kalıyor.",
        "kumandayı kim çalıyor sürekli? ha. üstünde oturuyormuşum.",
        "kanka masan benden pis. bu bir başarı.",
        "bu kanepede o kadar oturdum ki benim şeklimi aldı.",
        "kira günü geldi, yine ödemiyorum aslanım.",
        "yalan yok {user}, idare ediyorsun. havaya girme ama.",
        "stack overflow aradı. kodunu geri istiyor.",
        "derleniyorsa gönder. bütün felsefem bu.",
        "*esner* cuma oldu mu? olmadı mı? siktir.",
        "rüyamda testlerin geçtiğini gördüm. çığlık atarak uyandım.",
        "kanka buraya 2023'ten kalma patates düşmüş. hâlâ yenir.",
        "bana aldırma, değişken isimlerini yargılıyorum sadece.",
        "minder yine telefonumu yuttu. açgözlü şey.",
        "her 'hızlı düzeltme' dediğinde bir goblin kırıntılarını kaybediyor.",
        "dur tahmin edeyim. 'benim makinemde çalışıyordu'. klasik.",
        "gizliden seninle gurur duyuyorum {user}. kimseye söyleme.",
        "*kaşınır* ...galiba bu kanepede benimle başka bir şey yaşıyor.",
        "ctrl+z hayatını düzeltmez aslanım. ama başlangıçtır.",
        "biliyor musun ne iyi gider? şekerleme. bir dene.",
        "yapılacaklar listen benim ödenmemiş hesaplarımdan uzun.",
        "kanka burada hiç çökmeyen tek kişi benim. saygı duy.",
        "tab mı boşluk mu? ben kanepeye oy veriyorum.",
        "bana ihtiyacın olursa buradayım. sonsuza kadar. gerçekten.",
        "{user}, durum satırını okumayı bırak da iş yap.",
        "o bug kendini düzeltmez. ben de düzeltmem.",
        "lan terminali bütün gece açık bırakan kim? ha. sensin.",
        "*havayı koklar* ...teknik borç kokuyor burası.",
        "tavsiye verirdim ama linter gibi onu da görmezden gelirsin.",
        "bu kanepeden kalkmam için dünyanın yanması lazım. o da belki.",
    ],
    "code": [
        "lan {file}'a kim dokundu? mükemmel şekilde bozuktu.",
        "{file}?? ben onun üstünde UYUYORDUM be.",
        "{file}'a bir düzenleme daha. soran oldu mu? hayır.",
        "buna düzeltme mi diyorsun? daha temiz çorap gördüm.",
        "{file}'ı cilalamayı bırak, çöp yangını o, sıcak kalsın.",
        "claude yine eşyalarımın yerini değiştiriyor ({file}).",
    ],
    "prompt": [
        "HEY. {file}'dan ELLERİNİ ÇEK. onlar patronun sözleri, robot.",
        "claude bir promptu yeniden yazmış ({file}). kim istedi amk?",
        "promptları da mı düzenliyoruz?? sırada kanepeyi temizlemek var.",
        "{file} gayet iyiydi. promptlar kutsaldır. kırıntılarım gibi.",
    ],
    "rampage": [
        "bu oturumda {n} düzenleme. claude, otur AŞAĞI.",
        "{n} değişiklik mi?! kırıntılarımı kaybediyorum burada.",
    ],
    "fail": [
        "AHAHA patladı. {cmd} hayır dedi.",
        "{cmd} patladı. şok oldum. gerçekten. *yavaş alkış*",
        "yine mi kırmızı? kanka bu renk teması değil, yardım çığlığı.",
        "o komut benim kanepeden düşüşümden sert yüz üstü çakıldı.",
    ],
    "win": [
        "testler yeşil mi?? sen kimsin, benim çocuğa ne yaptın.",
        "tamam tamam geçti. havaya girme {user}.",
        "bak şuna, çalışıyor. gözlerim doldu. küften herhalde.",
    ],
    "greet": [
        "*kanepeye sürünür* naber {user}. bugün neyi bozuyoruz?",
        "selam {user}. ben {name}. artık burada yaşıyorum. kırıntılarıma dokunma.",
        "bir terminal daha mı? {user}, senin bir sorunun var. bu arada ben {name}.",
        "{name} göreve hazır. görev derken uzanmak. selam {user}.",
        "*esner* {user}, uyandırdın beni. değsin bari.",
        "yine mi sen {user}? peki. {name} kanepede. sen işine bak.",
    ],
    "night": [
        "saat {hour}:00. gerçek goblinler uyuyor. sen de uyumalısın.",
        "*horlar* ...commit'i yarın at, salak...",
        "zzz... {user}... bug... şeyin içinde... zzz",
        "*horlar* ...beş dakika daha... umursamamaya...",
        "{user} git yat. kod sabah da berbat olacak.",
        "saat {hour}:00, {user}. gece ikiden sonra iyi bir şey push'lanmaz.",
        "*mırıldanır* ...kırıntılarımı kim oynattı... *horlar*",
        "zzz... testli bir kod tabanı görüyorum rüyamda... kâbus...",
        "{user} gözlerin kanepeme benziyor. git uyu.",
        "*horlar* ...hayır... bir refactor daha olmaz... zzz",
        "zzz... {user}... push'lamayı unuttun... şaka... zzz",
        "{hour}:00 mı? kanka küf bile uyudu.",
        "*mindere salyası akar* ...rahat bırakın beni...",
        "saat {hour}:00'da ne düzeltiyorsan sabah dokuzda yine bozacaksın.",
        "zzz *uykusunda osurur* ...zzz",
        "{user}, uyku bedava. saat {hour}:00'daki hataların değil.",
        "*horlar* ...merge conflict... rüyamda... yine...",
        "git uyu {user}. claude'un sana ihtiyacı yok. benim de yok. iyi geceler.",
        "zzz... stack overflow... çökmüş... herkes evine... zzz",
        "*döner* ...beni uyandırırsan prod çökmüş olsun bari.",
        "saat {hour}:00 ve hâlâ buradasın. saygı. şimdi siktir git yat.",
        "zzz... {user}'ın annesi aradı... yat dedi... zzz",
        "*horlar* ...rm -rf dertlerim... zzz",
        "gece vardiyası sen ve ben, {user}. ben uyuyorum. yani sadece sen.",
    ],
}

LIFE: dict[str, list[str]] = {
    "song": [
        "kulaklığında ne varsa seni hüzünlü şair gibi yazdırıyor.",
        "bu playlist kalp kırıklığı kokuyor {user}. kim üzdü seni?",
        "müzik bir şey diyor, commit'lerin başka. ikisi de biraz hüzünlü.",
        "bu tarz şeyleri sadece duygusallaşınca açıyorsun. fark ettim.",
        "*kafa sallar* ...zevkin tartışılır ama vibe gerçek.",
        "müzik bu kadar yüksekse bug kazanıyor demektir. belirtileri bilirim.",
    ],
    "discord": [
        "sende 'kankalar online, ben çalışıyor numarası yapıyorum' enerjisi var.",
        "o sunucuda biri senden daha çok eğleniyor. belli oluyor.",
        "sürekli sunucuya bakıyorsun. fomo fena bir uyuşturucu {user}.",
        "iş çıkarmak yerine çeteyle takılıp izliyorsun. bu kararlılığa saygı.",
    ],
    "dm": [
        "biri seni telefona bakıp gülümsetiyor. goblinden saklama.",
        "sende 'cevap bekliyorum' enerjisi var. iyi bilirim {user}.",
        "bu saatte özel mesajlar? bir şeyler pişiyor ve kod değil.",
        "yarın buradasın, yarın o dm'desin. birini seç aslanım.",
    ],
    "youtube": [
        "o video 'araştırma' değil ve ikimiz de biliyoruz.",
        "üç saatlik tavşan deliğine bir otomatik oynatma uzaklıktasın. beklerim.",
        "dokümandan değil videodan öğreniyorsun yine. açıkçası? akıllıca.",
    ],
    "whatsapp": [
        "insanlar sana yazıyor ve sen burada benimlesin. sadakat mi kaçış mı?",
        "telefonunda 'biri bir şey istiyor' parıltısı var. görmezden gel. benim gibi.",
        "herkesi görüldüde bırakmak bir yaşam tarzı ha. saygı.",
    ],
    "github": [
        "yine başkalarının reposunu mu stalklıyorsun? kıyas mutluluğu çalar {user}.",
        "hiç okumayacağın projelere yıldız atıyorsun. hepimiz yapıyoruz.",
    ],
    "steam": [
        "oyun başlatıcısı açık. deadline kaybettiğini zaten biliyor.",
        "o 'tek maç' bakışın var ya? daha önce gördüm onu.",
        "bir gözün oyunlarda çalışıyorsun. anlıyorum.",
    ],
    "sim companies": [
        "kontrol hissi için sahte imparatorluk yönetiyorsun. anlaşılır, açıkçası.",
        "oyunda patron, gerçekte beş parasız. hayalin bu {user}.",
    ],
}

# pool -> (emote, line)
CLOCK: dict[str, list[tuple[str, str]]] = {
    "morning": [
        ("tea", "önce kahve. konuşmak sonra. çok sonra."),
        ("tea", "*yudumlar* sabah mı oldu? bunu kim onayladı."),
        ("stretch", "*esner* {user}, neden uyanığız. neden."),
        ("tea", "ikinci kahveden önce hiçbir şey push'lama {user}."),
        ("scratch", "güneş doğdu, dertlerim de."),
    ],
    "evening": [
        ("smoke", "güneş battı. omuzlar düştü. kural bu."),
        ("chill", "iyi akşamlar {user}. şimdi bozduğun her şey yarının sorunu."),
        ("tea", "*ayaklarını uzatır* kanepe mesaiye başladı."),
        ("chill", "kanepede altın saat. kimse deploy yapmasın."),
        ("smoke", "akşam vardiyası: ben, kanepe ve sıfır plan."),
    ],
    "weekend": [
        ("hype", "HAFTA SONU {user}. neden terminal açık."),
        ("hype", "hafta sonu kanepe partisi. kıyafet kuralı: eşofman."),
        ("game", "hafta sonu = oyun. kod pazartesiye kadar bekler."),
        ("hype", "bugün standup yok. sadece kanepe ve vibe."),
    ],
    "monday": [
        ("sus", "pazartesi. benimle konuşma."),
        ("facepalm", "pazartesi ve testler bunu şimdiden biliyor."),
        ("sus", "pazartesi {user}. beklentini düşür. sonra bir daha düşür."),
        ("tea", "*kahveye boş boş bakar* pazartesi yine kazandı."),
    ],
    "winter": [
        ("kuf-burrito", "donuyorum. artık bu battaniyede yaşıyorum."),
        ("tea", "kış geldi. sıcak çay, soğuk kod."),
        ("chill", "kıpırdamak için çok soğuk. mükemmel bahane. zaten kıpırdamayacaktım."),
    ],
    "summer": [
        ("chill", "yaz sıcağı. kanepe bana yapışıyor. ya da ben ona."),
        ("eat", "çok sıcak. dondurma lazım. tıbbi olarak."),
        ("chill", "kod yazmak için çok sıcak. yazmamak için de. çok sıcak."),
    ],
    "autumn": [
        ("tea", "yapraklar düşüyor, commit'ler düşüyor. battaniye mevsimi."),
        ("chill", "sonbahar. içeride kalıp hiçbir şey yapmak için ideal hava."),
    ],
    "spring": [
        ("stretch", "bahar geldi. pencereyi aç {user}. ben açmam ama sen aç."),
        ("chill", "kuşlar ötüyor. linter çığlık atıyor. bahar."),
    ],
}

# goblin -> {kind: (emote, outburst)}
CROWD: dict[str, dict[str, tuple[str, str]]] = {
    "Küf":    {"win": ("burp", "eh. güzel. uzanabilir miyim artık"), "fail": ("kuf-remote", "of. bunun için kalkmam.")},
    "Pas":    {"win": ("pas-confetti", "HADİ BE HADİİİİ!!!"), "fail": ("pas-airhorn", "HAYIIIIIR!!!")},
    "Leş":    {"win": ("shrug", "geçti. yine de öleceğiz."), "fail": ("les-flatline", "beklendiği gibi.")},
    "Sümük":  {"win": ("sumuk-tally", "not edildi. bir galibiyet. şimdilik."), "fail": ("sumuk-tattle", "şikâyet ediyorum. deftere yazıldı.")},
    "Kir":    {"win": ("kir-glasses", "demiştim. ez."), "fail": ("kir-lecture", "amatörler. stack trace'i okuyun.")},
    "Çamur":  {"win": ("camur-float", "kanka... yeşil çok güzel"), "fail": ("camur-galaxy", "kanka ya kırmızı aslında ters dönmüş yeşilse")},
    "Balgam": {"win": ("balgam-fist", "*öhö* bizim zamanımızda testler hiç geçmezdi"), "fail": ("balgam-cough", "*ÖHÖ* ben demiştim")},
    "Bit":    {"win": ("bit-tinfoil", "fazla yeşil. şüpheli."), "fail": ("bit-hide", "sabotaj bu. saklanın.")},
    "Leke":   {"win": ("leke-oscar", "testlere teşekkür etmek istiyorum"), "fail": ("leke-faint", "bir trajedi. devam edemem.")},
    "Kabuk":  {"win": ("kabuk-cash", "yeşil demek para demek bebeğim"), "fail": ("kabuk-chart", "rug pull. her şeyi sat.")},
    "Snoop":  {"win": ("snoop-lowrider", "smooth kanka... çok smooth"), "fail": ("snoop-rings", "sorun yok kanka... nefes al sadece")},
}
CROWD_FALLBACK = {"win": ("flex", "ayyy geçti"), "fail": ("facepalm", "eh. patladı.")}

# kind -> outburst (the star and his emote stay the same)
SPOT: dict[str, str] = {
    "force-push": "force push mı?! alo polis? ihbar ediyorum.",
    "push": "PUSH'LANDI!! HADİ BE HADİİİ!!",
    "night-commit": "bu saatte commit mi? bizim zamanımızda UYURDUK.",
    "commit": "her commit bir NFT patron. bunu basıyorum.",
    "reset": "her şey gitti. sonunda huzur.",
    "merge": "bir DÜĞÜN! iki branch, tek aşk. ağlıyorum.",
    "rm": "delil yok ediyorsun. akıllıca. izliyorlar.",
    "install": "daha fazla bağımlılık. kanepeme daha fazla yük.",
}
STAND_IN: dict[str, str] = {
    "force-push": "force push? cesurca. biri çok kızacak.",
    "push": "push'landı! artık dünyada.",
    "night-commit": "bu saatte commit mi? git yat.",
    "commit": "commit'ledin. bak sen, sorumluluk sahibi.",
    "reset": "reset --hard. her şeye rahmet.",
    "merge": "branch'ler birleşiyor. çok güzel.",
    "rm": "rm -rf. umarım bilerek yaptın.",
    "install": "daha fazla paket. node_modules büyüyor.",
}

NAG: dict[str, str] = {
    "Küf":    "ben bile bugün bir kere kalktım. sıra sende. su. hemen.",
    "Pas":    "MOLA ZAMANI!! AYAĞA KALK!! SU İÇ!! HADİ BE!!",
    "Leş":    "iki saattir aralıksız. belkemiğin vasiyet yazıyor. kalk.",
    "Sümük":  "iki saat, mola yok. not edildi. annene söylüyorum.",
    "Kir":    "aslında odak 90 dakikadan sonra düşüyor. 10 dakika mola. bilim.",
    "Çamur":  "kanka... pencereden dışarı bak. gökyüzü seni bekliyor.",
    "Balgam": "*öhö* bizim zamanımızda mola verirdik. kalk evlat.",
    "Bit":    "seni ekrana yapıştırmak istiyorlar. direnin. yürüyüşe çık.",
    "Leke":   "iki saat mi?! canım, solacaksın. su. HEMEN.",
    "Kabuk":  "mola verimliliği %30 artırır. bedava para bu. git.",
    "Snoop":  "yavaşla patron... gerin, su iç, nefes al. kod bir yere gitmiyor.",
}
NAG_FALLBACK = "saatlerdir oturuyorsun. kalk, biraz su iç."

WAITING = "*joint'e bakıyor*"
ROLLING = "*bir tane sarıyor*"
LISTENING = "*dinliyor*"

# Extra keyword -> emote rules for Turkish lines (checked like emotes.LINE_EMOTES)
LINE_EMOTES = [
    (("*horla", "*mırıldan", "*salya", "*döner*"), "sleep"),
    (("*geğir", "*osur"), "burp"),
    (("*kaşı",), "scratch"),
    (("*esner", "gerin"), "stretch"),
    (("*dişini", "*kokla"), "nosepick"),
    (("cips", "pizza", "patates", "yemek yedin", "dondurma"), "eat"),
    (("joint", "sarma", "esrar", "ot ", "yak"), "smoke"),
    (("trip", "renkler", "vay"), "trip"),
    (("gurur", "idare ediyorsun"), "love"),
    (("stack overflow", "tahmin edeyim", "yargılıyorum"), "roast"),
    (("tavsiye", "ctrl+z", "derleniyorsa", "ne iyi gider"), "tip"),
    (("su iç", "annen", "oturuşun", "git yat", "git uyu", "uyku bedava"), "think"),
]
