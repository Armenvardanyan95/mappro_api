from .models import Order

Order.objects.all().update(is_selected=True)