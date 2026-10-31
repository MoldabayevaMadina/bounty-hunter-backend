from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class WantedCriminal(models.Model):
    name = models.CharField(max_length=120, blank=True)
    nickname = models.CharField(max_length=120)  
    reward = models.PositiveIntegerField() 
    
    last_known_latitude = models.FloatField(
        null=True, blank=True, validators=[MinValueValidator(-90), MaxValueValidator(90)]
    )
    last_known_longitude = models.FloatField(
        null=True, blank=True, validators=[MinValueValidator(-180), MaxValueValidator(180)]
    )
    last_known_note = models.TextField(blank=True)
    difficulty = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    armed = models.BooleanField(default=False)
    has_crew = models.BooleanField(default=False)
    escape_master = models.BooleanField(default=False)

    class Meta:
        ordering = ["id"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(difficulty__gte=1, difficulty__lte=10),
                name="difficulty_1_to_10",
            ),
        ]

    def __str__(self):
        return f"{self.nickname} ({self.reward})"


class HuntLog(models.Model):
    criminal = models.ForeignKey(WantedCriminal, on_delete=models.CASCADE, related_name="hunt_logs")
    success = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)   
    class Meta:
        ordering = ["-created_at", "-id"]

    def __str__(self):
        return f"Hunt #{self.id} on {self.criminal.nickname}: {'success' if self.success else 'failed'}"