from django.db import models


class CustomerUser(models.Model):
	username = models.CharField(max_length=120, unique=True)
	password_hash = models.CharField(max_length=255)
	full_name = models.CharField(max_length=255)
	email = models.EmailField(unique=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ["-created_at"]

	def __str__(self):
		return self.username


class CustomerSession(models.Model):
	customer = models.ForeignKey(CustomerUser, on_delete=models.CASCADE, related_name="sessions")
	token = models.CharField(max_length=128, unique=True)
	created_at = models.DateTimeField(auto_now_add=True)
	expires_at = models.DateTimeField()

	class Meta:
		ordering = ["-created_at"]


class Cart(models.Model):
	STATUS_CHOICES = [("active", "Active"), ("ordered", "Ordered")]

	customer = models.ForeignKey(CustomerUser, on_delete=models.CASCADE, related_name="carts")
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["-updated_at"]


class CartItem(models.Model):
	ITEM_TYPE_CHOICES = [
		("computer", "Computer"),
		("mobile", "Mobile"),
		("tablet", "Tablet"),
		("monitor", "Monitor"),
		("keyboard", "Keyboard"),
		("mouse", "Mouse"),
		("headphone", "Headphone"),
		("speaker", "Speaker"),
		("camera", "Camera"),
		("printer", "Printer"),
	]

	cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
	item_type = models.CharField(max_length=20, choices=ITEM_TYPE_CHOICES)
	item_id = models.PositiveIntegerField()
	item_name = models.CharField(max_length=255)
	unit_price = models.DecimalField(max_digits=12, decimal_places=2)
	quantity = models.PositiveIntegerField(default=1)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		unique_together = ("cart", "item_type", "item_id")


class Order(models.Model):
	STATUS_CHOICES = [("created", "Created"), ("paid", "Paid")]

	customer = models.ForeignKey(CustomerUser, on_delete=models.CASCADE, related_name="orders")
	total_amount = models.DecimalField(max_digits=14, decimal_places=2)
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="created")
	shipping_address = models.CharField(max_length=500)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ["-created_at"]


class OrderItem(models.Model):
	ITEM_TYPE_CHOICES = [
		("computer", "Computer"),
		("mobile", "Mobile"),
		("tablet", "Tablet"),
		("monitor", "Monitor"),
		("keyboard", "Keyboard"),
		("mouse", "Mouse"),
		("headphone", "Headphone"),
		("speaker", "Speaker"),
		("camera", "Camera"),
		("printer", "Printer"),
	]

	order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
	item_type = models.CharField(max_length=20, choices=ITEM_TYPE_CHOICES)
	item_id = models.PositiveIntegerField()
	item_name = models.CharField(max_length=255)
	unit_price = models.DecimalField(max_digits=12, decimal_places=2)
	quantity = models.PositiveIntegerField(default=1)
