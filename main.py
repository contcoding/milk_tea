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


# 商品数据列表，模拟后端数据存储
products = [
    MilkTeaProduct(1, "珍珠奶茶", "常规奶茶", 10),
    MilkTeaProduct(2, "椰果奶茶", "常规奶茶", 10),
    MilkTeaProduct(3, "抹茶拿铁", "奶类饮品", 12),
    MilkTeaProduct(4, "草莓雪顶", "含奶沙冰", 15)
]

# 分类字典，用于存储按类别分类后的商品
category_dict = {}

# 初始化分类字典
for product in products:
    if product.category not in category_dict:
        category_dict[product.category] = []
    category_dict[product.category].append(product)

# 购物车列表
shopping_cart = []


# 分类显示商品函数
def display_products_by_category():
    product_list.delete(*product_list.get_children())
    for category, product_list_data in category_dict.items():
        category_item = product_list.insert("", "end", text=category, open=True)
        for product in product_list_data:
            product_list.insert(category_item, "end", text=product.product_name, values=(product.product_id, product.price))


# 点单功能，将商品加入购物车（避免重复添加商品行）
def add_to_cart():
    selected_item = product_list.selection()
    if selected_item:
        item_data = product_list.item(selected_item)
        product_id = int(item_data["values"][0])
        for product in shopping_cart:
            if product.product_id == product_id:
                product.increase_quantity()
                update_shopping_cart()
                messagebox.showinfo("提示", f"{product.product_name} 已加入购物车", font=("Arial", 12))
                return
        for product in products:
            if product.product_id == product_id:
                product.increase_quantity()
                shopping_cart.append(product)
                update_shopping_cart()
                messagebox.showinfo("提示", f"{product.product_name} 已加入购物车", font=("Arial", 12))
                return
    messagebox.showerror("错误", "未选中商品，请重新选择。", font=("Arial", 12))


# 显示购物车函数
def update_shopping_cart():
    cart_list.delete(*cart_list.get_children())
    total_price = 0
    for product in shopping_cart:
        cart_list.insert("", "end", text=product.product_name, values=(product.order_quantity, product.price, product.price * product.order_quantity))
        total_price += product.price * product.order_quantity
    total_price_label.config(text=f"总价: {total_price}")


# 从购物车减少商品数量或者移除商品（数量减为0时移除）
def adjust_cart():
    selected_item = cart_list.selection()
    if selected_item:
        item_data = cart_list.item(selected_item)
        product_name = item_data["text"]
        for product in shopping_cart:
            if product.product_name == product_name:
                product.decrease_quantity()
                if product.order_quantity == 0:
                    shopping_cart.remove(product)
                update_shopping_cart()
                messagebox.showinfo("提示", f"{product.product_name} 数量已调整", font=("Arial", 12))
                return
    messagebox.showerror("错误", "未选中购物车中的商品，请重新选择。", font=("Arial", 12))


# 增加购物车中商品数量功能
def increase_cart_quantity():
    selected_item = cart_list.selection()
    if selected_item:
        item_data = cart_list.item(selected_item)
        product_name = item_data["text"]
        for product in shopping_cart:
            if product.product_name == product_name:
                product.increase_quantity()
                update_shopping_cart()
                messagebox.showinfo("提示", f"{product.product_name} 数量已增加", font=("Arial", 12))
                return
    messagebox.showerror("错误", "未选中购物车中的商品，请重新选择。", font=("Arial", 12))


# 模拟支付功能（这里只是简单打印提示）
def checkout():
    global shopping_cart
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
button_frame.pack(pady=10, side="bottom", fill="x")  # 修改此处，让按钮框架位于底部

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
Button(button_frame, text="按类别查看商品", command=display_products_by_category, font=("Arial", 12)).pack_forget()  # 隐藏按钮
Button(button_frame, text="点单", command=add_to_cart, font=("Arial", 12)).pack(side="left", padx=5)
Button(button_frame, text="增加商品数量", command=increase_cart_quantity, font=("Arial", 12)).pack(side="left", padx=5)
Button(button_frame, text="减少商品数量", command=adjust_cart, font=("Arial", 12)).pack(side="left", padx=5)
Button(button_frame, text="支付", command=checkout, font=("Arial", 12)).pack(side="left", padx=5)

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