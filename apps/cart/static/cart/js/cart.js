// static/js/cart.js

// Отримати CSRF токен з cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

// Показати Toast повідомлення
function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    if (!toast) return;
    
    toast.textContent = message;
    toast.className = `toast ${type}`;
    toast.classList.add('show');
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// Додати товар до корзини
function addToCart(productId, quantity = 1) {
    fetch(`/cart/add/${productId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': csrftoken,
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: `quantity=${quantity}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast(data.message, 'success');
            updateCartCount(data.cart_items_count);
        } else {
            showToast(data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('Виникла помилка', 'error');
    });
}

// Видалити товар з корзини
function removeFromCart(productId) {
    if (!confirm('Ви впевнені, що хочете видалити цей товар з кошика?')) {
        return;
    }
    
    // Додати клас для анімації видалення
    const item = document.querySelector(`[data-product-id="${productId}"]`);
    if (item) {
        item.classList.add('removing');
    }
    
    fetch(`/cart/remove/${productId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': csrftoken,
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast(data.message, 'success');
            updateCartCount(data.cart_items_count);
            
            // Видалити елемент з DOM з анімацією
            if (item) {
                setTimeout(() => {
                    item.remove();
                    
                    // Оновити summary якщо функція існує
                    if (typeof updateCartUI === 'function' && data.cart_total !== undefined) {
                        updateCartUI(data);
                    }
                    
                    // Якщо корзина порожня - перезавантажити сторінку
                    if (data.cart_items_count === 0) {
                        location.reload();
                    }
                }, 300);
            }
        } else {
            showToast(data.message, 'error');
            if (item) {
                item.classList.remove('removing');
            }
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('Виникла помилка', 'error');
        if (item) {
            item.classList.remove('removing');
        }
    });
}

// Оновити кількість товару
function updateQuantity(productId, quantity) {
    fetch(`/cart/update/${productId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': csrftoken,
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: `quantity=${quantity}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast('Кількість оновлено', 'success');
            updateCartCount(data.cart_items_count);
            
            // Оновити відображення кількості
            const quantityInput = document.getElementById(`quantity-${productId}`);
            if (quantityInput) {
                quantityInput.value = quantity;
                
                // Оновити стан кнопок
                const item = document.querySelector(`[data-product-id="${productId}"]`);
                if (item) {
                    const decreaseBtn = item.querySelector('.decrease-btn');
                    const increaseBtn = item.querySelector('.increase-btn');
                    
                    if (decreaseBtn) {
                        decreaseBtn.disabled = (quantity <= 1);
                    }
                    if (increaseBtn) {
                        increaseBtn.disabled = (quantity >= 99);
                    }
                }
            }
            
            // Оновити summary якщо функція існує
            if (typeof updateCartUI === 'function' && data.cart_total !== undefined) {
                updateCartUI(data);
            }
        } else {
            showToast(data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('Виникла помилка', 'error');
    });
}

// Оновити лічильник в header
function updateCartCount(count) {
    // Знайти всі елементи з лічильником в header
    const cartLinks = document.querySelectorAll('a[href*="cart"]');
    
    cartLinks.forEach(link => {
        const badge = link.querySelector('span.absolute, span[class*="badge"]');
        if (badge) {
            badge.textContent = count;
            
            // Показати/сховати badge
            if (count > 0) {
                badge.style.display = 'flex';
            } else {
                badge.style.display = 'none';
            }
        }
    });
}