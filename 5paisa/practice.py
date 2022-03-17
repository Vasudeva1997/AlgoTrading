from py5paisa import FivePaisaClient
from py5paisa.order import Order, OrderType, Exchange
cred = {
    "APP_NAME": "5P56409084",
    "APP_SOURCE": "9217",
    "USER_ID": "pybeQPEbjju",
    "PASSWORD": "AESDZQGqyAa",
    "USER_KEY": "542GTEZguBbLERUXRZe26rLvfWU2X2KD",
    "ENCRYPTION_KEY": "R4adCPfgGq8HuTbru8WnpKzzTVHWhvWI",
}
client = FivePaisaClient(
    email="vasuappliedai@gmail.com", passwd="Vasudeva@2", dob="19981218", cred=cred
)
client.login()
print(client.order_request(req_type)())
