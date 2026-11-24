from datetime import date

from flask import render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user

from extensions import db
from forms import EmployeeForm, SalaryForm, PayrollRunForm
from models import Employee, SalaryStructure, PayrollRun
from services.payroll_service import generate_payroll, approve_payroll
from blueprints.payroll import payroll_bp
from utils.decorators import company_required, role_required


@payroll_bp.route('/')
@login_required
@company_required
def index():
    employees = (Employee.query.filter_by(company_id=current_user.company_id)
                 .order_by(Employee.full_name).all())
    return render_template('payroll/employees.html', employees=employees)


@payroll_bp.route('/employees/new', methods=['GET', 'POST'])
@login_required
@company_required
@role_required('admin', 'finance', 'manager')
def new_employee():
    form = EmployeeForm()
    if form.validate_on_submit():
        emp = Employee(
            company_id=current_user.company_id,
            full_name=form.full_name.data.strip(),
            phone=form.phone.data, email=form.email.data,
            kra_pin=form.kra_pin.data, nssf_no=form.nssf_no.data,
            shif_no=form.shif_no.data, bank_account=form.bank_account.data,
            bank_name=form.bank_name.data, department=form.department.data,
            position=form.position.data, employment_type=form.employment_type.data,
        )
        db.session.add(emp)
        db.session.commit()
        flash('Employee saved.', 'success')
        return redirect(url_for('payroll.index'))
    return render_template('payroll/employee_form.html', form=form)


@payroll_bp.route('/employees/<int:eid>/salary', methods=['GET', 'POST'])
@login_required
@company_required
@role_required('admin', 'finance')
def salary(eid):
    emp = Employee.query.get_or_404(eid)
    if emp.company_id != current_user.company_id:
        abort(403)
    form = SalaryForm()
    if form.validate_on_submit():
        SalaryStructure.query.filter_by(employee_id=emp.id, active=True).update({'active': False})
        db.session.add(SalaryStructure(
            employee_id=emp.id, gross_salary=form.gross_salary.data,
            allowances=form.allowances.data or 0,
            effective_from=form.effective_from.data or date.today(),
        ))
        db.session.commit()
        flash('Salary updated.', 'success')
        return redirect(url_for('payroll.index'))
    return render_template('payroll/salary_form.html', form=form, employee=emp)


@payroll_bp.route('/runs')
@login_required
@company_required
def runs():
    rows = (PayrollRun.query.filter_by(company_id=current_user.company_id)
            .order_by(PayrollRun.created_at.desc()).all())
    return render_template('payroll/runs.html', runs=rows)


@payroll_bp.route('/runs/new', methods=['GET', 'POST'])
@login_required
@company_required
@role_required('admin', 'finance')
def new_run():
    form = PayrollRunForm()
    if form.validate_on_submit():
        run = generate_payroll(current_user.company_id, current_user.id,
                               form.period.data, form.label.data or '')
        flash(f'Payroll {run.period} generated. Total net: {run.total_net}', 'success')
        return redirect(url_for('payroll.runs'))
    return render_template('payroll/run_form.html', form=form)


@payroll_bp.route('/runs/<int:rid>/approve', methods=['POST'])
@login_required
@company_required
@role_required('admin', 'finance', 'approver')
def approve_run(rid):
    run = PayrollRun.query.get_or_404(rid)
    if run.company_id != current_user.company_id:
        abort(403)
    if run.status != 'draft':
        flash(f'Payroll is already {run.status}.', 'warning')
        return redirect(url_for('payroll.runs'))
    approve_payroll(run, current_user.id)
    flash('Payroll approved.', 'success')
    return redirect(url_for('payroll.runs'))
