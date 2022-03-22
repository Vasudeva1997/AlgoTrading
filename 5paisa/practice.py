from py5paisa import FivePaisaClient
from py5paisa.order import Order, OrderType, Exchange, Bo_co_order
from time import sleep

cred = {
    "APP_NAME": "5P56409084",
    "APP_SOURCE": "9217",
    "USER_ID": "pybeQPEbjju",
    "PASSWORD": "AESDZQGqyAa",
    "USER_KEY": "542GTEZguBbLERUXRZe26rLvfWU2X2KD",
    "ENCRYPTION_KEY": "l8sRTIsjl1JhUrz8X48XQJzKGI4k0gft",
}
client = FivePaisaClient(
    email="vasuappliedai@gmail.com", passwd="Vasudeva@1", dob="19981218", cred=cred
)
client.login()
# 53427


def place_co_bo(order_type, script_code, quantity, price, stop_loss):
    test_order = Bo_co_order(
        script_code,
        quantity,
        price,
        0,
        0,
        order_type,
        "N",
        "D",
        "p",
        stop_loss + 0.5,
        stop_loss,
    )
    return client.bo_order(test_order)


# print(place_co_bo("S", 53427,
#                   25, 750, 750*1.2))
# 669469447(executed, ExchangeOrderID: 1400000058766616), 669505170

# print(order_book)
def wait_for_order_execution(brokerId):
    while_flag = True
    while while_flag:
        order_book = client.order_book()
        for index in range(len(order_book)):
            order = order_book[index]
            if(order["BrokerOrderId"] == brokerId):
                final_order = order
                if(final_order["OrderStatus"] == "Fully Executed"):
                    while_flag = False
                else:
                    sleep(60)
                break
    return final_order


# print(wait_for_order_execution(669505170))
print(wait_for_order_execution(669469447))
