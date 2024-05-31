from django.shortcuts import render

from threading import Thread
from django.db import transaction
from decimal import Decimal, ROUND_HALF_UP

import json
import threading
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.http import HttpResponse

from django.db.models import Q
from django.core.serializers import serialize
from .models import *
from .sendemail import *
from .publicapi import *
from .RESTAPIv3 import *

def get_all_users(request):
    all_users = User.objects.all()
    user_list = list(all_users.values())
    
    all_wallets = Wallet.objects.all()
    wallet_list = list(all_wallets.values())
    
    all_coins = Coins.objects.all()
    coins_list = list(all_coins.values())
    
    all_history = History.objects.all()
    history_list = list(all_history.values())
    
    all_inform = Inform.objects.all()
    inform_list = list(all_inform.values())
    
    all_template = Template.objects.all()
    template_list = list(all_template.values())
    
    json_data = { "template": template_list,"history":history_list, "inform":inform_list, "users": user_list, "wallet":wallet_list, "coins":coins_list}
    
    return JsonResponse(json_data, safe=False)

def home(request):
    return HttpResponse("<h1>WTF U want !</h1>")

@csrf_exempt
def check_user(request):
    if request.method == 'POST':
        if request.body:
            data = json.loads(request.body)
            phone = data.get('phone')
            password = data.get('password')
            print("Received phone:", phone)
            print("Received password:", password)
            try:
                User.objects.get(Phone=phone, Pass=password, Lim__gt=0)
                return JsonResponse({'user': User.getuser(phone)})
            except User.DoesNotExist:
                return JsonResponse({'error': 'User not found'})
        else:
            return JsonResponse({'error': 'No data sent'})
    else:
        return JsonResponse({'error': 'Invalid request method'})

@csrf_exempt
def get_infor_home(request):
    if request.method == 'POST':
        if request.body:
            data = json.loads(request.body)
            phone = data.get('phone')
            print(phone)
            if phone is not None:
                try:
                    user = User.getuser(phone)
                    wallet = Wallet.objects.get(user=user["id"],kind='ndyduc')
                    coins = Coins.objects.filter(wallet=wallet.wallet_id)
                    balance=0
                    for coin in coins:
                        key = map_token_to_key(coin.currency)
                        value = float(call_api(key).get("result", {}).get(key, {}) .get("b", [])[0])
                        balance += Decimal(round(float(coin.amount)*value,4))
                        balance = balance.quantize(Decimal('.0001'), rounding=ROUND_HALF_UP)
                    return JsonResponse({'user': user, 'status': wallet.wallet_id, 'symbol': str(balance)})
                except Exception as e:
                    print(e)
            else:
                return JsonResponse({'error': 'No id provided in the request'}, status=400)
        else:
            return JsonResponse({'error': 'No data provided in the request'}, status=400)

@csrf_exempt
def register(request):
    if request.method == 'POST':
        if request.body:
            data = json.loads(request.body)
            uname = data.get('name')
            uphone = data.get('phone')
            uemail = data.get('email')
            upass = data.get('pass')
            lim = -1
            
            check = User.check_user_exist(uphone, uemail)
            if check is True:
                return JsonResponse({'error': 'Already exists'})
            
            fa = send_email(uemail)
            if fa == False:
                return JsonResponse({'false to send email'}, status=400)
            
            checks = User.check_duplicate(uphone)
            if checks != 0 :
                User.update_user(checks, name=uname, email=uemail, password=upass, limit=None, fa=fa)
            else:
                User.insert_user(uphone, uname, uemail, upass, lim, fa)
            
            Inform.add_notification(User.objects.get(Phone=uphone),"Your _ndyduc_ Account has been created at " + str(datetime.now()))
            return JsonResponse({'user': User.getuser(uphone)})
        else:
            return JsonResponse({'false'}, status=400)
    else:
        return JsonResponse({'error': 'No data provided in the request'}, status=400)

@csrf_exempt
def confirm(request):
    if request.method == 'POST':
        if request.body:
            data = json.loads(request.body)
            uphone = data.get('phone')
            ufa = data.get('fa')
            check = User.check_verify(uphone, ufa)
            if check is True:
                user = User.getuser(uphone)
                User.update_user(user['id'], limit=5000, fa=None)
                return JsonResponse({'user': user,
                                    'status': 'Successfully !'})
            else:
                return JsonResponse({'status' : 'Invalid code'})
        else:
            return JsonResponse({'false'}, status=302)
    else:
        return JsonResponse({'error': 'No data provided in the request'}, status=400)

@csrf_exempt
def resend_email(request):
    if request.method == 'POST':
        if request.body:
            data = json.loads(request.body)
            email = data.get('email')
            phone = data.get('phone')
            fa = send_email(email)
            print(email)
            
            if fa == False:
                return JsonResponse({'status' : 'Failed to send email'})
            
            user = User.getuser(phone)
            User.update_user(str(user['id']), fa=fa)
            
            return JsonResponse({'status': 'Resend successfuly !'})
    
@csrf_exempt
def complete_change_email(request):
    if request.method == 'POST':
        if request.body:
            data = json.loads(request.body)
            email = data.get('email')
            phone = data.get('phone')
            
            try: 
                User.update_user(User.objects.get(Phone=phone).ID, email=email)
                Inform.add_notification(User.objects.get(Phone=phone).ID,"_ndyduc_ account's email has been updated at "+str(datetime.now()))
                return JsonResponse({'status': 'successfuly !'}, status=200)
            except Exception as e:
                return JsonResponse({'status': 'False' + str(e)}, status=200)
        else:
            return JsonResponse({'status': 'Not found body !'})
    else:
        return JsonResponse({'error': 'No data provided in the request'}, status=400)

@csrf_exempt
def get_email_by_phone(request):
    if request.method == 'POST':
        if request.body:
            data = json.loads(request.body)
            phone = data.get('phone')
            user = User.getuser(phone)
            fa = send_email(user['email']) 
            User.update_user(user['id'], fa=fa)
            return JsonResponse({'user': user})
        else:
            return JsonResponse({'false'}, status=302)
    else:
        return JsonResponse({'error': 'No data provided in the request'}, status=400)

@csrf_exempt
def forgot_password(request):
    if request.method == 'POST':
        if request.body:
            data = json.loads(request.body)
            phone = data.get('phone')
            newpass = data.get('newpass')
            
            user = User.getuser(phone)
            User.update_user(str(user['id']), password=newpass, fa=None)
            
            Inform.add_notification(user['id'],"Your _ndyduc_ account's password has been changed at" + str(datetime.now()))
            return JsonResponse({'status': 'Change password successfully !'})
        else:
            return JsonResponse({'status': "Don't get the body"})
    else:
        return JsonResponse({'error': 'No data provided in the request'}, status=400)
    
@csrf_exempt
def get_daily_prices(request):
    if request.method == 'POST':
        if request.body:
            data = json.loads(request.body)
            token = data['token']
            tokenjson = call_api(token)
            coin = process_token_data(tokenjson,token)
            return JsonResponse({"token" : coin})
        else:
            return JsonResponse({'status': "Don't get the body"})
    else:
        return JsonResponse({'error': 'No data provided in the request'}, status=400)
    
@csrf_exempt
def get_logo_tokens(request):
    if request.method == 'GET':
        tokens__logo = [{"symbol": "1INCH", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/8104.png"}, {"symbol": "AAVE", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/7278.png"}, {"symbol": "ACA", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/6756.png"}, {"symbol": "ACH", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/6958.png"}, {"symbol": "ADA", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/2010.png"}, {"symbol": "ADX", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/1768.png"}, {"symbol": "AGLD", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/11568.png"}, {"symbol": "AIR", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/12209.png"}, {"symbol": "AKT", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/7431.png"}, {"symbol": "ALCX", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/8613.png"}, {"symbol": "ALGO", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/4030.png"}, {"symbol": "ALICE", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/8766.png"}, {"symbol": "ALPHA", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/7232.png"}, {"symbol": "AMP", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/6945.png"}, {"symbol": "ANKR", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/3783.png"}, {"symbol": "ANT", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/1680.png"}, {"symbol": "APE", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/18876.png"}, {"symbol": "API3", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/7737.png"}, {"symbol": "APT", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/21794.png"}, {"symbol": "ARB", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/11841.png"}, {"symbol": "ARPA", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/4039.png"}, {"symbol": "ASTR", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/12885.png"}, {"symbol": "ATLAS", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/11212.png"}, {"symbol": "ATOM", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/3794.png"}, {"symbol": "AUDIO", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/7455.png"}, {"symbol": "AUD", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/23334.png"}, {"symbol": "AURY", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/11367.png"}, {"symbol": "AVAX", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/5805.png"}, {"symbol": "AXL", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/17799.png"}, {"symbol": "AXS", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/6783.png"}, {"symbol": "BADGER", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/7859.png"}, {"symbol": "BAL", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/5728.png"}, {"symbol": "BAND", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/4679.png"}, {"symbol": "BAT", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/1697.png"}, {"symbol": "BCH", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/1831.png"}, {"symbol": "BEAM", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/28298.png"}, {"symbol": "BICO", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/9543.png"}, {"symbol": "BIT", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/11500.png"}, {"symbol": "BLUR", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/23121.png"}, {"symbol": "BLZ", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/2505.png"}, {"symbol": "BNC", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/8705.png"}, {"symbol": "BNT", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/1727.png"}, {"symbol": "BOBA", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/14556.png"}, {"symbol": "BOND", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/7440.png"}, {"symbol": "BONK", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/23095.png"}, {"symbol": "BOO", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/9608.png"}, {"symbol": "BRICK", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/27615.png"}, {"symbol": "BSX", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/28078.png"}, {"symbol": "BTT", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/16086.png"}, {"symbol": "C98", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/10903.png"}, {"symbol": "CELR", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/3814.png"}, {"symbol": "CFG", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/6748.png"}, {"symbol": "CHR", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/3978.png"}, {"symbol": "CHZ", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/4066.png"}, {"symbol": "CLV", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/8384.png"}, {"symbol": "COMP", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/5692.png"}, {"symbol": "COTI", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/3992.png"}, {"symbol": "CQT", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/7411.png"}, {"symbol": "CRV", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/6538.png"}, {"symbol": "CSM", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/10055.png"}, {"symbol": "CTSI", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/5444.png"}, {"symbol": "CVC", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/1816.png"}, {"symbol": "CVX", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/9903.png"}, {"symbol": "DAI", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/4943.png"}, {"symbol": "DASH", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/131.png"}, {"symbol": "DENT", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/1886.png"}, {"symbol": "DOT", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/6636.png"}, {"symbol": "DYDX", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/28324.png"}, {"symbol": "DYM", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/28932.png"}, {"symbol": "EGLD", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/6892.png"}, {"symbol": "ENJ", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/2130.png"}, {"symbol": "ENS", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/13855.png"}, {"symbol": "EOS", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/1765.png"}, {"symbol": "EQ", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/12468.png"}, {"symbol": "ETC", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/1321.png"}, {"symbol": "ETH", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/1027.png"}, {"symbol": "EUL", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/14280.png"}, {"symbol": "EWT", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/5268.png"}, {"symbol": "FARM", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/6859.png"}, {"symbol": "FET", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/3773.png"}, {"symbol": "FIDA", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/7978.png"}, {"symbol": "FIL", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/2280.png"}, {"symbol": "FIS", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/5882.png"}, {"symbol": "FLOW", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/4558.png"}, {"symbol": "FLR", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/7950.png"}, {"symbol": "FLUX", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/3029.png"}, {"symbol": "FORTH", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/9421.png"}, {"symbol": "FTM", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/3513.png"}, {"symbol": "FXS", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/6953.png"}, {"symbol": "GALA", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/7080.png"}, {"symbol": "GAL", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/11877.png"}, {"symbol": "GARI", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/12969.png"}, {"symbol": "GBP", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/6897.png"}, {"symbol": "GEIST", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/12576.png"}, {"symbol": "GHST", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/7046.png"}, {"symbol": "GLMR", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/6836.png"}, {"symbol": "GMT", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/18069.png"}, {"symbol": "GMX", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/11857.png"}, {"symbol": "GNO", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/1659.png"}, {"symbol": "GNT", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/9533.png"}, {"symbol": "GOO", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/29805.png"}, {"symbol": "GRT", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/6719.png"}, {"symbol": "GST", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/16352.png"}, {"symbol": "GTC", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/10052.png"}, {"symbol": "HDX", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/6753.png"}, {"symbol": "HFT", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/22461.png"}, {"symbol": "HNT", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/5665.png"}, {"symbol": "ICP", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/8916.png"}, {"symbol": "ICX", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/2099.png"}, {"symbol": "IDEX", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/3928.png"}, {"symbol": "IMX", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/10603.png"}, {"symbol": "INJ", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/7226.png"}, {"symbol": "INTR", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/20366.png"}, {"symbol": "JASMY", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/8425.png"}, {"symbol": "JTO", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/28541.png"}, {"symbol": "JUNO", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/14299.png"}, {"symbol": "JUPITER", "url": "https://www.google.com/url?sa=i&url=https%3A%2F%2Fcryptorank.io%2Fprice%2Fjupiter-stattion&psig=AOvVaw0BY0C4MTp7-VECMiDHZhRr&ust=1714552447032000&source=images&cd=vfe&opi=89978449&ved=0CBIQjRxqFwoTCLDApN7D6YUDFQAAAAAdAAAAABAI"}, {"symbol": "KAR", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/10042.png"}, {"symbol": "KAVA", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/4846.png"}, {"symbol": "KEEP", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/5566.png"}, {"symbol": "KEY", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/2398.png"}, {"symbol": "KILT", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/6830.png"}, {"symbol": "KINT", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/13675.png"}, {"symbol": "KIN", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/1993.png"}, {"symbol": "KNC", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/9444.png"}, {"symbol": "KP3R", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/7535.png"}, {"symbol": "KSM", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/5034.png"}, {"symbol": "LCX", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/4950.png"}, {"symbol": "LDO", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/8000.png"}, {"symbol": "LINK", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/1975.png"}, {"symbol": "LMWR", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/24476.png"}, {"symbol": "LOOKS", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/17081.png"}, {"symbol": "LPT", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/3640.png"}, {"symbol": "LRC", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/1934.png"}, {"symbol": "LSK", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/1214.png"}, {"symbol": "LTC", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/2.png"}, {"symbol": "LUNA", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/20314.png"}, {"symbol": "MANA", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/1966.png"}, {"symbol": "MASK", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/8536.png"}, {"symbol": "MATIC", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/3890.png"}, {"symbol": "MC", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/25376.png"}, {"symbol": "MINA", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/8646.png"}, {"symbol": "MIR", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/7857.png"}, {"symbol": "MKR", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/1518.png"}, {"symbol": "XMOON", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/14817.png"}, {"symbol": "MNGO", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/11171.png"}, {"symbol": "MOON", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/7396.png"}, {"symbol": "MOONRIVER", "url": "https://www.google.com/url?sa=i&url=https%3A%2F%2Fcoinmarketcap.com%2Fcurrencies%2Fmoonriver%2F&psig=AOvVaw3_YxDrMHw9DxNDkg4inD6V&ust=1714552287569000&source=images&cd=vfe&opi=89978449&ved=0CBIQjRxqFwoTCPiU65HD6YUDFQAAAAAdAAAAABAE"}, {"symbol": "SOLANA", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/27755.png"}, {"symbol": "MULTI", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/17050.png"}, {"symbol": "MV", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/17704.png"}, {"symbol": "MXC", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/3628.png"}, {"symbol": "NANO", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/24211.png"}, {"symbol": "NEAR", "url": "https://www.google.com/url?sa=i&url=https%3A%2F%2Fcoinlist.co%2Fasset%2FNEAR&psig=AOvVaw18tnLtHChP-dv7Thn82tz9&ust=1714552261685000&source=images&cd=vfe&opi=89978449&ved=0CBIQjRxqFwoTCKCY0oXD6YUDFQAAAAAdAAAAABAJ"}, {"symbol": "NEST", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/5841.png"}, {"symbol": "NMR", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/1732.png"}, {"symbol": "NODLE", "url": "https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.kraken.com%2Fprices%2Fnodle-network&psig=AOvVaw2-Gas47xvy9YCGDnQjD2bq&ust=1714552061937000&source=images&cd=vfe&opi=89978449&ved=0CBIQjRxqFwoTCMjjoKbC6YUDFQAAAAAdAAAAABAZ"}, {"symbol": "NYM", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/17591.png"}, {"symbol": "OCEAN", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/3911.png"}, {"symbol": "OGN", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/5117.png"}, {"symbol": "OMG", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/1808.png"}, {"symbol": "ONDO", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/21159.png"}, {"symbol": "ORCA", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/11165.png"}, {"symbol": "OXT", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/5026.png"}, {"symbol": "OXY", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/8029.png"}, {"symbol": "PAXG", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/4705.png"}, {"symbol": "PEOPLE", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/14806.png"}, {"symbol": "PEPECASH", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/30473.png"}, {"symbol": "PERP", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/6950.png"}, {"symbol": "PHA", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/6841.png"}, {"symbol": "POLIS", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/11213.png"}, {"symbol": "POLKASTARTER", "url": "https://www.google.com/url?sa=i&url=https%3A%2F%2Fcoinmarketcap.com%2Fcurrencies%2Fpolkastarter%2F&psig=AOvVaw3ykF6vxdU9l2aPQPzviccI&ust=1714552016323000&source=images&cd=vfe&opi=89978449&ved=0CBIQjRxqFwoTCKiMy5DC6YUDFQAAAAAdAAAAABAE"}, {"symbol": "POLKAMARKETS", "url": "https://www.google.com/url?sa=i&url=https%3A%2F%2Fcoinmarketcap.com%2Fcurrencies%2Fpolkamarkets%2F&psig=AOvVaw1CFSrGCDzUKzyY8hCCexQx&ust=1714551999887000&source=images&cd=vfe&opi=89978449&ved=0CBIQjRxqFwoTCNDt2ojC6YUDFQAAAAAdAAAAABAE"}, {"symbol": "MARLIN", "url": "https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.coingecko.com%2Fvi%2Fty_gia%2Fmarlin&psig=AOvVaw2lFq9ynv_wMglZ1VfMu1BK&ust=1714551977616000&source=images&cd=vfe&opi=89978449&ved=0CBIQjRxqFwoTCIij6YDC6YUDFQAAAAAdAAAAABAE"}, {"symbol": "POWERLEDGER", "url": "https://www.google.com/url?sa=i&url=https%3A%2F%2Fcoinmarketcap.com%2Fcurrencies%2Fpower-ledger%2F&psig=AOvVaw03CZMJBbw8X1KqizSgvxoH&ust=1714551960250000&source=images&cd=vfe&opi=89978449&ved=0CBIQjRxqFwoTCOiE4PXB6YUDFQAAAAAdAAAAABAE"}, {"symbol": "PERSISTENCE", "url": "https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.coingecko.com%2Fen%2Fcoins%2Fpersistence&psig=AOvVaw3tIAfCNxUP4HOEEJtOyQs1&ust=1714551943277000&source=images&cd=vfe&opi=89978449&ved=0CBIQjRxqFwoTCKim2O3B6YUDFQAAAAAdAAAAABAE"}, {"symbol": "PYTH", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/28177.png"}, {"symbol": "PARTY", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/6556.png"}, {"symbol": "QNT", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/3155.png"}, {"symbol": "QTUM", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/1684.png"}, {"symbol": "RADIUM", "url": "https://www.google.com/url?sa=i&url=https%3A%2F%2Fcoinmarketcap.com%2Fcurrencies%2Fraydium%2F&psig=AOvVaw23H0tq3PLtSX0Mqp9p2E-u&ust=1714551893750000&source=images&cd=vfe&opi=89978449&ved=0CBIQjRxqFwoTCOCUhNbB6YUDFQAAAAAdAAAAABAI"}, {"symbol": "RARE", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/11294.png"}, {"symbol": "RARI", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/5877.png"}, {"symbol": "RAYDIUM", "url": "https://www.google.com/url?sa=i&url=https%3A%2F%2Fcoinmarketcap.com%2Fcurrencies%2Fraydium%2F&psig=AOvVaw23H0tq3PLtSX0Mqp9p2E-u&ust=1714551893750000&source=images&cd=vfe&opi=89978449&ved=0CBIQjRxqFwoTCOCUhNbB6YUDFQAAAAAdAAAAABAI"}, {"symbol": "RUBLIX", "url": "https://www.google.com/url?sa=i&url=https%3A%2F%2Fcoinmarketcap.com%2Fcurrencies%2Frublix%2F&psig=AOvVaw3agZnFEpK9ZbBUzrpGOd4X&ust=1714551876882000&source=images&cd=vfe&opi=89978449&ved=0CBIQjRxqFwoTCMDk983B6YUDFQAAAAAdAAAAABAE"}, {"symbol": "REN", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/2539.png"}, {"symbol": "REPV2", "url": "https://www.google.com/url?sa=i&url=https%3A%2F%2Fcoinmarketcap.com%2Fcurrencies%2Faugur%2F&psig=AOvVaw3VH-mBF5R5NxT3rWKZEQUB&ust=1714551861514000&source=images&cd=vfe&opi=89978449&ved=0CBIQjRxqFwoTCKDz08bB6YUDFQAAAAAdAAAAABAE"}, {"symbol": "REQ", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/2071.png"}, {"symbol": "RLC", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/1637.png"}, {"symbol": "RMRK", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/12140.png"}, {"symbol": "RNDR", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/5690.png"}, {"symbol": "RONS", "url": "https://www.google.com/url?sa=i&url=https%3A%2F%2Fcoinmarketcap.com%2Fcurrencies%2Fronin%2F&psig=AOvVaw2SmGZHiuXRtG5jbmfEZwtY&ust=1714551822525000&source=images&cd=vfe&opi=89978449&ved=0CBIQjRxqFwoTCIDV37TB6YUDFQAAAAAdAAAAABAE"}, {"symbol": "ROOK", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/7678.png"}, {"symbol": "RPL", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/2943.png"}, {"symbol": "RUNE", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/4157.png"}, {"symbol": "SAMO", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/9721.png"}, {"symbol": "SAND", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/6210.png"}, {"symbol": "SABER", "url": "https://www.google.com/url?sa=i&url=https%3A%2F%2Fcoinmarketcap.com%2Fcurrencies%2Fsaber%2F&psig=AOvVaw2-kmv2HdeigYSHCYnQQz0X&ust=1714551805763000&source=images&cd=vfe&opi=89978449&ved=0CBIQjRxqFwoTCLD0lKzB6YUDFQAAAAAdAAAAABAE"}, {"symbol": "SECRET", "url": "https://www.google.com/url?sa=i&url=https%3A%2F%2Fcoinmarketcap.com%2Fcurrencies%2Fsecret%2F&psig=AOvVaw0KNwk36LyIKKfmi23HBYsR&ust=1714551785956000&source=images&cd=vfe&opi=89978449&ved=0CBIQjRxqFwoTCIjjxKTB6YUDFQAAAAAdAAAAABAE"}, {"symbol": "SIACOIN", "url": "https://www.google.com/url?sa=i&url=https%3A%2F%2Fcoinmarketcap.com%2Fcurrencies%2Fsiacoin%2F&psig=AOvVaw2jjbM_j77C5RvmjHVhbuaL&ust=1714551768213000&source=images&cd=vfe&opi=89978449&ved=0CBIQjRxqFwoTCKjUnprB6YUDFQAAAAAdAAAAABAE"}, {"symbol": "SHIDEN", "url": "https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.coingecko.com%2Fen%2Fcoins%2Fshiden-network&psig=AOvVaw3efJfiSVNX7lbRuez5PBAE&ust=1714551733212000&source=images&cd=vfe&opi=89978449&ved=0CBIQjRxqFwoTCIi3-onB6YUDFQAAAAAdAAAAABAR"}, {"symbol": "SEI", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/23149.png"}, {"symbol": "SOGUR", "url": "https://www.google.com/url?sa=i&url=https%3A%2F%2Fcoinmarketcap.com%2Fcurrencies%2Fsogur%2F&psig=AOvVaw3BGekzAXLRi11MaSa5YuJZ&ust=1714551699012000&source=images&cd=vfe&opi=89978449&ved=0CBIQjRxqFwoTCKjKrvrA6YUDFQAAAAAdAAAAABAE"}, {"symbol": "SHIBA", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/14341.png"}, {"symbol": "SLP", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/5824.png"}, {"symbol": "SNX", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/2586.png"}, {"symbol": "SOL", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/5426.png"}, {"symbol": "SPELL", "url": "https://www.google.com/url?sa=i&url=https%3A%2F%2Fcoinmarketcap.com%2Fcurrencies%2Fspell-token%2F&psig=AOvVaw2gn47QEq9H2tpZI9PRyFlF&ust=1714551668031000&source=images&cd=vfe&opi=89978449&ved=0CBIQjRxqFwoTCIDO7-rA6YUDFQAAAAAdAAAAABAE"}, {"symbol": "SRM", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/6187.png"}, {"symbol": "SSV", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/12999.png"}, {"symbol": "STEP", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/9443.png"}, {"symbol": "STG", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/18934.png"}, {"symbol": "STORJ", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/1772.png"}, {"symbol": "STRK", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/22691.png"}, {"symbol": "STRONG", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/6511.png"}, {"symbol": "STX", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/4847.png"}, {"symbol": "SUSHI", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/6758.png"}, {"symbol": "SUPER", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/8290.png"}, {"symbol": "SXP", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/4279.png"}, {"symbol": "SYN", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/12147.png"}, {"symbol": "TBTC", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/26133.png"}, {"symbol": "TEER", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/13323.png"}, {"symbol": "TIA", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/22861.png"}, {"symbol": "TLM", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/9119.png"}, {"symbol": "TON", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/11419.png"}, {"symbol": "TRB", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/4944.png"}, {"symbol": "TRU", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/7725.png"}, {"symbol": "TRX", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/1958.png"}, {"symbol": "TUSD", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/2563.png"}, {"symbol": "TVK", "url": "https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.coingecko.com%2Fen%2Fcoins%2Fvirtua&psig=AOvVaw3udIL0rwKs-QGHKIgGKFMb&ust=1714551535580000&source=images&cd=vfe&opi=89978449&ved=0CBIQjRxqFwoTCIinzKvA6YUDFQAAAAAdAAAAABAQ"}, {"symbol": "UMA", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/5617.png"}, {"symbol": "UNFI", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/7672.png"}, {"symbol": "UNI", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/7083.png"}, {"symbol": "USD", "url": "https://www.google.com/url?sa=i&url=https%3A%2F%2Fcoinmarketcap.com%2Fcurrencies%2Fusd-coin%2F&psig=AOvVaw2eMk4kvlirO3ZUAdhbtlRW&ust=1714551596476000&source=images&cd=vfe&opi=89978449&ved=0CBIQjRxqFwoTCPi2qcjA6YUDFQAAAAAdAAAAABAE"}, {"symbol": "UST", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/3100.png"}, {"symbol": "WAVES", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/1274.png"}, {"symbol": "WAXL", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/28322.png"}, {"symbol": "WAX", "url": "https://www.google.com/url?sa=i&url=https%3A%2F%2Fcoinmarketcap.com%2Fcurrencies%2Fwax%2F&psig=AOvVaw1Czt0FmuSvwiK-RmMqumMf&ust=1714551616147000&source=images&cd=vfe&opi=89978449&ved=0CBIQjRxqFwoTCLCPndPA6YUDFQAAAAAdAAAAABAE"}, {"symbol": "WBTC", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/3717.png"}, {"symbol": "WIF", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/28752.png"}, {"symbol": "WNXM", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/5939.png"}, {"symbol": "WOO", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/7501.png"}, {"symbol": "WUSD", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/29318.png"}, {"symbol": "XBT", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/4813.png"}, {"symbol": "BTC", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/1.png"}, {"symbol": "XCN", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/18679.png"}, {"symbol": "XDG", "url": "https://www.google.com/url?sa=i&url=https%3A%2F%2Fcoinmarketcap.com%2Fcurrencies%2Fdecentral-games-governance-xdg%2F&psig=AOvVaw0XJHRD2riojFaWuXMH06xJ&ust=1714551643167000&source=images&cd=vfe&opi=89978449&ved=0CBIQjRxqFwoTCKDLy97A6YUDFQAAAAAdAAAAABAE"}, {"symbol": "XLM", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/512.png"}, {"symbol": "XMR", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/328.png"}, {"symbol": "XOR", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/5802.png"}, {"symbol": "XRP", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/52.png"}, {"symbol": "XRT", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/4757.png"}, {"symbol": "XTZ", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/2011.png"}, {"symbol": "YFI", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/5864.png"}, {"symbol": "YGG", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/10688.png"}, {"symbol": "ZEC", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/1437.png"}, {"symbol": "ZRX", "url": "https://s2.coinmarketcap.com/static/img/coins/64x64/1896.png"}]
        return JsonResponse(tokens__logo, safe=False)
    else:
        return JsonResponse({'error': 'It not method GET'}, status=400)
    
@csrf_exempt
def get_full_symbol(request):
    if request.method == 'POST':
        if request.body :
            data = json.loads(request.body)
            symbol = data['symbol']
            key = map_token_to_key(symbol)
            return JsonResponse({"symbol": key})
        else:
            return JsonResponse({'status': "Don't get the body"})
    else:
        return JsonResponse({'error': 'No data provided in the request'}, status=400)
    
@csrf_exempt
def add_kraken(request):
    if request.method == 'POST':
        if request.body:
            data = json.loads(request.body)
            phone = data['phone']
            pub = data['pub']
            pri = data['pri']
            try:
                api = cfApiMethods(apiPath="https://demo-futures.kraken.com",
                                    apiPublicKey=pub, apiPrivateKey=pri)
                data=json.loads(api.get_accounts())
                result = data["result"]
                if result == "success":
                    try:
                        Wallet.create_wallet_kraken(User.objects.get(Phone=phone),pub,pri)
                        balances = {}
                        for account_name, account_data in data["accounts"].items():
                            if account_name.startswith("fi_") or account_name.startswith("fv_"):
                                for currency, balance in account_data["balances"].items():
                                    if currency in balances:
                                        balances[currency] += balance
                                    else:
                                        balances[currency] = balance
                                        
                        for currency, amount in balances.items():
                            users = User.getuser(phone)
                            wallet = Wallet.objects.get(user=users['id'], kind='kraken')
                            Coins.get_coin(wallet_id=wallet.wallet_id, currency=currency.upper(), amount=amount)
                            Coins.update(wallet_id=wallet.wallet_id, currency=currency)
                            
                        content = 'Your account has been add Kraken wallet at '+ str(datetime.now())
                        Inform.add_notification(User.objects.get(Phone=phone).ID, content)
                    except Exception as e:
                        print(e)
                        return JsonResponse({"status": "failure"})
                return JsonResponse({"status": result})
            except Exception as e:
                print(e)
                return JsonResponse({"status": "failure"})
        else:
            return JsonResponse({'status': "failure"})
    else:
        return JsonResponse({'error': 'No data provided in the request'}, status=400)

@csrf_exempt
def get_own_tokens(request):
    if request.method == 'POST':
        if request.body :
            data = json.loads(request.body)
            phone = data['phone']
            kind = data['kind']
            try:
                users = User.getuser(phone)
                wallet = Wallet.objects.get(user=users['id'], kind=kind)
                coins = Coins.objects.filter(wallet=wallet.wallet_id)
                tokens_list = []
                for coin in coins:
                    if coin.currency == "XBT": coin.currency = "BTC"
                    token_info = {"currency": coin.currency, "amount": float(coin.amount)}
                    
                    token_logo = get_logo(coin.currency)
                    token_info["logo"] = token_logo
                    tokens_list.append(token_info)
                return JsonResponse(tokens_list, safe=False)
            except Exception as e:
                print(e)
        else:
            return JsonResponse({'status': "Don't get the body"})
    else:
        return JsonResponse({'error': 'No data provided in the request'}, status=400)
    
@csrf_exempt
def check_getter(request):
    if request.method == 'POST':
        if request.body :
            data = json.loads(request.body)
            wid = data['towallet']
            try:
                wallet = Wallet.objects.get(wallet_id=wid)
                user_name = wallet.user.Name
                return JsonResponse({"status": user_name})
            except Exception as e:
                print(e)
                return JsonResponse({"status": "Can't find beneficiary wallet !"})
        else:
            return JsonResponse({'status': "Don't get the body"})
    else:
        return JsonResponse({'error': 'No data provided in the request'}, status=400)
    
import logging

# Cấu hình logging
logging.basicConfig(level=logging.INFO)
# Khóa để đồng bộ hóa truy cập vào các ví tiền
# lock = threading.Lock()

@csrf_exempt
def complete_transfer(request):
    if request.method == 'POST':
        if request.body:
            data = json.loads(request.body)
            phone = data['phone']
            kind = data['kind']
            currency = data['currency']
            towallet = data['towallet']
            amount = data['amount']
            message = data['message']
            
            if currency == 'BTC': currency='XBT'
            
            try:
                wallet1 = Wallet.objects.get(user=User.objects.get(Phone=phone), kind=kind)
                wallet2 = Wallet.objects.get(wallet_id=towallet)
                if wallet1.user.ID == wallet2.user.ID:
                    flag = 0
                else:
                    flag = 1
                
                def give_coin_operation():
                    try:
                        logging.info("Starting give_coin_operation for wallet1: %s", wallet1.wallet_id)
                        Coins.give_coin(wallet1.wallet_id, currency, Decimal(amount))
                    except Exception as e:
                        logging.error(str(e))
                        return False

                def get_coin_operation():
                    try:
                        logging.info("Starting get_coin_operation for wallet2: %s", wallet2.wallet_id)
                        Coins.get_coin(wallet2.wallet_id, currency, Decimal(amount))
                    except Exception as e:
                        logging.error(str(e))
                        return False

                # Thực hiện các hoạt động giao dịch trong một giao dịch nguyên tử
                try:
                    with transaction.atomic():
                        t1 = threading.Thread(target=give_coin_operation)
                        t2 = threading.Thread(target=get_coin_operation)
                        t1.start()
                        t2.start()
                        t1.join()
                        t2.join()
                        
                        History.add_transaction(User.objects.get(Phone=phone), flag, wallet1.wallet_id, amount, currency, wallet2.wallet_id, message)
                        
                        content = 'Account ' + kind + ' ' + wallet1.wallet_id + ' -' + amount + ' ' + ('BTC' if currency == 'XBT' else currency) + ' at ' + str(timezone.now()) + '. ' + message + ' .'

                        print(content)
                        Inform.add_notification(User.objects.get(Phone=phone).ID, content)
                        
                        user2 = Wallet.objects.get(wallet_id=towallet).user.ID
                        infor = 'Account ' + Wallet.objects.get(wallet_id=towallet).kind + ' ' + towallet + ' +' + amount + ' ' + ('BTC' if currency == 'XBT' else currency)+ ' from '+ User.objects.get(Phone=phone).Name + ' at ' + str(timezone.now()) + '. ' + message + ' .'

                        Inform.add_notification(user2, infor)
                        logging.info("Transaction completed successfully")
                        return JsonResponse({"status": "success"})
                except Exception as e:
                    return JsonResponse({"status": "failure", "error": str(e)})
            except Exception as e:
                logging.error("Error occurred during transaction: %s", str(e))
                return JsonResponse({"status": "failure", "message": str(e)})
        else:
            return JsonResponse({'status': "failure", "error": "No data provided in the request body"})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)

@csrf_exempt
def get_bill(request):
    if request.method == 'POST':
        if request.body:
            data = json.loads(request.body)
            phone = data['phone']
            
            try:
                latest_history = History.objects.filter(user=User.objects.get(Phone=phone), flag=1).order_by('-datetime').first()
                if latest_history:
                    history = History.get_history_by_time(latest_history.datetime)
                    wallet = Wallet.objects.get(wallet_id=history['to_id'])
                    infor = Inform.objects.filter(user=wallet.user).order_by('-datetime').first()
                    return JsonResponse({"user": User.getuser(wallet.user.Phone), "status": get_logo(history['currency']), "history": history, "symbol": infor.content})
                else:
                    return JsonResponse({"status": "failure", "message": "No history found for this user"})
            except Exception as e:
                return JsonResponse({"status": "failure", "message": str(e)})
        else:
            return JsonResponse({'status': "failure", "error": "No data provided in the request body"})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)

@csrf_exempt
def save_template(request):
    if request.method == 'POST':
        if request.body:
            data = json.loads(request.body)
            phone = data['phone']
            walletid = data['walletid']
            wallet = Wallet.objects.get(wallet_id=walletid)
            print(User.objects.get(Phone=phone).ID, wallet.wallet_id, wallet.kind)
            try:
                Template.objects.get(user=User.objects.get(Phone=phone), wallet_id=walletid, wallet_kind=wallet.kind)
                return JsonResponse({'status': "exist", "error": "this template already exists !"})
            except Exception as e:
                print(str(e))
                if Template.add_entry(User.objects.get(Phone=phone), wallet.user.Name, wallet.wallet_id, wallet.kind):
                    return JsonResponse({"status": "success"})
                else: return JsonResponse({"status": "failure"})
        else:
            return JsonResponse({'status': "failure", "error": "No data provided in the request body"})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)

@csrf_exempt
def check_exchange(request):
    if request.method == 'POST':
        if request.body:
            data = json.loads(request.body)
            phone = data['phone']
            fromkind = data['fromkind']
            tokind = data['tokind']
            
            try: 
                wallet1 = Wallet.get_wallet_json(phone, kind=fromkind)
                wallet2 = Wallet.get_wallet_json(phone, kind=tokind)
                return JsonResponse([wallet1, wallet2], safe=False)
            except Exception as e:
                return JsonResponse({"status": str(e)}, status=400)
        else:
            return JsonResponse({"status": "failure", "error": "No data provided in the request body"}, status=400)
    else:
        return JsonResponse({"error": "Invalid request method"}, status=400)

@csrf_exempt
def complete_exchange(request):
    if request.method == 'POST':
        if request.body:
            data = json.loads(request.body)
            phone = data['phone']
            fromk = data['from']
            to = data['to']
            currency = data['currency']
            amount = data['amount']
            password = data['password']
            
            try:
                User.objects.get(Phone=phone, Pass=password, Lim__gt=0)
                
                if currency == 'BTC': currency='XBT'
                
                try:
                    wallet1 = Wallet.objects.get(user=User.objects.get(Phone=phone), kind=fromk)
                    wallet2 = Wallet.objects.get(user=User.objects.get(Phone=phone), kind=to)
                    flag = 0
                    
                    def give_coin_operation():
                        try:
                            logging.info("Starting give_coin_operation for wallet1: %s", wallet1.wallet_id)
                            Coins.give_coin(wallet1.wallet_id, currency, Decimal(amount))
                        except Exception as e:
                            logging.error(str(e))
                            return False

                    def get_coin_operation():
                        try:
                            logging.info("Starting get_coin_operation for wallet2: %s", wallet2.wallet_id)
                            Coins.get_coin(wallet2.wallet_id, currency, Decimal(amount))
                        except Exception as e:
                            logging.error(str(e))
                            return False

                    # Thực hiện các hoạt động giao dịch trong một giao dịch nguyên tử
                    try:
                        with transaction.atomic():
                            t1 = threading.Thread(target=give_coin_operation)
                            t2 = threading.Thread(target=get_coin_operation)
                            t1.start()
                            t2.start()
                            t1.join()
                            t2.join()
                            
                            History.add_transaction(User.objects.get(Phone=phone), flag, wallet1.wallet_id, amount, currency, wallet2.wallet_id, message= None)
                            
                            content = 'Account exchange ' + amount + ' ' + ('BTC' if currency == 'XBT' else currency) + ' from ' + wallet1.wallet_id +' '+ fromk + ' to '+wallet2.wallet_id+' '+ to  + ' at ' + str(timezone.now()) +' .'

                            print(content)
                            Inform.add_notification(User.objects.get(Phone=phone).ID, content)
                            logging.info("Exchange completed successfully")
                            return JsonResponse({"status": "success"})
                    except Exception as e:
                        return JsonResponse({"status": "failure", "error": str(e)})
                except Exception as e:
                    logging.error("Error occurred during transaction: %s", str(e))
                    return JsonResponse({"status": "failure", "error": str(e)})
            except User.DoesNotExist:
                return JsonResponse({'status': 'failure','error': 'Incorrect password !'})
        else:
            return JsonResponse({'status': "failure", "error": "No data provided in the request body"})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
@csrf_exempt
def get_coins(request):
    if request.method == 'POST':
        if request.body:
            data = json.loads(request.body)
            phone = data.get('phone')
            kind  = data.get('kind')
            
            try:
                user = User.objects.get(Phone=phone)
                wallets = Wallet.objects.filter(user=user, kind=kind)
                coins = Coins.objects.filter(wallet__in=wallets)
                coins_list = list(coins.values())
                
                for coin in coins_list:
                    try:
                        token = 'BTC' if coin['currency'] == 'XBT' else coin['currency']
                        tokenus = map_token_to_key(token)
                        data = process_token_data(call_api(tokenus),tokenus)
                        name = data['logo_name']
                        now = data['bid'] * float(coin['amount'])
                        percent = round(((data['ask'] - data['open']) * 100) / data['open'], 2)
                        
                        coin['amount'] = round(float(coin['amount']), 10)
                        coin['name'] = name
                        coin['now'] = round(now,4)
                        coin['percent'] = ('+' if data['ask']>=data['open'] else '') + str(percent)+'%'
                        coin['logo'] = get_logo(coin['currency'])
                    except Exception as e:
                        print(str(e))
                return JsonResponse(coins_list, safe=False)
            except Exception as e:
                return JsonResponse({"status": "failure", "error": str(e)}, status=400)
        else:
            return JsonResponse({"status": "failure", "error": "No data provided in the request body"}, status=400)
    else:
        return JsonResponse({"status": "failure", "error": "Invalid request method"}, status=400)
    
@csrf_exempt
def get_wallets(request):
    if request.method =='POST':
        if request.body:
            data = json.loads(request.body)
            phone = data.get('phone')

            try:
                user = User.objects.get(Phone=phone)
                wallets = Wallet.objects.filter(user=user)
                wallets_list = list(wallets.values())

                return JsonResponse(wallets_list, safe=False)
            except Exception as e:
                return JsonResponse({"status": "failure", "error": str(e)}, status=400)
        else:
            return JsonResponse({"status": "failure", "error": "No data provided in the request body"}, status=400)
    else:
        return JsonResponse({"status": "failure", "error": "Invalid request method"}, status=400)
    
@csrf_exempt
def get_infor(request):
    if request.method == 'POST':
        if request.body:
            data = json.loads(request.body)
            phone = data.get('phone')

            try:
                user = User.objects.get(Phone=phone)
                informs = Inform.objects.filter(user=user).order_by('-datetime')
                informs_list = list(informs.values())

                return JsonResponse(informs_list, safe=False)
            except Exception as e:
                return JsonResponse({"status": "failure", "error": str(e)}, status=400)
        else:
            return JsonResponse({"status": "failure", "error": "No data provided in the request body"}, status=400)
    else:
        return JsonResponse({"status": "failure", "error": "Invalid request method"}, status=400)

@csrf_exempt
def get_history(request):
    if request.method == 'POST':
        if request.body:
            data = json.loads(request.body)
            phone = data.get('phone')
            print(phone+'abc')

            try:
                user = User.objects.get(Phone=phone)
                historys = History.objects.filter(user=user).order_by('-datetime')
                
                List_history = []
                for history in historys:
                    try:
                        wallet = Wallet.objects.get(wallet_id=history.wallet_id)
                        kind = wallet.kind
                    except Wallet.DoesNotExist:
                        kind = ''
                    name = user.Name
                    
                    content = 'Account ' + ('_ndyduc_' if kind == 'ndyduc' else 'Kraken') + (' transfer ' if history.flag == 0 else ' exchange ') + str(history.amount) + ' ' + ('BTC' if history.currency == 'XBT' else history.currency) + ' to ' + history.to_id + ' ' + name + ' at ' + history.datetime.strftime('%Y-%m-%d %H:%M:%S') + '. ' + (history.message + '.' if history.message else '')

                    json_item = {
                        'content': content,
                        'datetime': history.datetime.strftime('%Y-%m-%d %H:%M:%S'),
                        'flag': history.flag
                    }

                    List_history.append(json_item)

                return JsonResponse(List_history, safe=False)
            except User.DoesNotExist:
                return JsonResponse({"status": "failure", "error": "User not found"}, status=400)
            except Wallet.DoesNotExist:
                return JsonResponse({"status": "failure", "error": "Wallet not found"}, status=400)
            except Exception as e:
                return JsonResponse({"status": "failure", "error": str(e)}, status=500)
        else:
            return JsonResponse({"status": "failure", "error": "No data provided in the request body"}, status=400)
    else:
        return JsonResponse({"status": "failure", "error": "Invalid request method"}, status=400)
    
@csrf_exempt
def get_network(request):
    if request.method == 'POST':
        if request.body:
            data = json.loads(request.body)
            phone = data.get('phone')

            try:
                user = User.objects.get(Phone=phone)
                wallets = Wallet.objects.filter(user=user)
                wallets_list = list(wallets.values())

                return JsonResponse(wallets_list, safe=False)
            except Exception as e:
                return JsonResponse({"status": "failure", "error": str(e)}, status=400)
        else:
            return JsonResponse({"status": "failure", "error": "No data provided in the request body"}, status=400)
    else:
        return JsonResponse({"status": "failure", "error": "Invalid request method"}, status=400)

@csrf_exempt
def remove_wallet(request):
    if request.method == 'POST':
        if request.body:
            data = json.loads(request.body)
            phone = data.get('phone')
            kind = data.get('kind')

            try:
                user = User.objects.get(Phone=phone)
                wallet = Wallet.objects.get(user=user, kind=kind)
                Wallet.delete_wallet(wallet.wallet_id)
                Inform.add_notification(user.ID,"Your account "+kind+" has been removed.")
                return JsonResponse({"status": "success"})
            except Exception as e:
                return JsonResponse({"status": "failure", "error": str(e)}, status=400)
        else:
            return JsonResponse({"status": "failure", "error": "No data provided in the request body"}, status=400)
    else:
        return JsonResponse({"status": "failure", "error": "Invalid request method"}, status=400)
    
@csrf_exempt
def get_template(request):
    if request.method == 'POST':
        if request.body:
            data = json.loads(request.body)
            phone = data.get('phone')

            try:
                user = User.objects.get(Phone=phone)
                templates = Template.objects.filter(user=user)
                templates_list = list(templates.values())

                return JsonResponse(templates_list, safe=False)
            except Exception as e:
                return JsonResponse({"status": "failure", "error": str(e)}, status=400)
        else:
            return JsonResponse({"status": "failure", "error": "No data provided in the request body"}, status=400)
    else:
        return JsonResponse({"status": "failure", "error": "Invalid request method"}, status=400)

@csrf_exempt
def remove_template(request):
    if request.method == 'POST':
        if request.body:
            data = json.loads(request.body)
            phone = data.get('phone')
            walletid = data.get('walletid')

            try:
                user = User.objects.get(Phone=phone)
                Template.delete_entry(user,walletid)
                Inform.add_notification(user.ID,"Your template "+walletid+" has been removed.")
                return JsonResponse({"status": "success"})
            except Exception as e:
                return JsonResponse({"status": "failure", "error": str(e)}, status=400)
        else:
            return JsonResponse({"status": "failure", "error": "No data provided in the request body"}, status=400)
    else:
        return JsonResponse({"status": "failure", "error": "Invalid request method"}, status=400)
    