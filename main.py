from binance.client import Client
import pandas as pd
import talib

'''
    Pour fonctionner, cet algorithme requière d'être connecté à votre API binance.
    Si vous n'avez pas encore de compte binance passez par le lien :
        https://accounts.binance.com/fr/register?ref=YXRHFGHV
  Celui ci vous offre 10% de commision pour la création du compte.
  
  Créer une API Binance :
  https://www.binance.com/fr/my/settings/api-management
'''
key = 'YourApiKey'
secret = 'YourSecretApiKey'

client = Client(key, secret)

# Champs de saisi utilisateur
symbol_input = str(input("Veuillez entrer la crypto à analyser (ex: FTMUSDT) : ") or "FTMUSDT")
print("Vous voulez surveiller : ",symbol_input)
montant_input = int(input("Combien voulez vous investir (ex: 100) : ") or 100)
print("Vous voulez placer : ",montant_input)
seuil_min = int(input("Quel seuil de sous-achat (ex: 30) : ") or 30)
print("Vous avez placé le seuil de sous-achat à : ",seuil_min)
seuil_max =  int(input("Quel seuil de sur-achat (ex: 70) : ") or 70)
print("Vous avez placé le seuil de sur-achat à : ",seuil_max)
periode =  int(input("Sur une periode en jours (ex: 7): ") or 7)
print("Vous avez choisi une periode de : ",periode," jours")

# Tous les trades 30 minutes par 30 minutes depuis la veille
klines = client.get_historical_klines(symbol_input, Client.KLINE_INTERVAL_30MINUTE, str(periode) + " day ago UTC")
df = pd.DataFrame(klines, columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_av', 'trades', 'tb_base_av', 'tb_quote_av', 'ignore' ])

#Conversion du timestamp en datetime
df = df.set_index(df['timestamp'])
df.index = pd.to_datetime(df.index, unit='ms')
del df['timestamp']

#Nettoyage du dataset
df.drop(df.columns.difference(['open','high','low','close','volume']), 1, inplace=True)

# Initialisation de l'indicateur RSI.
df['RSI'] = talib.RSI(df['close'], timeperiod=14)

lastIndex = df.first_valid_index()
liste_benefs = []

for i in range(7,30):
    frais_binance = 0
    usdt = montant_input
    crypto = 0
    df['RSI'] = talib.RSI(df['close'], timeperiod=i)
    for index, row in df.iterrows():
        if df['RSI'][index] < seuil_min and usdt > 10:
            crypto = usdt / float(df['close'][index]) 
            crypto = crypto - 0.007 * crypto
            usdt = 0
            prix_achat = float(df['close'][index]) 

        elif df['RSI'][index] > seuil_max and crypto > 0.0001:
            usdt = crypto * float(df['close'][index]) 
            frais_binance = 0.007 * usdt
            usdt = usdt - frais_binance 
            crypto = 0
            
    liste_benefs.append(usdt + crypto * float(df['close'].iloc[-1]))   
    lastIndex = index
    
# Récupère la meilleure estimation
max = liste_benefs[0]
for i in range(len(liste_benefs)):
    if liste_benefs[i] > max:
        max = liste_benefs[i]
        
# Impression des résiltats
print()
print("-------- Resultats --------")
print("La meilleure periode pour le RSI est : ", liste_benefs.index(max)+ 7," Avec un benef de : ", max)
print("Pour un seuil min de : ", seuil_min)
print("Et un seuil max de : ", seuil_max)
