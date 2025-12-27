# FinTech Health Dashboard

A complete Personal Finance Health Dashboard built with Django, featuring transaction tracking, financial analytics, health scoring, and comprehensive admin backoffice management.

## Features

### User Features
- **Authentication**: Secure user registration, login, and logout
- **Dashboard**: 
  - Current balance display
  - Weekly/Monthly/Yearly financial summaries
  - Financial Health Score (0-100) with status indicators
  - Interactive charts (Weekly, Monthly, Yearly) using Chart.js
- **Transaction Management**:
  - Add income and expense transactions
  - Filter transactions by type, category, date range
  - Search transactions by note
  - Paginated transaction history
- **Category Management**: Create, edit, and delete custom categories

### Admin Features
- **User Management**: 
  - View all users
  - Activate/deactivate users
  - Change user roles (USER/ADMIN)
  - View user transaction statistics
- **System Settings**: Manage global categories
- **Monitoring**: 
  - System-wide transaction statistics
  - Daily totals tracking
  - Recent transaction activity
- **Audit Log**: Track all admin actions

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Step 1: Activate Virtual Environment

If you haven't already activated your virtual environment:

```bash
# On macOS/Linux
source venv/bin/activate

# On Windows
venv\Scripts\activate
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 4: Create Demo Data (Optional)

Create demo users and sample data:

```bash
python manage.py seed_demo
```

This will create:
- **Admin user**: `admin@example.com` / `AdminPass123!`
- **Regular user**: `user@example.com` / `UserPass123!`
- Sample categories and transactions

### Step 5: Run Development Server

```bash
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000/`

## Demo Credentials

After running `seed_demo`, you can use these credentials:

### Admin Account
- **Email**: `admin@example.com`
- **Username**: `admin`
- **Password**: `AdminPass123!`
- **Access**: Full admin dashboard with user management, monitoring, and audit logs

### Regular User Account
- **Email**: `user@example.com`
- **Username**: `user`
- **Password**: `UserPass123!`
- **Access**: User dashboard with transactions and categories

## Quick Demo Flow

### End-to-End User Flow

1. **Register/Login**: 
   - Go to `/accounts/register/` or use demo credentials
   - Login at `/accounts/login/`

2. **Create Category**:
   - Navigate to "Categories" in the menu
   - Click "Create Category"
   - Add a category (e.g., "Salary", "Groceries")

3. **Add Transaction**:
   - Click "Add Transaction" in the menu
   - Fill in: Type (Income/Expense), Category, Amount, Date, Note
   - Save the transaction

4. **View Dashboard**:
   - Go to Dashboard to see:
     - Updated balance
     - Health score calculation
     - Charts showing your data (Weekly/Monthly/Yearly tabs)

5. **View Transaction History**:
   - Go to "Transactions"
   - Use filters to search by type, category, date range, or note
   - View paginated results

### Admin Flow

1. **Login as Admin**:
   - Use admin credentials: `admin@example.com` / `AdminPass123!`
   - You'll be redirected to the Admin Dashboard

2. **User Management**:
   - Go to "Users" in the admin menu
   - View user list, search users
   - Click on a user to view details
   - Activate/deactivate users or change roles

3. **System Settings**:
   - Go to "Settings"
   - Create global categories (available to all users)

4. **Monitoring**:
   - Go to "Monitoring" to see system-wide statistics
   - View recent transactions across all users

5. **Audit Log**:
   - Go to "Audit Log" to see all admin actions

## Project Structure

```
fintech_health/
├── accounts/          # Authentication and user profiles
│   ├── models.py      # Profile model with roles
│   ├── views.py       # Registration, login views
│   ├── forms.py       # User registration form
│   ├── decorators.py  # Admin access decorator
│   └── urls.py
├── finance/           # Core finance functionality
│   ├── models.py      # Transaction, Category models
│   ├── views.py       # Dashboard, transactions, categories
│   ├── forms.py       # Transaction, Category forms
│   ├── utils.py       # Health score, balance, chart data
│   └── urls.py
├── backoffice/        # Admin backoffice
│   ├── models.py      # AuditLog model
│   ├── views.py       # User management, monitoring
│   ├── utils.py       # Audit logging helper
│   └── urls.py
├── templates/         # Django templates
│   ├── base.html      # Base template
│   ├── accounts/      # Auth templates
│   ├── finance/       # User-facing templates
│   └── backoffice/    # Admin templates
└── manage.py
```

## Key Features Implementation

### Financial Health Score

The health score (0-100) is calculated based on:
- **Base Score**: 50 points
- **Net Income Bonus**: Up to +30 points if net income is positive (last 30 days)
- **Spending Ratio Bonus**: Up to +20 points if expenses ≤ 80% of income
- **Status Labels**:
  - 70-100: "Healthy" (Green)
  - 40-69: "Caution" (Yellow)
  - 0-39: "Unhealthy" (Red)

### Security Features

- CSRF protection on all forms
- Password validation (Django built-in validators)
- Role-based access control (`@admin_required` decorator)
- Secure authentication using Django's auth system
- Passwords never displayed or logged

### Charts

- **Weekly**: Last 7 days, daily aggregation
- **Monthly**: Last 12 months, monthly aggregation
- **Yearly**: Last 5 years, yearly aggregation
- Uses Chart.js via CDN
- Shows Income, Expense, and Net trends

## Database

The project uses SQLite by default (for easy demo). The database file `db.sqlite3` will be created automatically after running migrations.

## Environment Variables

The project uses environment variables for sensitive settings. For demo purposes, a default SECRET_KEY is provided, but in production you should set:

```bash
export SECRET_KEY='your-secret-key-here'
```

## Troubleshooting

### Migration Issues
If you encounter migration errors:
```bash
python manage.py makemigrations
python manage.py migrate
```

### Static Files
If static files don't load, ensure `STATICFILES_DIRS` in settings.py points to your static directory.

### No Data in Charts
- Make sure you've created transactions
- Check that transaction dates are within the chart date ranges
- Verify categories are assigned to transactions

## Development Notes

- All views use proper authentication decorators
- Forms include server-side validation
- Error messages are user-friendly
- Navigation adapts based on user role
- All admin actions are logged in the audit log

## License

This project is for educational/demonstration purposes.


