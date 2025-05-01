# istifdeci rollaari
ROLE_CHOICES = (
    ('customer', 'Musteri'),
    ('staff', 'isci'),
    ('admin', 'Admin'),
)

# Endirim nisbeeti
DISCOUNT_PERCENTAGES = (
    (0, 'Endirimsiz'),
    (10, '10%'),
    (20, '20%'),
    (50, '50%'),
    (70, '70%'),
)

# sifaris melumatlari
STATUS_CHOICES = (
    ("pending", "gozleyir"),
    ("completed", "tamamlandi"),
    ("cancelled", "legv olundu"),
)

# Bonus xal sistemi
BONUS_POINTS_PER_AZN = 10  #her 10 azn ucun 1 xal
BONUS_COFFEE_THRESHOLD = 5 # 5 xal ucun pulsuz kofe

# satis statisticasi ucun
PAYMENT_TYPE_CHOICES = (
    ('cash', 'Nagd'),
    ('card', 'Kart'),
)