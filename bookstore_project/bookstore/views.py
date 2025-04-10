# bookstore/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm
# from django.contrib.auth.decorators import login_required # Optional: Uncomment if needed for specific views
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse
# from django.contrib import messages # Optional: Uncomment if you want to add flash messages
from .models import Book

# --- Book Listing ---
def book_list(request: HttpRequest) -> HttpResponse:
    """Displays the list of available books."""
    books = Book.objects.all()
    context = {'books': books}
    return render(request, 'bookstore/book_list.html', context)

# --- Authentication ---
def login_view(request: HttpRequest) -> HttpResponse:
    """Handles user login."""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                auth_login(request, user)

                # --- CORRECTED REDIRECT LOGIC ---
                next_url = request.POST.get('next') # Get the 'next' value from POST data

                # Check if next_url is empty or None. Also good practice to ensure
                # it's a safe URL (though Django's default LoginView does more checks)
                if not next_url:
                    # If no 'next' URL was provided or it was empty,
                    # redirect to the default book list page.
                    next_url = reverse('book_list')
                # Consider adding URL safety checks here if needed for production

                return redirect(next_url)
                # --- END CORRECTED REDIRECT LOGIC ---

            else:
                # Invalid login message handled by form errors ('Please enter a correct
                # username and password. Note that both fields may be case-sensitive.')
                pass # Let the form render with errors below
        else:
             # Form validation failed message handled by form errors
             pass # Let the form render with errors below
    else:
        # This is a GET request, so create a blank form
        form = AuthenticationForm()

    # Pass the 'next' parameter from GET (if any) to the template
    # This value will be put into the hidden input field in the form
    next_page = request.GET.get('next', '')
    context = {'form': form, 'next': next_page}
    return render(request, 'bookstore/login.html', context)

# Use POST for logout for security (prevents CSRF)
def logout_view(request: HttpRequest) -> HttpResponseRedirect:
    """Handles user logout."""
    # Only allow logout via POST request
    if request.method == 'POST':
        auth_logout(request)
        # Optional: Add a logout message
        # messages.success(request, "You have been successfully logged out.")
        return redirect('book_list') # Redirect to book list after logout

    # If accessed via GET, it's safer to just redirect or show an error/confirmation.
    # Redirecting to book list is simple.
    return redirect('book_list')


# --- Cart Management (Using Sessions) ---

def add_to_cart(request: HttpRequest, book_id: int) -> HttpResponseRedirect:
    """Adds a book to the session-based cart."""
    # Retrieve the book or return a 404 error if not found
    book = get_object_or_404(Book, pk=book_id)

    # Get the cart from the session, default to an empty dictionary if not found
    cart = request.session.get('cart', {})

    # Use book ID as string key for session compatibility (JSON serializable)
    book_id_str = str(book.id) # Use book.id to ensure consistency

    # Increment quantity if book already in cart, otherwise add it with quantity 1
    quantity = cart.get(book_id_str, 0) + 1
    cart[book_id_str] = quantity

    # Save the updated cart back into the session
    request.session['cart'] = cart
    # request.session.modified = True # Mark session as modified if needed (usually automatic for top-level changes)

    # Optional: Add a success message
    # messages.success(request, f"'{book.title}' added to cart.")

    # Redirect back to the book list page (or potentially the referring page)
    return redirect('book_list')

def view_cart(request: HttpRequest) -> HttpResponse:
    """Displays the contents of the cart."""
    cart_session = request.session.get('cart', {})
    cart_items = []
    total_price = 0

    # Get book IDs from the session cart keys
    # Filter out any potentially non-integer keys just in case
    book_ids = [int(id_str) for id_str in cart_session.keys() if id_str.isdigit()]

    if book_ids:
        # Fetch all needed book objects from the database in one query
        books_in_cart = Book.objects.filter(pk__in=book_ids)
        # Create a dictionary for quick lookup: {book_id: book_object}
        book_dict = {book.id: book for book in books_in_cart}
    else:
        book_dict = {}

    # Prepare items for the template, ensuring book exists and quantity is valid
    for book_id_str, quantity in cart_session.items():
        try:
            book_id = int(book_id_str)
            # Check if the book was found in our database query and quantity is positive
            if book_id in book_dict and quantity > 0:
                book = book_dict[book_id]
                item_total = book.price * quantity
                cart_items.append({
                    'book': book,
                    'quantity': quantity,
                    'item_total': item_total,
                })
                total_price += item_total
            elif book_id_str in cart_session:
                 # If the ID from session isn't in our valid book_ids list
                 # or quantity is invalid, consider removing it from the session
                 # to clean up the cart (optional)
                 # del request.session['cart'][book_id_str]
                 # request.session.modified = True
                 pass # Or log an error
        except (ValueError, TypeError):
            # Handle cases where book_id_str is not a valid integer
            # You might want to log this or remove the invalid entry
            # if book_id_str in request.session.get('cart', {}): # Check existence before del
            #     del request.session['cart'][book_id_str]
            #     request.session.modified = True
            pass

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
    }
    return render(request, 'bookstore/cart.html', context)

def remove_from_cart(request: HttpRequest, book_id: int) -> HttpResponseRedirect:
    """Removes an item completely from the cart."""
    cart = request.session.get('cart', {})
    book_id_str = str(book_id)

    # Check if the item exists before trying to delete
    if book_id_str in cart:
        del cart[book_id_str]
        # Save the modified cart back to the session
        request.session['cart'] = cart
        # Optional: Add a message
        # book = get_object_or_404(Book, pk=book_id) # Need to get book if using its title
        # messages.success(request, f"Removed '{book.title}' from cart.")

    # Redirect back to the cart page to show the updated cart
    return redirect('view_cart')