from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from accounts.decorators import admin_required
from accounts.models import Profile
from finance.models import Transaction, Category
from .models import AuditLog
from .utils import log_admin_action


@admin_required
def dashboard_view(request):
    """Admin dashboard with overview statistics."""
    # User statistics
    total_users = User.objects.count()
    active_users = Profile.objects.filter(is_active=True).count()
    admin_users = Profile.objects.filter(role='ADMIN').count()
    
    # Transaction statistics
    total_transactions = Transaction.objects.count()
    today_transactions = Transaction.objects.filter(
        created_at__date=timezone.now().date()
    ).count()
    
    # Recent transactions
    recent_transactions = Transaction.objects.select_related('owner', 'category').order_by('-created_at')[:20]
    
    # Daily totals (last 7 days)
    now = timezone.now().date()
    daily_totals = []
    for day_offset in range(7):
        day = now - timedelta(days=day_offset)
        day_transactions = Transaction.objects.filter(created_at__date=day)
        day_count = day_transactions.count()
        day_income = day_transactions.filter(type='INCOME').aggregate(
            total=Sum('amount')
        )['total'] or 0
        day_expense = day_transactions.filter(type='EXPENSE').aggregate(
            total=Sum('amount')
        )['total'] or 0
        daily_totals.append({
            'date': day,
            'count': day_count,
            'income': day_income,
            'expense': day_expense,
            'net': day_income - day_expense
        })
    
    daily_totals.reverse()  # Show oldest first
    
    context = {
        'total_users': total_users,
        'active_users': active_users,
        'admin_users': admin_users,
        'total_transactions': total_transactions,
        'today_transactions': today_transactions,
        'recent_transactions': recent_transactions,
        'daily_totals': daily_totals,
    }
    
    return render(request, 'backoffice/dashboard.html', context)


@admin_required
def user_list_view(request):
    """List all users with management options."""
    users = User.objects.select_related('profile').all().order_by('-date_joined')
    
    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(users, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'backoffice/user_list.html', {
        'page_obj': page_obj,
        'search_query': search_query
    })


@admin_required
def user_detail_view(request, pk):
    """View user details and manage user."""
    user = get_object_or_404(User, pk=pk)
    profile, created = Profile.objects.get_or_create(user=user)
    
    # Get user's transaction stats
    user_transactions = Transaction.objects.filter(owner=user)
    total_income = user_transactions.filter(type='INCOME').aggregate(
        total=Sum('amount')
    )['total'] or Decimal('0.00')
    total_expense = user_transactions.filter(type='EXPENSE').aggregate(
        total=Sum('amount')
    )['total'] or Decimal('0.00')
    net_balance = total_income - total_expense
    transaction_count = user_transactions.count()
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'toggle_active':
            profile.is_active = not profile.is_active
            profile.save()
            status = 'activated' if profile.is_active else 'deactivated'
            log_admin_action(
                request.user,
                f'User {status}',
                f'{user.username} ({user.email})',
                {'user_id': user.id, 'new_status': profile.is_active}
            )
            messages.success(request, f'User {status} successfully.')
        
        elif action == 'change_role':
            new_role = request.POST.get('role')
            if new_role in ['USER', 'ADMIN']:
                old_role = profile.role
                profile.role = new_role
                profile.save()
                log_admin_action(
                    request.user,
                    'Role changed',
                    f'{user.username} ({user.email})',
                    {'user_id': user.id, 'old_role': old_role, 'new_role': new_role}
                )
                messages.success(request, f'User role changed to {new_role}.')
        
        return redirect('backoffice:user_detail', pk=user.id)
    
    return render(request, 'backoffice/user_detail.html', {
        'user': user,
        'profile': profile,
        'total_income': total_income,
        'total_expense': total_expense,
        'net_balance': net_balance,
        'transaction_count': transaction_count,
    })


@admin_required
def settings_view(request):
    """Manage global categories and system settings."""
    # Get global categories (no owner)
    global_categories = Category.objects.filter(owner__isnull=True).order_by('name')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'create_category':
            name = request.POST.get('name', '').strip()
            category_type = request.POST.get('type', 'BOTH')
            
            if name:
                category = Category.objects.create(
                    name=name,
                    type=category_type,
                    owner=None
                )
                log_admin_action(
                    request.user,
                    'Global category created',
                    category.name,
                    {'category_id': category.id, 'type': category_type}
                )
                messages.success(request, 'Global category created successfully.')
            else:
                messages.error(request, 'Category name is required.')
        
        elif action == 'delete_category':
            category_id = request.POST.get('category_id')
            try:
                category = Category.objects.get(id=category_id, owner__isnull=True)
                category_name = category.name
                category.delete()
                log_admin_action(
                    request.user,
                    'Global category deleted',
                    category_name,
                    {'category_id': category_id}
                )
                messages.success(request, 'Global category deleted successfully.')
            except Category.DoesNotExist:
                messages.error(request, 'Category not found.')
        
        return redirect('backoffice:settings')
    
    return render(request, 'backoffice/settings.html', {
        'global_categories': global_categories
    })


@admin_required
def monitoring_view(request):
    """System monitoring and statistics."""
    now = timezone.now()
    
    # Transaction counts
    total_transactions = Transaction.objects.count()
    today_count = Transaction.objects.filter(created_at__date=now.date()).count()
    week_count = Transaction.objects.filter(
        created_at__gte=now - timedelta(days=7)
    ).count()
    month_count = Transaction.objects.filter(
        created_at__gte=now - timedelta(days=30)
    ).count()
    
    # Financial totals
    total_income = Transaction.objects.filter(type='INCOME').aggregate(
        total=Sum('amount')
    )['total'] or Decimal('0.00')
    total_expense = Transaction.objects.filter(type='EXPENSE').aggregate(
        total=Sum('amount')
    )['total'] or Decimal('0.00')
    net_total = total_income - total_expense
    
    # User statistics
    total_users = User.objects.count()
    users_with_transactions = User.objects.filter(transactions__isnull=False).distinct().count()
    
    # Category statistics
    total_categories = Category.objects.count()
    global_categories = Category.objects.filter(owner__isnull=True).count()
    user_categories = Category.objects.filter(owner__isnull=False).count()
    
    # Recent activity (last 50 transactions)
    recent_transactions = Transaction.objects.select_related(
        'owner', 'category'
    ).order_by('-created_at')[:50]
    
    context = {
        'total_transactions': total_transactions,
        'today_count': today_count,
        'week_count': week_count,
        'month_count': month_count,
        'total_income': total_income,
        'total_expense': total_expense,
        'net_total': net_total,
        'total_users': total_users,
        'users_with_transactions': users_with_transactions,
        'total_categories': total_categories,
        'global_categories': global_categories,
        'user_categories': user_categories,
        'recent_transactions': recent_transactions,
    }
    
    return render(request, 'backoffice/monitoring.html', context)


@admin_required
def audit_log_view(request):
    """View audit logs of admin actions."""
    logs = AuditLog.objects.select_related('actor').all()
    
    # Filter by action
    action_filter = request.GET.get('action', '')
    if action_filter:
        logs = logs.filter(action__icontains=action_filter)
    
    # Pagination
    paginator = Paginator(logs, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'backoffice/audit_log.html', {
        'page_obj': page_obj,
        'action_filter': action_filter
    })

