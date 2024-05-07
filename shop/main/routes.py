from flask import render_template, url_for, flash, redirect, request, Blueprint, abort
from flask_login import login_user, current_user, logout_user, login_required
from shop import db
from shop.models import User, Product, ShoppingCartItem
from shop.forms import RegistrationForm, LoginForm, AddToCartForm, CheckoutForm
from werkzeug.security import generate_password_hash, check_password_hash

main = Blueprint('main', __name__)

@main.route("/")
@main.route("/home")
def home():
    sort_by = request.args.get('sort_by', 'name')  # Default sorting by name
    if sort_by == 'price':
        products = Product.query.order_by(Product.price).all()
    elif sort_by == 'environment':
        products = Product.query.order_by(Product.carbon_footprint).all()
    else:  # Default and 'name' case
        products = Product.query.order_by(Product.name).all()

    form = AddToCartForm()
    return render_template('home.html', products=products, form=form)

@main.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Email already registered. Please use a different email or recover your password.', 'warning')
            return redirect(url_for('main.register'))

        hashed_password = generate_password_hash(form.password.data)
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html', title='Register', form=form)

@main.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@main.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.home'))

@main.route("/add_to_cart/<int:product_id>", methods=['POST'])
@login_required
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    form = AddToCartForm()
    if form.validate_on_submit():
        quantity = form.quantity.data

        cart_item = ShoppingCartItem.query.filter_by(user_id=current_user.id, product_id=product.id).first()
        if cart_item:
            cart_item.quantity += quantity
        else:
            new_item = ShoppingCartItem(user_id=current_user.id, product_id=product.id, quantity=quantity)
            db.session.add(new_item)
        db.session.commit()
        flash('Item added to cart!', 'success')
        return redirect(url_for('main.home'))
    else:
        for fieldName, errorMessages in form.errors.items():
            for error in errorMessages:
                flash(f'Error in {fieldName} - {error}', 'danger')
    return redirect(url_for('main.product', product_id=product_id))

@main.route("/cart")
@login_required
def cart():
    cart_items = ShoppingCartItem.query.filter_by(user_id=current_user.id).all()
    total_price = 0  # Initialize total price
    for item in cart_items:
        product = item.product  # Access the associated Product object using the relationship
        total_price += product.price * item.quantity
    return render_template('cart.html', cart_items=cart_items, total_price=total_price)

@main.route("/remove_from_cart/<int:item_id>")
@login_required
def remove_from_cart(item_id):
    item = ShoppingCartItem.query.get_or_404(item_id)
    if item.user_id != current_user.id:
        abort(403)
    db.session.delete(item)
    db.session.commit()
    flash('Item removed from cart.', 'info')
    return redirect(url_for('main.cart'))


@main.route("/checkout", methods=['GET', 'POST'])
@login_required
def checkout():
    form = CheckoutForm()
    if form.validate_on_submit():
        # Validate card number
        card_number = form.card_number.data.replace('-', '').replace(' ', '')
        if not card_number.isdigit() or len(card_number) != 16:
            flash('Invalid credit card number. Please enter a 16-digit number.', 'danger')
            return redirect(url_for('main.checkout'))

        cvv = form.cvv.data.strip()
        if not cvv.isdigit() or len(cvv) != 3:
            flash('Invalid CVV. Please enter a 3-digit number.', 'danger')
            return redirect(url_for('main.checkout'))

        # If all validations pass, show checkout successful message
        flash('Checkout successful!', 'success')

        # Clear the shopping cart
        ShoppingCartItem.query.filter_by(user_id=current_user.id).delete()
        db.session.commit()

        # Redirect to the checkout successful page
        return redirect(url_for('main.checkout_successful'))

    return render_template('checkout.html', title='Checkout', form=form)

@main.route("/checkout/successful")
@login_required
def checkout_successful():
    return render_template('checkout_successful.html')

@main.route("/product/<int:product_id>")
def product(product_id):
    product = Product.query.get_or_404(product_id)
    form = AddToCartForm()
    return render_template('product.html', product=product, form=form)