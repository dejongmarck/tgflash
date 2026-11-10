TEXT = {
"en": {
"welcome":"<b>Welcome to FlashToken Shop</b>\nChoose an option below.",
"shop":"🛒 Shop","orders":"📦 My orders","account":"👤 Account","language":"🌐 Language","help":"ℹ️ Help",
"choose_product":"Choose a product:","choose_network":"Choose delivery network:","enter_amount":"Enter the amount to purchase:",
"enter_wallet":"Send your receiving wallet address:","confirm":"Please review your order:",
"buy":"✅ Create order","cancel":"Cancel","no_products":"No products were returned by the API.",
"created":"<b>Order created.</b>\nOrder: <code>{id}</code>\nStatus: {status}\n\nPay using the official FlashToken checkout: {url}",
"orders_empty":"You have no orders yet.","account_unavailable":"Account information is temporarily unavailable.",
"markup_note":"Indicative resale quote (+{pct}%): {quote}. <b>This is not the amount charged by FlashToken.</b>",
"help_text":"Choose a product, network, amount and receiving wallet. Payment is handled on FlashToken's official checkout page. Never send funds to an address posted by an unofficial account.",
"choose_language":"Choose your language:"
},
"nl": {
"welcome":"<b>Welkom bij FlashToken Shop</b>\nKies hieronder een optie.",
"shop":"🛒 Producten","orders":"📦 Mijn bestellingen","account":"👤 Account","language":"🌐 Taal","help":"ℹ️ Help",
"choose_product":"Kies een product:","choose_network":"Kies het leveringsnetwerk:","enter_amount":"Voer het gewenste aantal in:",
"enter_wallet":"Stuur je ontvangende walletadres:","confirm":"Controleer je bestelling:",
"buy":"✅ Bestelling aanmaken","cancel":"Annuleren","no_products":"De API heeft geen producten teruggegeven.",
"created":"<b>Bestelling aangemaakt.</b>\nBestelling: <code>{id}</code>\nStatus: {status}\n\nBetaal via de officiële FlashToken-checkout: {url}",
"orders_empty":"Je hebt nog geen bestellingen.","account_unavailable":"Accountinformatie is tijdelijk niet beschikbaar.",
"markup_note":"Indicatieve verkoopprijs (+{pct}%): {quote}. <b>Dit is niet het bedrag dat FlashToken in rekening brengt.</b>",
"help_text":"Kies een product, netwerk, hoeveelheid en ontvangstadres. Betaling verloopt via de officiële FlashToken-betaalpagina. Stuur nooit geld naar een adres van een onofficieel account.",
"choose_language":"Kies je taal:"
},
"fr": {
"welcome":"<b>Bienvenue chez FlashToken Shop</b>\nChoisissez une option.",
"shop":"🛒 Boutique","orders":"📦 Mes commandes","account":"👤 Compte","language":"🌐 Langue","help":"ℹ️ Aide",
"choose_product":"Choisissez un produit :","choose_network":"Choisissez le réseau de réception :","enter_amount":"Saisissez le montant :",
"enter_wallet":"Envoyez votre adresse de portefeuille de réception :","confirm":"Vérifiez votre commande :",
"buy":"✅ Créer la commande","cancel":"Annuler","no_products":"L’API n’a renvoyé aucun produit.",
"created":"<b>Commande créée.</b>\nCommande : <code>{id}</code>\nStatut : {status}\n\nPayez via la page officielle FlashToken : {url}",
"orders_empty":"Vous n’avez pas encore de commandes.","account_unavailable":"Les informations du compte sont temporairement indisponibles.",
"markup_note":"Prix de revente indicatif (+{pct} %) : {quote}. <b>Ce n’est pas le montant facturé par FlashToken.</b>",
"help_text":"Choisissez un produit, un réseau, un montant et une adresse de réception. Le paiement est traité sur la page officielle FlashToken. N’envoyez jamais de fonds à une adresse publiée par un compte non officiel.",
"choose_language":"Choisissez votre langue :"
},
"de": {
"welcome":"<b>Willkommen bei FlashToken Shop</b>\nBitte wähle eine Option.",
"shop":"🛒 Shop","orders":"📦 Meine Bestellungen","account":"👤 Konto","language":"🌐 Sprache","help":"ℹ️ Hilfe",
"choose_product":"Produkt auswählen:","choose_network":"Empfangsnetzwerk auswählen:","enter_amount":"Gewünschte Menge eingeben:",
"enter_wallet":"Sende deine Empfangs-Wallet-Adresse:","confirm":"Bitte überprüfe deine Bestellung:",
"buy":"✅ Bestellung erstellen","cancel":"Abbrechen","no_products":"Die API hat keine Produkte zurückgegeben.",
"created":"<b>Bestellung erstellt.</b>\nBestellung: <code>{id}</code>\nStatus: {status}\n\nZahle über den offiziellen FlashToken-Checkout: {url}",
"orders_empty":"Du hast noch keine Bestellungen.","account_unavailable":"Kontoinformationen sind vorübergehend nicht verfügbar.",
"markup_note":"Unverbindlicher Wiederverkaufspreis (+{pct} %): {quote}. <b>Dies ist nicht der von FlashToken berechnete Betrag.</b>",
"help_text":"Wähle Produkt, Netzwerk, Menge und Empfangsadresse. Die Zahlung erfolgt über die offizielle FlashToken-Seite. Sende niemals Geld an eine Adresse eines inoffiziellen Kontos.",
"choose_language":"Sprache auswählen:"
}}
def t(lang, key, **kwargs):
    lang = lang if lang in TEXT else "en"
    return TEXT[lang].get(key, TEXT["en"].get(key, key)).format(**kwargs)
