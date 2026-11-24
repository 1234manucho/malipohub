import os
from flask import Flask, redirect, url_for, render_template
from flask_login import current_user

from config import get_config
from extensions import db, login_manager, migrate, csrf, scheduler


def create_app(config_name: str | None = None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(get_config(config_name))
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    # Import blueprints here so extensions are ready
    from blueprints.auth import auth_bp
    from blueprints.dashboard import dashboard_bp
    from blueprints.payments import payments_bp
    from blueprints.payroll import payroll_bp
    from blueprints.stock import stock_bp
    from blueprints.workforce import workforce_bp
    from blueprints.scheduling import scheduling_bp
    from blueprints.reports import reports_bp
    from blueprints.admin import admin_bp

    for bp in (auth_bp, dashboard_bp, payments_bp, payroll_bp,
               stock_bp, workforce_bp, scheduling_bp, reports_bp, admin_bp):
        app.register_blueprint(bp)

    # -------------------- Root route --------------------
    @app.route("/")
    def index():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard.index"))
        return render_template("index.html")

    # -------------------- Jinja filters --------------------
    from utils.formatters import kes, dt as dt_fmt
    app.jinja_env.filters["kes"] = kes
    app.jinja_env.filters["dt"] = dt_fmt

    # -------------------- Error handlers --------------------
    @app.errorhandler(403)
    def forbidden(_):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def not_found(_):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(_):
        db.session.rollback()
        return render_template("errors/500.html"), 500

    # -------------------- Dev-only: ensure tables exist --------------------
    # Creates missing tables on SQLite when DEBUG is on. No-op in prod.
    # Runs BEFORE load_pending_jobs, otherwise the scheduler query would
    # hit "no such table" on a fresh database.
    uri = app.config.get("SQLALCHEMY_DATABASE_URI", "")
    if app.config.get("DEBUG") and uri.startswith("sqlite"):
        with app.app_context():
            try:
                db.create_all()
                app.logger.info("SQLite tables ensured.")
            except Exception as exc:  # noqa: BLE001
                app.logger.warning("Could not auto-create tables: %s", exc)

    # -------------------- Scheduler bootstrap --------------------
    # IMPORTANT for production: when running gunicorn with multiple workers,
    # every worker would start its own scheduler and fire the same jobs N
    # times. Set SCHEDULER_ENABLED=false on the web workers and run
    # `python scheduler_worker.py` as a dedicated single-instance process
    # instead (see scheduler_worker.py in this project).
    if app.config.get("SCHEDULER_ENABLED") and not app.config.get("TESTING"):
        scheduler.configure(timezone=app.config["SCHEDULER_TIMEZONE"])
        if not scheduler.running:
            scheduler.start()
        from jobs.scheduler import load_pending_jobs
        load_pending_jobs(app)

    # -------------------- CLI --------------------
    @app.cli.command("init-db")
    def init_db():
        """Create all tables."""
        db.create_all()
        print("Database initialised.")

    @app.cli.command("seed")
    def seed():
        """Seed a demo company/admin (admin@malipohub.test / password123)."""
        from models import Company, User, Account, Payee
        if User.query.filter_by(email="admin@malipohub.test").first():
            print("Already seeded.")
            return
        c = Company(name="Demo Co", email="admin@malipohub.test", phone="0700000000")
        db.session.add(c)
        db.session.flush()
        u = User(company_id=c.id, email="admin@malipohub.test",
                 full_name="Demo Admin", role="admin")
        u.set_password("password123")
        db.session.add(u)
        db.session.add(Account(company_id=c.id, name="Petty Cash", account_type="petty_cash"))
        db.session.add(Payee(company_id=c.id, name="Alice W.", phone="254700000001", method="mpesa"))
        db.session.commit()
        print("Seeded: admin@malipohub.test / password123")

    return app


# ------------------------------------------------------------------
# Module-level WSGI app.
#
#   Gunicorn:  gunicorn -w 4 -b 0.0.0.0:8000 app:app
#   Flask CLI: flask --app app <command>
#   Dev:       python app.py
#
# Gunicorn's default `app:app` syntax imports this module and looks for
# the `app` attribute. Without this line it raises:
#   AppImportError: Failed to find attribute 'app' in 'app'.
# ------------------------------------------------------------------
app = create_app()


if __name__ == "__main__":
    # In dev, reuse the module-level app so create_app() is not called twice.
    app.run(debug=True, host="0.0.0.0", port=5000)