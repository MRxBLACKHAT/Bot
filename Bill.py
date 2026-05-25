# requirements:
# pip install pyTelegramBotAPI

import telebot
from telebot import types

API_TOKEN = "8888927005:AAGmD2SIRWBcvmCp-7vFeXbgG1mD-0i_tp0"

bot = telebot.TeleBot(API_TOKEN, parse_mode="HTML")

orders = []
waiting_for_order = {}

# CONVERT QUANTITY
def convert_quantity(quantity_text):

    qty = quantity_text.strip().upper()

    if "M" in qty:
        number = float(qty.replace("M", ""))
        return number * 1000

    if "K" in qty:
        number = float(qty.replace("K", ""))
        return number

    return float(qty)

# START
@bot.message_handler(commands=['start'])
def start(message):

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("➕ New Order")
    markup.row("📋 All Orders")
    markup.row("🗑 Delete Order")
    markup.row("💰 Total Amount Earned")

    bot.send_message(
        message.chat.id,
        """
🔥 <b>Welcome to Order Manager Bot by @xxxDICTATORxxx</b>
""",
        reply_markup=markup
    )

# NEW ORDER
@bot.message_handler(func=lambda m: m.text == "➕ New Order")
def new_order(message):

    waiting_for_order[message.chat.id] = True

    bot.send_message(
        message.chat.id,
        """
📥 <b>Send details line by line :</b>

🧾 Order No: 
🎮 Order Name: 
👤 Seller: 
📦 Quantity: 
💸 Rate: 
"""
    )

# SAVE ORDER
@bot.message_handler(func=lambda m: m.chat.id in waiting_for_order)
def save_order(message):

    try:
        data = message.text.strip().split("\n")

        if len(data) != 5:
            raise Exception()

        order_no = data[0]
        order_name = data[1]
        seller = data[2]

        quantity_text = data[3]
        rate = float(data[4])

        quantity_value = convert_quantity(quantity_text)

        amount = quantity_value * rate

        order = {
            "order_no": order_no,
            "order_name": order_name,
            "seller": seller,
            "quantity": quantity_text,
            "rate": rate,
            "amount": amount,
            "payment_status": "Pending"
        }

        orders.append(order)

        index = len(orders) - 1

        # PAYMENT BUTTONS
        markup = types.InlineKeyboardMarkup()

        btn_paid = types.InlineKeyboardButton(
            "✅ Mark Paid",
            callback_data=f"paid_{index}"
        )

        btn_pending = types.InlineKeyboardButton(
            "❌ Mark Pending",
            callback_data=f"pending_{index}"
        )

        markup.add(btn_paid, btn_pending)

        bill = f"""
✅ <b>ORDER SAVED</b>

🧾 Order No: <b>{order_no}</b>
🎮 Order Name: <b>{order_name}</b>
👤 Seller: <b>{seller}</b>
📦 Quantity: <b>{quantity_text}</b>
💸 Rate: <b>{rate}/K</b>
💰 Amount: <b>₹{amount}</b>

❌ Payment:
<b>Pending</b>
"""

        bot.send_message(
            message.chat.id,
            bill,
            reply_markup=markup
        )

        del waiting_for_order[message.chat.id]

    except:
        bot.send_message(
            message.chat.id,
            """
❌ <b>Invalid format.</b>

Send exactly 5 lines.
"""
        )

# ALL ORDERS
@bot.message_handler(func=lambda m: m.text == "📋 All Orders")
def all_orders(message):

    if not orders:
        bot.send_message(message.chat.id, "❌ <b>No orders found.</b>")
        return

    markup = types.InlineKeyboardMarkup()

    for i, order in enumerate(orders):

        status = "✅" if order["payment_status"] == "Paid" else "❌"

        btn = types.InlineKeyboardButton(
            f"{status} {order['order_name']} • {order['seller']}",
            callback_data=f"view_{i}"
        )

        markup.add(btn)

    bot.send_message(
        message.chat.id,
        "📋 <b>Select an order :</b>",
        reply_markup=markup
    )

# VIEW ORDER
@bot.callback_query_handler(func=lambda call: call.data.startswith("view_"))
def view_order(call):

    index = int(call.data.split("_")[1])

    order = orders[index]

    text = f"""
📦 <b>ORDER DETAILS</b>

🧾 Order No: <b>{order['order_no']}</b>
🎮 Order Name: <b>{order['order_name']}</b>
👤 Seller: <b>{order['seller']}</b>
📦 Qty: <b>{order['quantity']}</b>
💸 Rate: <b>{order['rate']}/K</b>
💰 Amount: <b>₹{order['amount']}</b>

{"✅ Payment:\n<b>Paid</b>" if order["payment_status"] == "Paid" else "❌ Payment:\n<b>Pending</b>"}
"""

    markup = types.InlineKeyboardMarkup()

    btn_paid = types.InlineKeyboardButton(
        "✅ Paid",
        callback_data=f"paid_{index}"
    )

    btn_pending = types.InlineKeyboardButton(
        "❌ Pending",
        callback_data=f"pending_{index}"
    )

    markup.add(btn_paid, btn_pending)

    bot.edit_message_text(
        text,
        call.message.chat.id,
        call.message.message_id,
        reply_markup=markup
    )

# UPDATE STATUS
@bot.callback_query_handler(
    func=lambda call:
    call.data.startswith("paid_") or
    call.data.startswith("pending_")
)
def update_status(call):

    data = call.data.split("_")

    status = data[0]
    index = int(data[1])

    if status == "paid":
        orders[index]["payment_status"] = "Paid"
    else:
        orders[index]["payment_status"] = "Pending"

    order = orders[index]

    text = f"""
📦 <b>ORDER DETAILS</b>

🧾 Order No: <b>{order['order_no']}</b>
🎮 Order Name: <b>{order['order_name']}</b>
👤 Seller: <b>{order['seller']}</b>
📦 Qty: <b>{order['quantity']}</b>
💸 Rate: <b>{order['rate']}/K</b>
💰 Amount: <b>₹{order['amount']}</b>

{"✅ Payment:\n<b>Paid</b>" if order["payment_status"] == "Paid" else "❌ Payment:\n<b>Pending</b>"}
"""

    markup = types.InlineKeyboardMarkup()

    btn_paid = types.InlineKeyboardButton(
        "✅ Paid",
        callback_data=f"paid_{index}"
    )

    btn_pending = types.InlineKeyboardButton(
        "❌ Pending",
        callback_data=f"pending_{index}"
    )

    markup.add(btn_paid, btn_pending)

    bot.edit_message_text(
        text,
        call.message.chat.id,
        call.message.message_id,
        reply_markup=markup
    )

    bot.answer_callback_query(call.id, "✅ Updated")

# DELETE ORDER MENU
@bot.message_handler(func=lambda m: m.text == "🗑 Delete Order")
def delete_order_menu(message):

    if not orders:
        bot.send_message(message.chat.id, "❌ <b>No orders found.</b>")
        return

    markup = types.InlineKeyboardMarkup()

    for i, order in enumerate(orders):

        btn = types.InlineKeyboardButton(
            f"🗑 {order['order_name']} • {order['seller']}",
            callback_data=f"delete_{i}"
        )

        markup.add(btn)

    bot.send_message(
        message.chat.id,
        "🗑 <b>Select order to delete :</b>",
        reply_markup=markup
    )

# DELETE ORDER
@bot.callback_query_handler(func=lambda call: call.data.startswith("delete_"))
def delete_order(call):

    index = int(call.data.split("_")[1])

    deleted_order = orders[index]["order_name"]

    del orders[index]

    bot.edit_message_text(
        f"""
🗑 <b>{deleted_order}</b> deleted successfully.
""",
        call.message.chat.id,
        call.message.message_id
    )

    bot.answer_callback_query(call.id, "Deleted")

# TOTAL EARNED + TOTAL POP
@bot.message_handler(func=lambda m: m.text == "💰 Total Amount Earned")
def total_earned(message):

    total_amount = 0
    total_pop = 0

    for order in orders:

        # ADD PAID AMOUNT
        if order["payment_status"] == "Paid":
            total_amount += order["amount"]

        # CONVERT QUANTITY TO NUMBER
        qty = convert_quantity(order["quantity"])

        total_pop += qty

    # FORMAT POP
    if total_pop >= 1000:
        pop_text = f"{total_pop/1000}M"
    else:
        pop_text = f"{total_pop}K"

    bot.send_message(
        message.chat.id,
        f"""
💰 <b>TOTAL REPORT</b>

💵 Total Amount Earned:
<b>₹ {total_amount}</b>

📦 Total POP Sent:
<b>{pop_text}</b>
"""
    )

print("🔥 Bot is running...")

bot.infinity_polling()