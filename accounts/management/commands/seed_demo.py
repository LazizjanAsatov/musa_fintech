from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import Profile
from finance.models import Category, Transaction
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal


class Command(BaseCommand):
    help = 'Creates demo users, categories, and transactions for testing'

    def handle(self, *args, **options):
        self.stdout.write('Creating demo data...')
        
        # Create admin user
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'is_staff': True,
            }
        )
        if created:
            admin_user.set_password('AdminPass123!')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS(f'Created admin user: {admin_user.username}'))
        else:
            self.stdout.write(f'Admin user already exists: {admin_user.username}')
        
        # Set admin profile
        admin_profile, _ = Profile.objects.get_or_create(user=admin_user)
        admin_profile.role = 'ADMIN'
        admin_profile.is_active = True
        admin_profile.save()
        
        # Create regular user
        regular_user, created = User.objects.get_or_create(
            username='user',
            defaults={
                'email': 'user@example.com',
                'first_name': 'Regular',
                'last_name': 'User',
            }
        )
        if created:
            regular_user.set_password('UserPass123!')
            regular_user.save()
            self.stdout.write(self.style.SUCCESS(f'Created regular user: {regular_user.username}'))
        else:
            self.stdout.write(f'Regular user already exists: {regular_user.username}')
        
        # Set regular user profile
        user_profile, _ = Profile.objects.get_or_create(user=regular_user)
        user_profile.role = 'USER'
        user_profile.is_active = True
        user_profile.save()
        
        # Create global categories
        global_categories = [
            {'name': 'Salary', 'type': 'INCOME'},
            {'name': 'Freelance', 'type': 'INCOME'},
            {'name': 'Groceries', 'type': 'EXPENSE'},
            {'name': 'Utilities', 'type': 'EXPENSE'},
            {'name': 'Entertainment', 'type': 'EXPENSE'},
            {'name': 'Transportation', 'type': 'EXPENSE'},
        ]
        
        for cat_data in global_categories:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                owner=None,
                defaults={'type': cat_data['type']}
            )
            if created:
                self.stdout.write(f'Created global category: {category.name}')
        
        # Create user-specific categories
        user_categories = [
            {'name': 'Side Hustle', 'type': 'INCOME'},
            {'name': 'Dining Out', 'type': 'EXPENSE'},
        ]
        
        for cat_data in user_categories:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                owner=regular_user,
                defaults={'type': cat_data['type']}
            )
            if created:
                self.stdout.write(f'Created user category: {category.name}')
        
        # Create sample transactions for regular user
        now = timezone.now().date()
        
        # Get categories
        salary_cat = Category.objects.filter(name='Salary', owner__isnull=True).first()
        freelance_cat = Category.objects.filter(name='Freelance', owner__isnull=True).first()
        groceries_cat = Category.objects.filter(name='Groceries', owner__isnull=True).first()
        utilities_cat = Category.objects.filter(name='Utilities', owner__isnull=True).first()
        entertainment_cat = Category.objects.filter(name='Entertainment', owner__isnull=True).first()
        dining_cat = Category.objects.filter(name='Dining Out', owner=regular_user).first()
        
        # Income transactions (last 30 days)
        income_transactions = [
            {'date': now - timedelta(days=0), 'amount': Decimal('5000.00'), 'category': salary_cat, 'note': 'Monthly salary'},
            {'date': now - timedelta(days=15), 'amount': Decimal('5000.00'), 'category': salary_cat, 'note': 'Monthly salary'},
            {'date': now - timedelta(days=7), 'amount': Decimal('500.00'), 'category': freelance_cat, 'note': 'Freelance project'},
            {'date': now - timedelta(days=3), 'amount': Decimal('200.00'), 'category': freelance_cat, 'note': 'Small gig'},
        ]
        
        # Expense transactions (last 30 days)
        expense_transactions = [
            {'date': now - timedelta(days=1), 'amount': Decimal('150.00'), 'category': groceries_cat, 'note': 'Weekly groceries'},
            {'date': now - timedelta(days=5), 'amount': Decimal('150.00'), 'category': groceries_cat, 'note': 'Weekly groceries'},
            {'date': now - timedelta(days=10), 'amount': Decimal('150.00'), 'category': groceries_cat, 'note': 'Weekly groceries'},
            {'date': now - timedelta(days=14), 'amount': Decimal('150.00'), 'category': groceries_cat, 'note': 'Weekly groceries'},
            {'date': now - timedelta(days=2), 'amount': Decimal('120.00'), 'category': utilities_cat, 'note': 'Electricity bill'},
            {'date': now - timedelta(days=8), 'amount': Decimal('80.00'), 'category': utilities_cat, 'note': 'Water bill'},
            {'date': now - timedelta(days=4), 'amount': Decimal('50.00'), 'category': entertainment_cat, 'note': 'Movie tickets'},
            {'date': now - timedelta(days=6), 'amount': Decimal('75.00'), 'category': dining_cat, 'note': 'Restaurant dinner'},
            {'date': now - timedelta(days=12), 'amount': Decimal('60.00'), 'category': dining_cat, 'note': 'Lunch with friends'},
        ]
        
        # Create income transactions
        for trans_data in income_transactions:
            Transaction.objects.get_or_create(
                owner=regular_user,
                type='INCOME',
                date=trans_data['date'],
                amount=trans_data['amount'],
                defaults={
                    'category': trans_data['category'],
                    'note': trans_data['note'],
                }
            )
        
        # Create expense transactions
        for trans_data in expense_transactions:
            Transaction.objects.get_or_create(
                owner=regular_user,
                type='EXPENSE',
                date=trans_data['date'],
                amount=trans_data['amount'],
                defaults={
                    'category': trans_data['category'],
                    'note': trans_data['note'],
                }
            )
        
        self.stdout.write(self.style.SUCCESS(f'Created {len(income_transactions)} income and {len(expense_transactions)} expense transactions'))
        
        self.stdout.write(self.style.SUCCESS('\nDemo data created successfully!'))
        self.stdout.write('\nDemo Credentials:')
        self.stdout.write('  Admin: admin@example.com / AdminPass123!')
        self.stdout.write('  User:  user@example.com / UserPass123!')

