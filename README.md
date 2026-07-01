# Ondrobit E-Shop 🛒

A fully functional, scalable, and responsive e-commerce platform built with Django. Ondrobit E-Shop offers a seamless shopping experience for users with dynamic product management, intuitive UI, and secure order processing.

## 🚀 Features

* **Advanced Product Presentation:** 
    * Multi-image product galleries with interactive thumbnails.
    * Smooth image zoom functionality on hover/click for detailed product viewing.
* **Dynamic Specifications:** Flexible key features and specifications that can be dynamically added from the admin panel (e.g., Brand, Bluetooth version).
* **Smart Cart & Checkout:** Real-time quantity updates, cart management, and seamless checkout processing.
* **Order Management:** Supports Cash on Delivery (COD) and online payment logic with dynamic order status tracking.
* **Inventory Control:** Real-time stock tracking with automated "Out of Stock" handling and quantity limits.
* **Custom Admin Dashboard:** A highly customized Django admin interface utilizing inlines for efficient management of product images, specifications, and related data.
* **Responsive UI:** Mobile-first, clean, and modern design utilizing Bootstrap and custom CSS.

## 🛠️ Tech Stack

* **Backend:** Python, Django
* **Frontend:** HTML5, CSS3, Bootstrap 5, JavaScript
* **Database:** SQLite (Development) / PostgreSQL (Production ready)
* **Architecture:** MVT (Model-View-Template)

## ⚙️ Installation & Setup

Follow these steps to run the project locally on your machine.

**1. Clone the repository**
bash
git clone [https://github.com/yourusername/ondrobit-eshop.git](https://github.com/yourusername/ondrobit-eshop.git)
cd ondrobit-eshop
2. Create a virtual environment

Bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
3. Install dependencies

Bash
pip install -r requirements.txt
4. Apply database migrations

Bash
python manage.py makemigrations
python manage.py migrate
5. Create a superuser (Admin)

Bash
python manage.py createsuperuser
6. Run the development server

Bash
python manage.py runserver
Open your browser and navigate to http://127.0.0.1:8000/ to view the site, or http://127.0.0.1:8000/admin/ to access the dashboard.

📁 Project Structure
shop/: Main application containing models, views, and URLs for products, cart, and orders.

templates/: HTML templates (including base.html, product_detail.html).

static/: CSS, JavaScript, and image assets.

media/: User-uploaded content (e.g., product gallery images).

👨‍💻 Developed By
Nahidul Arafat for Ondrobit_Shop



Solely designed, architected, and developed this e-commerce solution to drive the technical vision of Ondrobit.

If you have any questions or suggestions, feel free to open an issue or submit a pull request!
