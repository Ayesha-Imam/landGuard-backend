from ..utils.db_utils import get_mongo_collection

def blacklist_token(jti):
    collection = get_mongo_collection("blacklisted_tokens")
    
    # 🔁 Check if already exists
    if collection.find_one({"jti": jti}):
        return  # already blacklisted, do nothing
    
    # ⬇️ If not, insert it
    collection.insert_one({"jti": jti})

def is_token_blacklisted(jti):
    collection = get_mongo_collection("blacklisted_tokens")
    return collection.find_one({"jti": jti}) is not None
