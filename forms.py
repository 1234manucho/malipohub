from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, SubmitField, SelectField,
    DecimalField, IntegerField, TextAreaField, DateTimeField, DateField,
)
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional, NumberRange


class RegisterForm(FlaskForm):
    company_name = StringField("Company name", validators=[DataRequired(), Length(2, 150)])
    full_name = StringField("Your name", validators=[DataRequired(), Length(2, 120)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    phone = StringField("Phone", validators=[Optional(), Length(9, 15)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8, max=128)])
    confirm = PasswordField("Confirm password", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Create account")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Sign in")


class PayeeForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(2, 120)])
    phone = StringField("Phone", validators=[Optional(), Length(9, 15)])
    account_number = StringField("Account number", validators=[Optional(), Length(2, 50)])
    bank_name = StringField("Bank name", validators=[Optional(), Length(2, 80)])
    method = SelectField("Method", choices=[("mpesa", "M-Pesa"), ("bank", "Bank"),
                                            ("paybill", "Paybill"), ("till", "Till")])
    tag = StringField("Tag", validators=[Optional(), Length(2, 40)])
    submit = SubmitField("Save")


class PaymentForm(FlaskForm):
    payee_id = SelectField("Payee", coerce=int)
    amount = DecimalField("Amount", validators=[DataRequired(), NumberRange(min=1)])
    method = SelectField("Method", choices=[("mpesa", "M-Pesa"), ("bank", "Bank"),
                                            ("paybill", "Paybill"), ("till", "Till")])
    description = StringField("Description", validators=[Optional(), Length(0, 255)])
    submit = SubmitField("Send payment")


class BulkUploadForm(FlaskForm):
    label = StringField("Batch label", validators=[DataRequired(), Length(2, 120)])
    submit = SubmitField("Upload batch")


class EmployeeForm(FlaskForm):
    full_name = StringField("Full name", validators=[DataRequired(), Length(2, 120)])
    phone = StringField("Phone", validators=[Optional(), Length(9, 15)])
    email = StringField("Email", validators=[Optional(), Email()])
    kra_pin = StringField("KRA PIN", validators=[Optional(), Length(5, 20)])
    nssf_no = StringField("NSSF", validators=[Optional(), Length(2, 20)])
    shif_no = StringField("SHIF", validators=[Optional(), Length(2, 20)])
    bank_account = StringField("Bank account", validators=[Optional(), Length(2, 50)])
    bank_name = StringField("Bank name", validators=[Optional(), Length(2, 80)])
    department = StringField("Department", validators=[Optional(), Length(2, 80)])
    position = StringField("Position", validators=[Optional(), Length(2, 80)])
    employment_type = SelectField("Employment type", choices=[("permanent", "Permanent"),
                                                              ("contract", "Contract"),
                                                              ("casual", "Casual")])
    submit = SubmitField("Save employee")


class SalaryForm(FlaskForm):
    gross_salary = DecimalField("Gross salary", validators=[DataRequired(), NumberRange(min=1)])
    allowances = DecimalField("Allowances", validators=[Optional(), NumberRange(min=0)], default=0)
    effective_from = DateField("Effective from", validators=[Optional()])
    submit = SubmitField("Save salary")


class PayrollRunForm(FlaskForm):
    period = StringField("Period (YYYY-MM)", validators=[DataRequired(), Length(7, 7)])
    label = StringField("Label", validators=[Optional(), Length(2, 120)])
    submit = SubmitField("Generate payroll")


class ItemForm(FlaskForm):
    name = StringField("Item name", validators=[DataRequired(), Length(2, 120)])
    sku = StringField("SKU", validators=[Optional(), Length(0, 60)])
    unit = StringField("Unit", validators=[Optional(), Length(1, 20)])
    cost_price = DecimalField("Cost price", validators=[Optional(), NumberRange(min=0)], default=0)
    selling_price = DecimalField("Selling price", validators=[Optional(), NumberRange(min=0)], default=0)
    stock_qty = DecimalField("Opening stock", validators=[Optional(), NumberRange(min=0)], default=0)
    reorder_level = DecimalField("Reorder level", validators=[Optional(), NumberRange(min=0)], default=0)
    submit = SubmitField("Save item")


class PurchaseOrderForm(FlaskForm):
    supplier_id = SelectField("Supplier", coerce=int)
    submit = SubmitField("Create PO")


class AttendanceForm(FlaskForm):
    employee_id = SelectField("Employee", coerce=int)
    submit = SubmitField("Clock in")


class TaskForm(FlaskForm):
    employee_id = SelectField("Assign to", coerce=int)
    title = StringField("Title", validators=[DataRequired(), Length(2, 160)])
    description = TextAreaField("Description", validators=[Optional()])
    due_on = DateField("Due on", validators=[Optional()])
    submit = SubmitField("Create task")


class ScheduleForm(FlaskForm):
    job_type = SelectField("Job type", choices=[
        ("payroll", "Payroll run"),
        ("bulk_disbursement", "Bulk disbursement"),
        ("single_payment", "Single payment"),
        ("reorder", "Stock reorder"),
    ])
    ref_id = IntegerField("Reference ID", validators=[DataRequired()])
    label = StringField("Label", validators=[Optional(), Length(0, 120)])
    run_at = DateTimeField("Run at", format="%Y-%m-%dT%H:%M", validators=[DataRequired()])
    recurrence = SelectField("Recurrence", choices=[("once", "Once"), ("daily", "Daily"),
                                                    ("weekly", "Weekly"), ("monthly", "Monthly")])
    submit = SubmitField("Schedule")