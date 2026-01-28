# from unittest.mock import sentinel
import joblib
import re
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# ==============================
# Conversation State (GLOBAL)
# ==============================
conversation_state = {
    "active": True,
    "turns": 0,
    "sentiment": None,
    "negative_count": 0,
    "awaiting_order_id": False,
    "awaiting_item_selection": False,
    "awaiting_action": False,
    "order_id": None,
    "product_name": None,
    "selected_item": None,
    "order_status_request": False,

   
}



PRODUCT_DATABASE = {
    "shirt": {"price": 799, "stock": 12, "category": "Clothing", "material": "Cotton", "warranty": "No warranty"},
    "shoes": {"price": 2499, "stock": 0, "category": "Footwear", "material": "Synthetic", "warranty": "6 months"},
    "dress": {"price": 1899, "stock": 5, "category": "Clothing", "material": "Rayon", "warranty": "No warranty"},
    "iphone": {"price": 69999, "stock": 3, "category": "Electronics", "material": "Aluminum and Glass", "warranty": "1 year"},
    "laptop": {"price": 55999, "stock": 7, "category": "Electronics", "material": "Aluminum", "warranty": "1 year"}
}


DUMMY_ORDER_ITEMS = {
    "ORD12345": ["shirt", "shoes"],
    "ORD67890": ["dress"],
    "ORDER12345": ["laptop"],
    "ORDER67890": ["iphone", "shirt"],
    "default": ["shirt", "dress", "shoes"]
}


ORDER_STATUS_DB = {
    "ORD12345": "📦 Your order is **Out for Delivery** and will arrive today.",
    "ORD67890": "🚚 Your order is **In Transit** and will arrive in 2 days.",
    "ORDER12345": "✅ Your order has been **Delivered successfully**.",
    "ORDER67890": "⏳ Your order is **Processing** and will be shipped soon.",
    "default": "📦 Your order is being processed. Please check again later."
}


sentiment_model = joblib.load("models/sentiment_model.pkl")
sent_vectorizer = joblib.load("models/tfidf_vectorizer.pkl")

intent_model = joblib.load("models/intent_model.pkl")
intent_vectorizer = joblib.load("models/intent_vectorizer.pkl")

# ==============================
# NLP Preprocessing
# ==============================
stop_words = set(stopwords.words("english"))
stop_words.discard("not")
stop_words.discard("no")
stop_words.discard("nor")

lemmatizer = WordNetLemmatizer()
ORDER_ID_PATTERN = r"(ord\d+|order\d+|\b\d{5,}\b)"

def clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-zA-Z0-9]", " ", text)
    words = text.split()
    words = [lemmatizer.lemmatize(w) for w in words if w not in stop_words]
    return " ".join(words)




# ==============================
# MAIN CHAT 
# ==============================
def process_customer_query(query: str):
    global conversation_state

    query_lower = query.lower()
    cleaned = clean_text(query)


    

    if not conversation_state["active"]:
        return {"response": "This conversation has ended. Please refresh the page to start a new chat."}

    conversation_state["turns"] += 1

    # ==============================
    # ORDER STATUS INTENT
    # ==============================
    if any(w in query_lower for w in ["order status", "track my order", "track order", "where is my order", "order tracking"]):
        conversation_state["awaiting_order_id"] = True
        conversation_state["order_status_request"] = True
        return {
            "intent": "order_status",
            "response": "📦 Sure! Please share your **Order ID** to track your order."
        }

    # ==============================
    # RETURN / REFUND INTENT
    # ==============================
    if (any(w in query_lower for w in ["refund", "return", "replace"])
        and not conversation_state["awaiting_item_selection"]
        and not conversation_state["awaiting_action"]):
        conversation_state["awaiting_order_id"] = True
        return {
            "intent": "refund_or_return",
            "response": (
                "I’m sorry to hear that 😔.\n"
                "I have raised a complaint for you.\n\n"
                "Please share your **Order ID** so I can help you with the return or refund."
                
            )
        }

    # ==============================
    # Order ID Handling
    # ==============================
    if conversation_state["awaiting_order_id"]:
        match = re.search(ORDER_ID_PATTERN, query_lower)
        if match:
            order_id = match.group().upper()
            conversation_state["order_id"] = order_id
            conversation_state["awaiting_order_id"] = False

            if conversation_state["order_status_request"]:
                conversation_state["order_status_request"] = False
                conversation_state["awaiting_item_selection"] = False
                conversation_state["awaiting_action"] = False

                status = ORDER_STATUS_DB.get(order_id, ORDER_STATUS_DB["default"])
                return {
                    "intent": "order_status_result",
                    "response": f"**Order ID: {order_id}**\n\n{status}"
                }

            conversation_state["awaiting_item_selection"] = True
            items = DUMMY_ORDER_ITEMS.get(order_id, DUMMY_ORDER_ITEMS["default"])
            # item_list = "\n".join([f"• {item.title()}" for item in items])
            # item_list = "\n\n" + "\n".join([f"• {item.title()}" for item in items])
            # item_list = "<br><br>" + "<br>".join([f"• {item.title()}" for item in items])
            item_list = "".join([
            f"<button class='item-btn' onclick=\"selectItem('{item}')\">{item.title()}</button><br>"
            for item in items
])



            return {
               "intent": "order_id_received",
               "response": (
               f"Thanks 😊 I’ve received your <b>Order ID: {order_id}</b>.<br><br>"
               "Here are the items in this order:<br><br>"
               f"{item_list}<br>"
               "Please click the item you want to proceed with."
    )
}




        return {
            "intent": "order_id_missing",
            "response": "Please share your **Order ID** (example: ORD12345)."
        }

    # ==============================
    # Awaiting Item Selection
    # ==============================
    if conversation_state["awaiting_item_selection"]:
        for product in PRODUCT_DATABASE:
            if product in query_lower:
                conversation_state["selected_item"] = product
                conversation_state["awaiting_item_selection"] = False
                conversation_state["awaiting_action"] = True

                return {
                    "intent": "item_selected",
                    "response": (
                        f"You’ve selected **{product.title()}** ✅.\n\n"
                        "What would you like to do?\n"
                        "• 🔁 Replacement\n"
                        "• 💰 Refund\n"
                        "• 🔄 Return"
                    )
                }

        return {
            "intent": "invalid_item",
            "response": "Please select an item from the list shown above."
        }

    # ==============================
    # Awaiting Action Selection
    # ==============================
    if conversation_state["awaiting_action"]:
        if any(w in query_lower for w in ["refund", "return", "replace"]):
            action = "Refund" if "refund" in query_lower else \
                     "Return" if "return" in query_lower else "Replacement"

            conversation_state["awaiting_action"] = False

            return {
                "intent": "action_confirmed",
                "response": (
                    f"✅ Your **{action} request** for "
                    f"**{conversation_state['selected_item'].title()}** "
                    "has been successfully initiated."
                )
            }

        return {
            "intent": "action_missing",
            "response": "Please choose **Refund**, **Return**, or **Replacement**."
        }

    # ==============================
    # END CONVERSATION
    # ==============================
    if any(w in query_lower for w in ["thanks", "thank you", "bye"]):
        conversation_state["active"] = False
        return {
            "intent": "end",
            "response": "Thank you for chatting with us 😊. Have a great day!"
        }

    # ==============================
    # SENTIMENT DETECTION 
    # ==============================
    negative_keywords = [
        "problem", "issue", "complaint", "damage", "damaged", "broken",
        "defective", "angry", "frustrated", "terrible", "worst", "bad",
        "not happy", "unhappy", "disappointed", "hate", "awful", "poor", "dissatisfied", "lousy",
        "subpar", "unsatisfactory", "regret", "ripoff", "scam", "fraud", "junk", "trash",
        "useless", "worthless", "broken", "malfunction", "malfunctioning",
        "not working", "doesn't work", "never again","didn't like", "not satisfied", "not recommend"

    ]

    positive_keywords = [
        "good", "great", "excellent", "happy", "satisfied",
        "love", "amazing", "perfect", "awesome", "fantastic", "best", "recommend",
        "pleased", "delighted", "enjoyed", "wonderful", "positive", "brilliant", "superb", "outstanding", "exceptional",
        "five stars", "5 stars", "highly recommend", "will buy again"

    ]

    if any(word in query_lower for word in negative_keywords):
        sentiment = "negative"
    elif any(word in query_lower for word in positive_keywords):
        sentiment = "positive"
    else:
        sentiment = sentiment_model.predict(
            sent_vectorizer.transform([cleaned])
        )[0]

    conversation_state["sentiment"] = sentiment

    # ==============================
    # Sentiment-based Response
    # ==============================
    if sentiment == "negative":
        return {
            "intent": "negative_emotion",
            "response": (
                "I’m really sorry to hear that 😔. "
                "I understand how frustrating this must be. "
                "I’ll do my best to help you."
            )
        }

    if sentiment == "positive":
        return {
            "intent": "positive_emotion",
            "response": (
                "I’m glad to hear that 😊. "
                "How else can I assist you today?"
            )
        }

    return {
        "intent": "general_query",
        "response": "How can I assist you further?"
    }

# ==============================
# RESET ON REFRESH
# ==============================
def reset_conversation():
    global conversation_state
    conversation_state = {
    "active": True,
    "turns": 0,
    "sentiment": None,
    "negative_count": 0,
    "awaiting_order_id": False,
    "awaiting_item_selection": False,
    "awaiting_action": False,
    "order_id": None,
    "product_name": None,
    "selected_item": None,
    "order_status_request": False,

    
}

