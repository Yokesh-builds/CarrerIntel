
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    abort
)

from math import ceil

from database import (
    initialize_database,
    save_jobs,
    search_jobs,
    get_job_by_id,
    get_dashboard_statistics,
    get_filter_options
)

from main import collect_all_jobs, remove_duplicates


app = Flask(__name__)

app.secret_key = "change-this-secret-key-before-deployment"

initialize_database()


@app.route("/", methods=["GET"])
def index():

    keyword = request.args.get("q", "").strip()
    source = request.args.get("source", "").strip()
    company = request.args.get("company", "").strip()
    location = request.args.get("location", "").strip()

    try:
        page = max(1, int(request.args.get("page", 1)))
    except ValueError:
        page = 1

    per_page = 20

    jobs, total = search_jobs(
        keyword=keyword,
        source=source,
        company=company,
        location=location,
        page=page,
        per_page=per_page
    )

    statistics = get_dashboard_statistics()

    companies, locations = get_filter_options()

    total_pages = max(1, ceil(total / per_page))

    return render_template(
        "index.html",
        jobs=jobs,
        keyword=keyword,
        selected_source=source,
        selected_company=company,
        selected_location=location,
        statistics=statistics,
        companies=companies,
        locations=locations,
        total=total,
        page=page,
        total_pages=total_pages
    )


@app.route("/job/<int:job_id>")
def job_details(job_id):

    job = get_job_by_id(job_id)

    if not job:
        abort(404)

    return render_template(
        "job_details.html",
        job=job
    )


@app.route("/collect", methods=["POST"])
def collect():

    try:

        collected, errors = collect_all_jobs()

        unique_jobs, duplicates = remove_duplicates(collected)

        inserted, updated = save_jobs(unique_jobs)

        message = (
            f"Collection completed. "
            f"{len(unique_jobs)} unique jobs collected; "
            f"{inserted} new jobs inserted; "
            f"{updated} existing jobs updated; "
            f"{duplicates} duplicates removed."
        )

        if errors:
            message += f" {len(errors)} source error(s) occurred."

        flash(
            message,
            "success" if not errors else "warning"
        )

    except Exception as error:

        flash(
            f"Job collection failed: {error}",
            "error"
        )

    return redirect(url_for("index"))


@app.errorhandler(404)
def page_not_found(error):

    return render_template(
        "job_details.html",
        job=None
    ), 404


if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
