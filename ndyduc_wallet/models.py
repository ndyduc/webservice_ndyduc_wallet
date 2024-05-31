from django.db import models
from django.db.models import Q
from django.utils import timezone

# python3 manage.py makemigrations
# python3 manage.py migrate

class User(models.Model):
    ID = models.AutoField(primary_key=True)
    Phone = models.CharField(max_length=20)
    Name = models.CharField(max_length=100)
    Email = models.EmailField(max_length=254)
    Pass = models.CharField(max_length=100)
    Lim = models.IntegerField(null=True)
    FA = models.CharField(max_length=100, null=True) 

    def __str__(self):
        return self.Name

    @staticmethod
    def insert_user(phone, name, email, password, limit, fa):
        try:
            new_user = User(Phone=phone, Name=name, Email=email, Pass=password, Lim=limit, FA=fa)
            new_user.save()
            print('Insert successfully')
        except Exception as e:
            print('Error:', e)

    @staticmethod
    def update_user(id, phone=None, name=None, email=None, password=None, limit=None, fa=None):
        try:
            user = User.objects.get(ID=id)
            if phone is not None:
                user.Phone = phone
            if name is not None:
                user.Name = name
            if email is not None:
                user.Email = email
            if password is not None:
                user.Pass = password
            if limit is not None:
                user.Lim = limit
            if fa is not None:
                user.FA = fa
            user.save()
            return True
        except User.DoesNotExist:
            return False

    @staticmethod
    def delete_user(id):
        try:
            user = User.objects.get(ID=id)
            user.delete()
            return True
        except User.DoesNotExist:
            return False

    @staticmethod
    def getuser(phone):
        user = User.objects.get(Phone=phone)
        user_data = {
                    'id': user.ID,
                    'phone': user.Phone,
                    'name': user.Name,
                    'email': user.Email,
                    'password': user.Pass,
                    'limit': user.Lim,
                    'fa': user.FA
                }
        return user_data

    @staticmethod
    def check_user_exist(phone, email):
        try:
            if User.objects.filter(Q(Phone=phone) & Q(Email=email) & Q(Lim__gt=0)).exists() :
                return True
            else:
                return False  
        except Exception as e:
            return False 

    @staticmethod
    def check_duplicate(phone):
        user = User.objects.filter(Phone=phone)
        if user.exists():
            return user.first().ID
        else:
            return 0

    @staticmethod
    def check_verify(phone, fa):
        try:
            user = User.objects.get(Phone=phone)
            if user.FA == fa:
                return True
            else:
                return False
        except User.DoesNotExist:
            return None

class Inform(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    content = models.CharField(max_length=5000)
    datetime = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"User ID: {self.user.pk}, Content: {self.content}, Datetime: {self.datetime}"

    @classmethod
    def add_notification(cls, user_id, content):
        user = User.objects.get(pk=user_id)
        notification = cls(user=user, content=content)
        notification.save()
        
    def delete_inform(request, id):
        inform = Inform.objedcts.get(Inform, id=id)
        inform.delete()


from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import secrets

class Wallet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    kind = models.CharField(max_length=100)
    public_key = models.CharField(max_length=1000)
    private_key = models.CharField(max_length=5000)
    wallet_id = models.CharField(max_length=100, primary_key=True)

    def __str__(self):
        return f"Wallet for user: {self.user.username}"

    @staticmethod
    def get_wallet_json(phone, kind):
        wallet = Wallet.objects.get(user=User.objects.get(Phone=phone),kind=kind)
        return {
            'user': wallet.user.ID,
            'kind': wallet.kind,
            'public_key': wallet.public_key,
            'private_key': wallet.private_key,
            'wallet_id': wallet.wallet_id
        }

    @classmethod
    def create_wallet(cls, user):
        key = RSA.generate(2048)
        kind = 'ndyduc'
        private_key = key.export_key().decode()
        public_key = key.publickey().export_key().decode()
        wallet_id = ''.join(secrets.choice("0123456789") for _ in range(10))
        wallet = cls(user=user, kind=kind, public_key=public_key, private_key=private_key, wallet_id=wallet_id)
        wallet.save()
        
    @classmethod
    def create_wallet_kraken(cls, user, pub, pri):
        kind = 'kraken'
        private_key = pub
        public_key = pri
        wallet_id = ''.join(secrets.choice("0123456789") for _ in range(10))
        wallet = cls(user=user, kind=kind, public_key=public_key, private_key=private_key, wallet_id=wallet_id)
        wallet.save()

    @classmethod
    def update_wallet(cls, wallet_id,kind=None, new_public_key=None, new_private_key=None):
        wallet = cls.objects.get(wallet_id=wallet_id)
        if kind:
            wallet.kind = kind
        if new_public_key:
            wallet.public_key = new_public_key
        if new_private_key:
            wallet.private_key = new_private_key
        wallet.save()

    @classmethod
    def delete_wallet(cls, wallet_id):
        wallet = cls.objects.get(wallet_id=wallet_id)
        wallet.delete()


class Coins(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    Coin_id = models.AutoField(primary_key=True)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, null=True)
    currency = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=20, decimal_places=10)

    def __str__(self):
        return f"Coins: {self.wallet.wallet_id} - {self.currency}"

    @classmethod
    def add_coin(cls, wallet_id, currency, amount):
        wallet = Wallet.objects.get(wallet_id=wallet_id)
        coin = cls(user=wallet.user, wallet=wallet, currency=currency, amount=amount)
        coin.save()

    @classmethod
    def get_coin(cls, wallet_id, currency, amount):
        try:
            coin = cls.objects.get(wallet__wallet_id=wallet_id, currency=currency)
            coin.amount += amount
            coin.save()
        except cls.DoesNotExist:
            wallet = Wallet.objects.get(wallet_id=wallet_id)
            coin = cls(wallet=wallet, currency=currency, amount=amount)
            coin.save()

    @classmethod
    def give_coin(cls, wallet_id, currency, amount):
        coin = cls.objects.get(wallet__wallet_id=wallet_id, currency=currency)
        coin.amount -= amount
        coin.save()
    
    @classmethod
    def update(cls, wallet_id, currency):
        coin = cls.objects.get(wallet__wallet_id=wallet_id, currency=currency)
        coin.user = Wallet.objects.get(wallet_id=wallet_id).user
        coin.save()
    
    @classmethod
    def update_coin(cls, wallet_id, currency, new_amount):
        coin = cls.objects.get(wallet__wallet_id=wallet_id, currency=currency)
        coin.amount = new_amount
        coin.user = Wallet.objects.get(wallet_id=wallet_id).user
        coin.save()

    @classmethod
    def delete_coin(cls, wallet_id, currency):
        coin = cls.objects.get(wallet__wallet_id=wallet_id, currency=currency)
        coin.delete()


class Template(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    gained_username = models.CharField(max_length=100)
    wallet_id = models.CharField(max_length=100)
    wallet_kind = models.CharField(max_length=20)
    
    def __str__(self):
        return f"User ID: {self.user.id}, Gained username: {self.gained_username}, Wallet ID/Address: {self.wallet_id}"

    @classmethod
    def exists(cls, user,wallet_id, wallet_kind):
        return cls.objects.filter(
            user=user,
            wallet_id=wallet_id,
            wallet_kind=wallet_kind
        ).exists()

    @classmethod
    def add_entry(cls, user, gained_username, wallet_id, wallet_kind):
        try:
            entry = cls(user=user, gained_username=gained_username, wallet_id=wallet_id, wallet_kind=wallet_kind)
            entry.save()
            return True
        except Exception as e:
            print(e)
            return False

    @classmethod
    def update_entry(cls, entry_id, new_gained_username=None, new_wallet_id=None):
        entry = cls.objects.get(id=entry_id)
        if new_gained_username:
            entry.gained_username = new_gained_username
        if new_wallet_id:
            entry.wallet_id = new_wallet_id
        entry.save()

    @classmethod
    def delete_entry(cls, user, id):
        entry = cls.objects.get(user=user, wallet_id=id)
        entry.delete()

from decimal import Decimal

class History(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    datetime = models.DateTimeField(auto_now_add=True)
    flag = models.IntegerField()
    wallet_id = models.CharField(max_length=100)
    amount = models.CharField(max_length=30)
    currency = models.CharField(max_length=10)
    to_id = models.CharField(max_length=100)
    message = models.CharField(max_length=255, blank=True, null=True)
    
    @staticmethod
    def get_history_by_time(history_datetime):
        try:
            history_record = History.objects.get(datetime=history_datetime)
            
            history_data = {
                'id' : history_record.id,
                'user_id': history_record.user.ID if history_record.user else None,
                'datetime': history_record.datetime,
                'flag': history_record.flag,
                'wallet_id': history_record.wallet_id,
                'amount': history_record.amount,
                'currency': history_record.currency,
                'to_id': history_record.to_id,
                'message': history_record.message,
            }
            return history_data
        except History.DoesNotExist:
            return None

    def save(self, *args, **kwargs):
        if self.amount:
            self.amount = str(Decimal(self.amount).normalize())
        super(History, self).save(*args, **kwargs)

    def __str__(self):
        return f"History for {self.user.username} at {self.datetime}"

    @classmethod
    def add_transaction(cls, user, flag, wallet_id, amount, currency, to_id, message=None):
        history = cls(user=user, flag=flag, wallet_id=wallet_id, amount=amount, currency=currency, to_id=to_id, message=message)
        history.save()



########################################################################
from .getlogo import *

def process_token_data(json_data,token):
    if token == "BTCUSD": token="XXBTZUSD"
    result_data = json_data.get("result", {})
    token_data = result_data.get(token, {})  
    logo = map_token_to_name(token)
    logourl = get_logo(map_token_to_sign(token))
    
    token_info = {
        'ask': float(token_data.get("a", [])[0]),
        'bid': float(token_data.get("b", [])[0]),
        'close': float(token_data.get("c", [])[0]),
        'volume': float(token_data.get("v", [])[1]),
        'average_price': float(token_data.get("p", [])[0]),
        'number_of_trades': float(token_data.get("t", [])[0]),
        'low': float(token_data.get("l", [])[1]),
        'high': float(token_data.get("h", [])[1]),
        'open': float(token_data.get("o", 0)),
        'logo': logourl,
        'logo_name': logo
    }
    return token_info

