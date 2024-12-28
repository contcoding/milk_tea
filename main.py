import sqlite3
from tkinter import Tk, Label, Button, OptionMenu, StringVar, IntVar, Frame
import tkinter.messagebox as messagebox
from tkinter.ttk import Treeview
import tkinter.ttk as ttk

# 定义奶茶商品类
class MilkTeaProduct:
    def __init__(self, product_id, product_name, category, price):
        self.product_id = product_id
        self.product_name = product_name
        self.category = category
        self.price = price
        self.order_quantity = 0  # 点单数量，初始化为0

    def increase_quantity(self):
        self.order_quantity += 1

    def decrease_quantity(self):
        if self.order_quantity > 0:
            self.order_quantity -= 1


# 连接到SQLite数据库，如果不存在则创建新的数据库文件
conn = sqlite3.connect('milk_tea.db')
cursor = conn.cursor()

# 创建商品表（如果不存在）
cursor.execute('''
CREATE TABLE IF NOT EXISTS products (
    product_id INTEGER PRIMARY KEY,
    product_name TEXT,
    category TEXT,
    price REAL
)
''')

# 创建购物车表（如果不存在），用于存储加入购物车的商品及数量等信息
cursor.execute('''
CREATE TABLE IF NOT EXISTS shopping_cart (
    cart_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER,
    product_name TEXT,
    price REAL,
    quantity INTEGER,
    FOREIGN KEY (product_id) REFERENCES products (product_id)
)
''')

# 向商品表中插入初始数据（模拟原来的商品数据列表）
initial_products = [
    (1, "珍珠奶茶", "常规奶茶", 10),
    (2, "椰果奶茶", "常规奶茶", 10),
    (3, "抹茶拿铁", "奶类饮品", 12),
    (4, "草莓雪顶", "含奶沙冰", 15)
]
cursor.executemany('INSERT OR IGNORE INTO products (product_id, product_name, category, price) VALUES (?,?,?,?)', initial_products)

# 提交更改并关闭初始连接（后续需要操作时再重新打开连接）
conn.commit()
conn.close()


# 从数据库获取所有商品数据的函数
def get_products_from_database():
    conn = sqlite3.connect('milk_tea.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products')
    products_data = cursor.fetchall()
    conn.close()
    return products_data


# 从数据库获取购物车数据的函数
def get_shopping_cart_from_database():
    conn = sqlite3.connect('milk_tea.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM shopping_cart')
    cart_data = cursor.fetchall()
    conn.close()
    return cart_data


# 将商品加入购物车并更新数据库的函数
def add_to_cart(product_id):
    conn = sqlite3.connect('milk_tea.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM shopping_cart WHERE product_id=?', (product_id,))
    existing_item = cursor.fetchone()
    if existing_item:
        new_quantity = existing_item[4] + 1
        cursor.execute('UPDATE shopping_cart SET quantity=? WHERE product_id=?', (new_quantity, product_id))
    else:
        cursor.execute('SELECT product_name, price FROM products WHERE product_id=?', (product_id,))
        product_info = cursor.fetchone()
        product_name, price = product_info
        cursor.execute('INSERT INTO shopping_cart (product_id, product_name, price, quantity) VALUES (?,?,?, 1)', (product_id, product_name, price))
    conn.commit()
    conn.close()
    update_shopping_cart()
    messagebox.showinfo("提示", f"{product_name} 已加入购物车", font=("Arial", 12))


# 分类显示商品函数，从数据库获取商品数据后展示
def display_products_by_category():
    product_list.delete(*product_list.get_children())
    products_data = get_products_from_database()
    category_dict = {}
    for product_data in products_data:
        product_id, product_name, category, price = product_data
        if category not in category_dict:
            category_dict[category] = []
        category_dict[category].append((product_id, product_name, price))

    for category, product_list_data in category_dict.items():
        category_item = product_list.insert("", "end", text=category, open=True)
        for product_info in product_list_data:
            product_id, product_name, price = product_info
            product_list.insert(category_item, "end", text=product_name, values=(product_id, price))


# 显示购物车函数，从数据库获取购物车数据后展示并计算总价
def update_shopping_cart():
    cart_list.delete(*cart_list.get_children())
    total_price = 0
    cart_data = get_shopping_cart_from_database()
    for cart_item in cart_data:
        cart_id, product_id, product_name, price, quantity = cart_item
        cart_list.insert("", "end", text=product_name, values=(quantity, price, price * quantity))
        total_price += price * quantity
    total_price_label.config(text=f"总价: {total_price}")


# 从购物车减少商品数量或者移除商品（数量减为0时移除），并更新数据库
def adjust_cart():
    selected_item = cart_list.selection()
    if selected_item:
        item_data = cart_list.item(selected_item)
        product_name = item_data["text"]
        conn = sqlite3.connect('milk_tea.db')
        cursor = conn.cursor()
        cursor.execute('SELECT cart_id, product_id, quantity FROM shopping_cart WHERE product_name=?', (product_name,))
        cart_info = cursor.fetchone()
        cart_id, product_id, quantity = cart_info
        new_quantity = quantity - 1
        if new_quantity == 0:
            cursor.execute('DELETE FROM shopping_cart WHERE cart_id=?', (cart_id,))
        else:
            cursor.execute('UPDATE shopping_cart SET quantity=? WHERE cart_id=?', (new_quantity, cart_id))
        conn.commit()
        conn.close()
        update_shopping_cart()
        messagebox.showinfo("提示", f"{product_name} 数量已调整", font=("Arial", 12))
    else:
        messagebox.showerror("错误", "未选中购物车中的商品，请重新选择。", font=("Arial", 12))


# 增加购物车中商品数量功能，并更新数据库
def increase_cart_quantity():
    selected_item = cart_list.selection()
    if selected_item:
        item_data = cart_list.item(selected_item)
        product_name = item_data["text"]
        conn = sqlite3.connect('milk_tea.db')
        cursor = conn.cursor()
        cursor.execute('SELECT cart_id, product_id, quantity FROM shopping_cart WHERE product_name=?', (product_name,))
        cart_info = cursor.fetchone()
        cart_id, product_id, quantity = cart_info
        new_quantity = quantity + 1
        cursor.execute('UPDATE shopping_cart SET quantity=? WHERE cart_id=?', (new_quantity, cart_id))
        conn.commit()
        conn.close()
        update_shopping_cart()
        messagebox.showinfo("提示", f"{product_name} 数量已增加", font=("Arial", 12))
    else:
        messagebox.showerror("错误", "未选中购物车中的商品，请重新选择。", font=("Arial", 12))


# 模拟支付功能（这里只是简单打印提示，并清空购物车相关数据库表）
def checkout():
    global shopping_cart
    conn = sqlite3.connect('milk_tea.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM shopping_cart')
    conn.commit()
    conn.close()
    if shopping_cart:
        messagebox.showinfo("提示", "支付成功，感谢您的购买！", font=("Arial", 12))
        shopping_cart = []
        update_shopping_cart()
    else:
        messagebox.showwarning("提示", "购物车为空，无需支付。", font=("Arial", 12))


root = Tk()
root.title("奶茶点单系统")
root.geometry("800x600")
root.configure(bg="lightgray")

# 创建商品展示区域框架
product_frame = Frame(root, bg="white", bd=2, relief="groove")
product_frame.pack(pady=10, fill="both", expand=True)

# 创建操作按钮区域框架
button_frame = Frame(root, bg="white", bd=2, relief="groove")
button_frame.pack(pady=10, side="bottom", fill="x")

# 创建购物车展示区域框架
cart_frame = Frame(root, bg="white", bd=2, relief="groove")
cart_frame.pack(pady=10, fill="both", expand=True)

# 在商品展示区域框架内添加商品列表相关组件
Label(product_frame, text="商品列表", font=("Arial", 16)).pack()
product_list = Treeview(product_frame, columns=("ID", "价格"), show="tree headings")
product_list.heading("ID", text="商品ID")
product_list.heading("价格", text="单价")
product_list.pack(fill="both", expand=True)

# 设置商品列表Treeview样式
style = ttk.Style()
style.configure("Treeview.Heading", font=("Arial", 14), foreground="black")
style.configure("Treeview", rowheight=30, font=("Arial", 12))

# 在操作按钮区域框架内添加操作按钮，但隐藏按类别查看商品按钮，并调整布局顺序
Button(button_frame, text="按类别查看商品", command=display_products_by_category, font=("Arial", 12)).pack_forget()
# 使用Frame来包裹按钮，以便实现居中布局
button_container = Frame(button_frame)
button_container.pack(expand=True)  # 让其在父容器（button_frame）中扩展占满空间
Button(button_container, text="点单", command=lambda: add_to_cart(int(product_list.item(product_list.selection())["values"][0])), font=("Arial", 12)).pack(side="left", padx=5)
Button(button_container, text="增加商品数量", command=increase_cart_quantity, font=("Arial", 12)).pack(side="left", padx=5)
Button(button_container, text="减少商品数量", command=adjust_cart, font=("Arial", 12)).pack(side="left", padx=5)
Button(button_container, text="支付", command=checkout, font=("Arial", 12)).pack(side="left", padx=5)

# 为按钮添加鼠标悬停效果，改变背景色
def on_enter(event):
    event.widget.config(bg="lightblue")

def on_leave(event):
    event.widget.config(bg="SystemButtonFace")

for btn in button_frame.winfo_children():
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)

# 在购物车展示区域框架内添加购物车相关组件
Label(cart_frame, text="购物车", font=("Arial", 16)).pack()
cart_list = Treeview(cart_frame, columns=("数量", "单价", "小计"), show="tree headings")
cart_list.heading("数量", text="数量")
cart_list.heading("单价", text="单价")
cart_list.heading("小计", text="小计")
cart_list.pack(fill="both", expand=True)

total_price_label = Label(cart_frame, text="总价: 0", font=("Arial", 14))
total_price_label.pack()

# 程序启动时调用一次按类别查看商品功能，展示商品列表
display_products_by_category()

root.mainloop()