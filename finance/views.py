from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.utils import timezone
from django.utils.safestring import mark_safe
import json
from datetime import timedelta
from decimal import Decimal
from .models import Transaction, Category
from .forms import TransactionForm, CategoryForm
from .utils import calculate_balance, calculate_health_score, get_health_status, get_chart_data


@login_required
def dashboard_view(request):
    """User dashboard with balance, health score, and charts."""
    user = request.user
    
    # Calculate balance
    balance = calculate_balance(user)
    
    # Calculate health score
    health_score = calculate_health_score(user)
    health_status, health_class = get_health_status(health_score)
    
    # Get totals for different periods
    now = timezone.now().date()
    
    # Weekly (last 7 days)
    week_start = now - timedelta(days=6)
    weekly_income = Transaction.objects.filter(
        owner=user, type='INCOME', date__gte=week_start
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    weekly_expense = Transaction.objects.filter(
        owner=user, type='EXPENSE', date__gte=week_start
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    weekly_net = weekly_income - weekly_expense
    
    # Monthly (last 30 days)
    month_start = now - timedelta(days=29)
    monthly_income = Transaction.objects.filter(
        owner=user, type='INCOME', date__gte=month_start
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    monthly_expense = Transaction.objects.filter(
        owner=user, type='EXPENSE', date__gte=month_start
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    monthly_net = monthly_income - monthly_expense
    
    # Yearly (last 365 days)
    year_start = now - timedelta(days=364)
    yearly_income = Transaction.objects.filter(
        owner=user, type='INCOME', date__gte=year_start
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    yearly_expense = Transaction.objects.filter(
        owner=user, type='EXPENSE', date__gte=year_start
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    yearly_net = yearly_income - yearly_expense
    
    # Get chart data
    chart_data_weekly = get_chart_data(user, 'weekly')
    chart_data_monthly = get_chart_data(user, 'monthly')
    chart_data_yearly = get_chart_data(user, 'yearly')
    
    context = {
        'balance': balance,
        'health_score': health_score,
        'health_status': health_status,
        'health_class': health_class,
        'weekly_income': weekly_income,
        'weekly_expense': weekly_expense,
        'weekly_net': weekly_net,
        'monthly_income': monthly_income,
        'monthly_expense': monthly_expense,
        'monthly_net': monthly_net,
        'yearly_income': yearly_income,
        'yearly_expense': yearly_expense,
        'yearly_net': yearly_net,
        'chart_data_weekly': mark_safe(json.dumps(chart_data_weekly)),
        'chart_data_monthly': mark_safe(json.dumps(chart_data_monthly)),
        'chart_data_yearly': mark_safe(json.dumps(chart_data_yearly)),
    }
    
    return render(request, 'finance/dashboard.html', context)


@login_required
def transaction_list_view(request):
    """Transaction history with filtering and pagination."""
    user = request.user
    transactions = Transaction.objects.filter(owner=user)
    
    # Filtering
    transaction_type = request.GET.get('type', '')
    category_id = request.GET.get('category', '')
    search_query = request.GET.get('search', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    if transaction_type:
        transactions = transactions.filter(type=transaction_type)
    
    if category_id:
        transactions = transactions.filter(category_id=category_id)
    
    if search_query:
        transactions = transactions.filter(note__icontains=search_query)
    
    if date_from:
        transactions = transactions.filter(date__gte=date_from)
    
    if date_to:
        transactions = transactions.filter(date__lte=date_to)
    
    # Get categories for filter dropdown
    categories = Category.objects.filter(
        Q(owner=user) | Q(owner__isnull=True)
    ).order_by('name')
    
    # Pagination
    paginator = Paginator(transactions, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'filters': {
            'type': transaction_type,
            'category': category_id,
            'search': search_query,
            'date_from': date_from,
            'date_to': date_to,
        }
    }
    
    return render(request, 'finance/transaction_list.html', context)


@login_required
def transaction_create_view(request):
    """Create a new transaction."""
    if request.method == 'POST':
        form = TransactionForm(request.POST, user=request.user)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.owner = request.user
            transaction.save()
            messages.success(request, 'Transaction created successfully!')
            return redirect('finance:transaction_list')
    else:
        form = TransactionForm(user=request.user)
    
    return render(request, 'finance/transaction_form.html', {
        'form': form,
        'title': 'Add Transaction'
    })


@login_required
def category_list_view(request):
    """List and manage user categories."""
    user = request.user
    categories = Category.objects.filter(owner=user).order_by('name')
    
    return render(request, 'finance/category_list.html', {
        'categories': categories
    })


@login_required
def category_create_view(request):
    """Create a new category."""
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.owner = request.user
            category.save()
            messages.success(request, 'Category created successfully!')
            return redirect('finance:category_list')
    else:
        form = CategoryForm()
    
    return render(request, 'finance/category_form.html', {
        'form': form,
        'title': 'Create Category'
    })


@login_required
def category_edit_view(request, pk):
    """Edit an existing category."""
    category = get_object_or_404(Category, pk=pk, owner=request.user)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully!')
            return redirect('finance:category_list')
    else:
        form = CategoryForm(instance=category)
    
    return render(request, 'finance/category_form.html', {
        'form': form,
        'title': 'Edit Category',
        'category': category
    })


@login_required
def category_delete_view(request, pk):
    """Delete a category."""
    category = get_object_or_404(Category, pk=pk, owner=request.user)
    
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted successfully!')
        return redirect('finance:category_list')
    
    return render(request, 'finance/category_confirm_delete.html', {
        'category': category
    })

