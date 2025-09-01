# ---------------- Helper ----------------
def serialize_mongo(record):
    if isinstance(record, list):
        return [serialize_mongo(r) for r in record]
    if isinstance(record, dict):
        return {k: serialize_mongo(v) for k, v in record.items()}
    if isinstance(record, ObjectId):
        return str(record)
    return record