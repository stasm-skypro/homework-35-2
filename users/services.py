import stripe
import requests
from xml.etree import ElementTree
from config.settings import STRIPE_API_KEY

# stripe.api_key = STRIPE_API_KEY


def convert_rub_to_usd(amount_rub):
    """
    Конвертирует рубли в доллары
    :param amount_rub: Сумма в рублях
    :return: Сумма в долларах
    """

    def get_rub_to_usd_rate():
        """
        Получает курс конвертации рубля к доллару
        :return: Курс конвертации рубля РФ к доллару США
        """
        URL = "https://www.cbr.ru/scripts/XML_daily.asp"  # Ссылка на ежедневный курс конвертации рубля по ЦБ РФ
        response = requests.get(URL)
        tree = ElementTree.fromstring(response.content)

        for currency in tree.findall("Valute"):
            char_code = currency.find("CharCode").text
            if char_code == "USD":
                rate = float(currency.find("Value").text.replace(",", "."))
                return rate
        return None  # Если курс конвертации не найден

    rate = get_rub_to_usd_rate()
    return round(float(amount_rub) / rate, 2) if rate else "Ошибка получения курса конвертации"


def create_price(amount):
    """
    Создаёт цену
    :param amount: Цена оплаты
    :return: Объект цены stripe
    """
    stripe.api_key = STRIPE_API_KEY
    price = None
    try:
        price = stripe.Price.create(
            currency="usd",
            unit_amount=int(amount * 100),
            recurring={"interval": "month"},
            product_data={"name": "Gold Plan"},
        )
    except stripe.error.StripeError as e:
        print(e)
    return price


def create_checkout_session(price_id):
    """
    Создаёт сессию оплаты
    :param price_id: ID цены
    :return: Объект сессии stripe
    """
    session = stripe.checkout.Session.create(
        line_items=[
            {
                "price": price_id,
                "quantity": 1,
            }
        ],
        mode="subscription",
        success_url="http://localhost:8000/",
        cancel_url="http://localhost:8000/",
    )
    return session.get("id"), session.get("url")
