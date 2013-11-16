import json
import requests

query = ['The Shawshank Redemption', 'Galaxy Quest', 'Crank', 'Pacific Rim',
         'Gravity', 'Blade Runner', 'Big Trouble in Little China',
         'How to Train Your Dragon', 'Let the Right One In', 'Machete',
         'Pulp Fiction', "Pan's Labyrinth", 'REC', 'Starship Troopers']

r = requests.get('http://criticizer.ngrok.com/reviews',
                 params={'data': json.dumps({'movies': query})})
print r.json()
