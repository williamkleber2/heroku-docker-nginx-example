from django.db import connections
from collections import namedtuple
from datetime import datetime
from typing import List, NamedTuple, Dict

def namedtuplefetchall(cursor) -> List[NamedTuple]:
    """ Pega todas as colunas como NamedTuple.
    :param cursor: O cursor da conexão do banco.
    
    :returns: Uma lista de NamedTuple com as colunas. """

    "Return all rows from a cursor as a namedtuple"
    desc = cursor.description
    nt_result = namedtuple('Result', [col[0] for col in desc])
    return [nt_result(*row) for row in cursor.fetchall()]

def dictfetchall(cursor) -> List[Dict]:
    """ Pega todas as colunas como dicionário.
    :param cursor: O cursor da conexão do banco.
    
    :returns: Uma lista de dicionários com as colunas. """

    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

def get_user_shop_orders_by_status(user_shop_id, status, name_filter, start_date, end_date, gmt) -> List[Dict]:
    """ Pega os pedidos do UserShop por status.
    :param user_shop_id: O ID do UserShop.
    :param status: O status para filtrar.
    :param name_filter: O nome do filtro.
    :param start_date: A data de início.
    :param end_date: A data final.
    :param gmt: A hora em GMT.
    
    :returns: Uma lista de dicionários com os pedidos. """

    with connections["replica"].cursor() as cursor:
        cursor.execute("""
        select 
        so.name,
        so.client_name,
        so.client_phone,
        so.cpf,
        COALESCE((select count(*) from shopee_order so2 left join shopee_orderlineitem soli2 on soli2.order_id = so2.id  where so2.parent_order_id = so.id and soli2.status = soli.status group by so2.parent_order_id), 0) otus,
        so.address,
        sus.email,
        so.shopee_checkout_id as shopee_checkout,
        so.value,
        boleto.url,
        boleto.number,
        boleto.due_date,
        so.error,
        so.error_date,
        so.canceled_at,
        so.id as pk,
        so.id,
        so.sync_shopee,
        so.created_date,
        so.state,
        so.city,
        so.neighborhood,
        so.zip_code as cep,
        so.complement,
        so.street,
        so.street_number,
        so.parent_order_id as parent_order,
        so.dropshopee_created_date,
        so.has_child,
        case when sum(case when soli.cancellation_status in ('NC', 'WC') then 1 else 0 end) > 0 then 'NC' else 'C' end cancellation_status,
        soli.status,
        sum(soli.price) price,
        SUM(COALESCE(cast(opli.shopee_order_price as decimal), 0)/100000) shopee_order_price,
        sum(soli.price) + COALESCE((select sum(soli2.price) from shopee_order so2 left join shopee_orderlineitem soli2 on soli2.order_id = so2.id  where so2.parent_order_id = so.id and soli2.status = soli.status group by so2.parent_order_id), 0) price_with_upsell,
        coalesce(sum(opli.shipping_price), 0) shipping_price,
        boleto.value boleto_price
        from shopee_order so
        inner join shopee_usershop suse on suse.id = so.user_shop_id 
        inner join shopee_orderlineitem soli on soli.order_id = so.id   
        left join shopee_usershopee sus on sus.id = so.user_shopee_id
        left join shopee_orderpurchaselineitem opli on opli.order_line_item_id = soli.id 
        left join shopee_orderpurchase sop on sop.shopee_order_id = opli.order_purchase_id 
        left join shopee_boleto boleto on boleto.id = sop.boleto_id_id
        where suse.user_id = %s and soli.status = %s and parent_order_id is null
        and (so.created_date >= %s and so.created_date <= %s)
        and so.name like %s
        group by so.id, sus.email, soli.status, boleto.url, boleto.number, boleto.due_date, boleto.value, boleto.paid
        """, [
            user_shop_id,
            status,
            datetime.strftime(start_date, '%Y-%m-%d 00:00:00.000 ' + gmt),
            datetime.strftime(end_date, '%Y-%m-%d 23:59:59.000 ' + gmt),
            "%" + name_filter + "%",
        ])
        rows = dictfetchall(cursor)

    return rows


def get_child_orders_by_status(order_id, status) -> List[Dict]:
    """ Pega os pedidos filhos por status.
    :param order_id: O ID do pedido.
    :param status: O status para filtrar.
    
    :returns: Uma lista de dicionários com os pedidos. """

    with connections["replica"].cursor() as cursor:
        cursor.execute("""
        select 
        so.name,
        so.client_name,
        so.client_phone,
        so.cpf,
        so.address,
        sus.email,
        so.shopee_checkout_id,
        so.value,
        so.boleto_url,
        so.boleto_number,
        so.boleto_due_date,
        so.error,
        so.error_date,
        so.free_shipping,
        so.canceled_at,
        so.id as pk,
        so.id,
        so.sync_shopee,
        so.created_date,
        so.state,
        so.street,
        so.street_number,
        so.parent_order_id,
        so.has_child,
        soli.status,
        soli.price price
        from shopee_order so
        inner join shopee_usershop suse on suse.id = so.user_shop_id 
        left join shopee_usershopee sus on sus.id = so.user_shopee_id
        left join shopee_orderlineitem soli on soli.order_id = so.id   
        where so.parent_order_id = %s and (%s in (soli.status, '')) and parent_order_id is not null
        """, [order_id, status])
        rows = dictfetchall(cursor)

    return rows


def get_orderlineitem_by_status(order_id, status) -> List[Dict]:
    """ Pega as OLIs por status.
    :param order_id: O ID do pedido.
    :param status: O status para filtrar.
    
    :returns: Uma lista de dicionários com as OLIs. """

    with connections["replica"].cursor() as cursor:
        cursor.execute("""
        SELECT 
sor.name order_name,
sor.error,
max(spi.src) image,
spv.title as variant,
spv.vendor as product_vendor,
soli.id, 
soli.id as pk,
soli.order_id, 
soli.product_variant_id, 
soli.quantity, 
soli."name", 
soli.title, 
soli.product_variant_id_text, 
soli.canceled_at, 
soli.droplinkfy_created_date, 
soli.droplinkfy_deleted_date, 
soli.vendor oli_vendor, 
soli.free_shipping, 
soli.percentage_pay_id, 
soli.price, 
soli.status, 
soli.sync_shopee, 
soli.updated_date_af, 
soli.updated_date_ao, 
soli.updated_date_ap, 
soli.updated_date_aps, 
soli.updated_date_as, 
soli.updated_date_c, 
soli.updated_date_f, 
soli.updated_date_fo, 
soli.user_shopee_id,
soli.error_date,
soli.error,
soli.cancellation_status,
sop.shopee_order_id,
sop.purchase_date,
sop.canceled_status,
sop.tracking_number,
sop.serial_number,
boleto.paid,
boleto.value boleto_price,
boleto.url boleto_url,
boleto.number boleto_number,
boleto.due_date boleto_due_date,
boleto.value boleto_value,
boleto.created_at boleto_created_at,
COALESCE(soli.price, 0) price,
COALESCE(sum(sopli.shipping_price), 0) shipping_price,
COALESCE(cast(sopli.shopee_order_price as decimal), 0)/100000 shopee_order_price,
su.email,
su.vendor
FROM shopee_orderlineitem soli
left join shopee_productvariant spv on spv.id = soli.product_variant_id 
left join shopee_productimage spi on spi.product_shopify_id = spv.product_shopify_id 
left join shopee_order sor on sor.id = soli.order_id 
left join shopee_orderpurchaselineitem sopli on sopli.order_line_item_id = soli.id 
left join shopee_orderpurchase sop on sop.shopee_order_id = sopli.order_purchase_id 
left join shopee_boleto boleto on boleto.id = sop.boleto_id_id
left join shopee_usershopee su on su.id = sopli.user_shopee_id 
where %s in (sor.id, sor.parent_order_id)  and (%s in (soli.status, ''))
group by soli.id, spv.title, soli.status, soli.free_shipping, sor.name, sop.shopee_order_id , sopli.shopee_order_price, su.email, sor.error, su.vendor, boleto.id, spv.vendor
        """, [order_id, status])
        rows = dictfetchall(cursor)

    return rows
