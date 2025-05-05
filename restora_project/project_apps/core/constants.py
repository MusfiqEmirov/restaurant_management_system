# User Roles
ROLE_CHOICES = (
    ('customer', 'Customer'),
    ('staff', 'Staff'),
    ('admin', 'Admin'),
)

# Discount percentages
DISCOUNT_PERCENTAGES = (
    (0, 'No Discount'),
    (10, '10%'),
    (20, '20%'),
    (50, '50%'),
    (70, '70%'),
)

# Order Statuses
STATUS_CHOICES = (
    ("pending", "Pending"),
    ("completed", "Completed"),
    ("cancelled", "Cancelled"),
)

# Bonus Points System
BONUS_POINTS_PER_AZN = 10  # 1 point for every 10 AZN
BONUS_COFFEE_THRESHOLD = 5  # Free coffee for every 5 points

# Sales Statistics
PAYMENT_TYPE_CHOICES = (
    ('cash', 'Cash'),
    ('card', 'Card'),
)
