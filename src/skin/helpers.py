def apply_filters(query, model, is_stattrak, quality, short_slug, collection, phase, rarity, skin_type, min_price, max_price, min_float, max_float):
    if is_stattrak is not None:
        query = query.where(model.is_stattrak == is_stattrak)
    
    if quality:
        query = query.where(model.exterior == quality)
    
    if short_slug:
        query = query.where(model.short_slug == short_slug)
    
    if collection:
        query = query.where(model.collection == collection)

    if phase:
        query = query.where(model.phase == phase)
    
    if rarity:
        query = query.where(model.rarity == rarity)
    
    if skin_type:
        query = query.where(model.skin_type == skin_type)
    
    if min_price is not None:
        query = query.where(model.price >= min_price)
    
    if max_price is not None:
        query = query.where(model.price <= max_price)
    
    if min_float is not None:
        query = query.where(model.float_value >= min_float)
    
    if max_float is not None:
        query = query.where(model.float_value <= max_float)
    
    return query


def apply_sorting(query, model, sort, order):
    if sort == "price":
        if order == "asc":
            query = query.order_by(model.price.asc())
        else:
            query = query.order_by(model.price.desc())
    elif sort == "float":
        if order == "asc":
            query = query.order_by(model.float_value.asc())
        else:
            query = query.order_by(model.float_value.desc())
    
    return query