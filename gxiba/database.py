import logging

from sqlalchemy import asc, desc

from gxiba.environment import MAPPER_REGISTRY, GXIBA_DATABASE_ENGINE, GXIBA_DATABASE_SESSION




# =====================================================
# ================Interaction Methods==================
# =====================================================

def database_query(database_object, query_filters=None, order_by_parameter=None, order='asc'):
    if query_filters is None:
        query_filters = []
    query = GXIBA_DATABASE_SESSION.query(database_object)
    for query_filter in query_filters:
        query = query.filter(query_filter)
    if order_by_parameter:
        if order.lower() == 'asc':
            query = query.order_by(asc(order_by_parameter))
        elif order.lower() == 'desc':
            query = query.order_by(desc(order_by_parameter))
        else:
            raise NotImplementedError
    for result in query:
        result._in_database = True
        yield result
