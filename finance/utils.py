from django.db.models import Sum, Q
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from .models import Transaction


def calculate_balance(user):
    """Calculate current balance (total income - total expense)."""
    income = Transaction.objects.filter(owner=user, type='INCOME').aggregate(
        total=Sum('amount')
    )['total'] or Decimal('0.00')
    
    expense = Transaction.objects.filter(owner=user, type='EXPENSE').aggregate(
        total=Sum('amount')
    )['total'] or Decimal('0.00')
    
    return income - expense


def calculate_health_score(user):
    """
    Calculate financial health score (0-100).
    Rules:
    - Start at 50
    - + up to 30 points based on net_30 positive (scaled)
    - + up to 20 points if expense_30 <= 80% of income_30
    - Clamp 0..100
    """
    now = timezone.now().date()
    thirty_days_ago = now - timedelta(days=30)
    
    transactions_30 = Transaction.objects.filter(
        owner=user,
        date__gte=thirty_days_ago,
        date__lte=now
    )
    
    income_30 = transactions_30.filter(type='INCOME').aggregate(
        total=Sum('amount')
    )['total'] or Decimal('0.00')
    
    expense_30 = transactions_30.filter(type='EXPENSE').aggregate(
        total=Sum('amount')
    )['total'] or Decimal('0.00')
    
    net_30 = income_30 - expense_30
    
    # Start at 50
    score = 50
    
    # + up to 30 points based on net_30 positive (scaled)
    if net_30 > 0:
        # Scale: if net_30 is positive, add up to 30 points
        # Simple scaling: if net_30 >= income_30 * 0.2, get full 30 points
        if income_30 > 0:
            net_ratio = min(net_30 / income_30, Decimal('1.0'))
            score += float(net_ratio * Decimal('30'))
        else:
            score += 30
    else:
        # Negative net reduces score
        if income_30 > 0:
            net_ratio = abs(net_30) / income_30
            score -= min(float(net_ratio * Decimal('30')), 50)
        else:
            score -= 30
    
    # + up to 20 points if expense_30 <= 80% of income_30
    if income_30 > 0:
        expense_ratio = expense_30 / income_30
        if expense_ratio <= Decimal('0.8'):
            # Full 20 points if <= 80%
            score += 20
        elif expense_ratio <= Decimal('1.0'):
            # Partial points between 80% and 100%
            ratio_score = (Decimal('1.0') - expense_ratio) / Decimal('0.2') * 20
            score += float(ratio_score)
        # If > 100%, no points added
    
    # Clamp 0..100
    score = max(0, min(100, int(score)))
    
    return score


def get_health_status(score):
    """Get health status label based on score."""
    if score >= 70:
        return 'Healthy', 'success'
    elif score >= 40:
        return 'Caution', 'warning'
    else:
        return 'Unhealthy', 'danger'


def get_chart_data(user, period='monthly'):
    """
    Get aggregated chart data for user.
    period: 'weekly', 'monthly', 'yearly'
    """
    from django.db.models.functions import TruncDay, TruncWeek, TruncMonth, TruncYear
    from django.db.models import Sum
    
    now = timezone.now().date()
    
    if period == 'weekly':
        # Last 7 days, daily aggregation
        start_date = now - timedelta(days=6)
        transactions = Transaction.objects.filter(
            owner=user,
            date__gte=start_date,
            date__lte=now
        ).annotate(
            period=TruncDay('date')
        ).values('period', 'type').annotate(
            total=Sum('amount')
        ).order_by('period')
        
        labels = []
        income_data = []
        expense_data = []
        
        for day_offset in range(7):
            day = start_date + timedelta(days=day_offset)
            labels.append(day.strftime('%m/%d'))
            income_data.append(0)
            expense_data.append(0)
        
        for item in transactions:
            day_str = item['period'].strftime('%m/%d')
            if day_str in labels:
                idx = labels.index(day_str)
                if item['type'] == 'INCOME':
                    income_data[idx] = float(item['total'])
                else:
                    expense_data[idx] = float(item['total'])
    
    elif period == 'monthly':
        # Last 12 months
        start_date = now - timedelta(days=365)
        transactions = Transaction.objects.filter(
            owner=user,
            date__gte=start_date,
            date__lte=now
        ).annotate(
            period=TruncMonth('date')
        ).values('period', 'type').annotate(
            total=Sum('amount')
        ).order_by('period')
        
        labels = []
        income_data = []
        expense_data = []
        
        # Generate last 12 months
        for month_offset in range(12):
            month_date = now - timedelta(days=30 * month_offset)
            month_str = month_date.strftime('%Y-%m')
            labels.insert(0, month_date.strftime('%b %Y'))
            income_data.insert(0, 0)
            expense_data.insert(0, 0)
        
        for item in transactions:
            month_str = item['period'].strftime('%Y-%m')
            # Find matching month in labels
            for idx, label in enumerate(labels):
                if month_str in label:
                    if item['type'] == 'INCOME':
                        income_data[idx] = float(item['total'])
                    else:
                        expense_data[idx] = float(item['total'])
                    break
    
    else:  # yearly
        # Last 5 years
        start_date = now - timedelta(days=1825)
        transactions = Transaction.objects.filter(
            owner=user,
            date__gte=start_date,
            date__lte=now
        ).annotate(
            period=TruncYear('date')
        ).values('period', 'type').annotate(
            total=Sum('amount')
        ).order_by('period')
        
        labels = []
        income_data = []
        expense_data = []
        
        # Generate last 5 years
        current_year = now.year
        for year_offset in range(5):
            year = current_year - year_offset
            labels.insert(0, str(year))
            income_data.insert(0, 0)
            expense_data.insert(0, 0)
        
        for item in transactions:
            year_str = str(item['period'].year)
            if year_str in labels:
                idx = labels.index(year_str)
                if item['type'] == 'INCOME':
                    income_data[idx] = float(item['total'])
                else:
                    expense_data[idx] = float(item['total'])
    
    # Calculate net
    net_data = [income_data[i] - expense_data[i] for i in range(len(labels))]
    
    return {
        'labels': labels,
        'income': income_data,
        'expense': expense_data,
        'net': net_data,
    }

