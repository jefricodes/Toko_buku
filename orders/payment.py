import midtransclient

from django.conf import settings


class MidtransService:

    @staticmethod
    def get_snap_client():

        return midtransclient.Snap(is_production=(settings.MIDTRANS_IS_PRODUCTION),server_key=(settings.MIDTRANS_SERVER_KEY),
        client_key=(settings.MIDTRANS_CLIENT_KEY),)

    @staticmethod
    def create_transaction(order):

        snap = (MidtransService.get_snap_client())

        parameter = {
            'transaction_details':
            {'order_id': (order.order_number),'gross_amount': int(order.total),},

            'customer_details': 
            {'first_name': (order.full_name),'phone': (order.phone),},
        }

        transaction = (snap.create_transaction(parameter))

        return transaction