from django.db import models


class StaffUser(models.Model):
	username = models.CharField(max_length=120, unique=True)
	password_hash = models.CharField(max_length=255)
	full_name = models.CharField(max_length=255)
	email = models.EmailField(unique=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ["-created_at"]

	def __str__(self):
		return self.username


class StaffSession(models.Model):
	staff = models.ForeignKey(StaffUser, on_delete=models.CASCADE, related_name="sessions")
	token = models.CharField(max_length=128, unique=True)
	created_at = models.DateTimeField(auto_now_add=True)
	expires_at = models.DateTimeField()

	class Meta:
		ordering = ["-created_at"]


class ImportLog(models.Model):
	ITEM_TYPE_CHOICES = [("computer", "Computer"), ("mobile", "Mobile")]

	staff = models.ForeignKey(StaffUser, on_delete=models.CASCADE, related_name="imports")
	item_type = models.CharField(max_length=20, choices=ITEM_TYPE_CHOICES)
	payload = models.JSONField()
	target_item_id = models.IntegerField(null=True, blank=True)
	is_success = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ["-created_at"]
