from flask import (redirect, render_template, session, flash,
                   request, abort, jsonify, send_file, url_for)

from . import app, utils, calminerva
from .forms import MinervaForm

import pdb


def verify_json():
    if 'application/json' not in request.headers['Content-Type']:
        abort(400, 'Request not JSON')


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', step=1, disclaim=True)


@app.route('/login', methods=['GET', 'POST'])
def login():
    def fail(msg=None, tryagain=True):
        if msg:
            flash(msg)
        if tryagain:
            flash('Please try again.')
        return redirect('login')

    form = MinervaForm()
    form.year.choices = [(x, x) for x in utils.this_and_next_year()]
    if request.method == 'POST':
        app.logger.info('Post in /login')
        if form.validate():
            try:
                app.logger.info('Fetching courses...')
                courses = calminerva.from_minerva(
                        user=form.user.data,
                        secret=form.secret.data,
                        season=form.season.data,
                        year=form.year.data
                )
            except calminerva.exceptions.LoginError:
                return fail('Invalid username or password.')
            except calminerva.exceptions.SemesterError:
                return fail('You are not registered for this semester.')
            app.logger.info('Got courses.')
            defaultDate = utils.max_start_date(courses)
            session['courses'] = calminerva.pretty_dump(courses)
            session['defaultDate'] = defaultDate
            return redirect('preview')
        else:
            print('Form errors:')
            for k, errors in form.errors.items():
                for e in errors:
                    print(' : '.join([k, e]))
            fail()

    return render_template('login.html', form=form, disclaim=True, step=2)


@app.route('/preview')
def preview():
    courses = session.get('courses')
    if courses is None:
        print("No courses in session.")
        fail('Session expired.')

    defaultDate = session.get('defaultDate')
    return render_template(
        'preview-calendar.html',
        courses=courses,
        formatter=calminerva.dump(calminerva.default_formatter),
        defaultDate=defaultDate,
        step=3,
    )


@app.route('/events', methods=['POST'])
def events():
    verify_json()
    data = calminerva.load(request.data.decode())
    courses = data.get('courses')
    formatter = data.get('formatter')
    if not courses:
        abort(400, 'Missing courses')
    courses = calminerva.load_models(
            courses,
            model=calminerva.Course,
            _load=False)
    if not formatter:
        formatter = calminerva.default_formatter
    else:
        formatter = calminerva.load_models(
                formatter,
                model=calminerva.Formatter,
                _load=False)
    events = calminerva.events(courses, formatter)
    rv = {'events': events}
    return calminerva.dump(rv), 200


@app.route('/calendar', methods=['POST'])
def calendar():
    verify_json()
    data = calminerva.load(request.data.decode())
    events = data.get('events')
    if not events:
        abort(400, 'Missing events.')
    events = calminerva.load_models(
            events,
            model=calminerva.Event,
            _load=False)
    format = data.get('format')
    if format == 'ics':
        rv = {'calendar': calminerva.ics(events)}
    elif format == 'gcal':
        rv = {'events': list(calminerva.gcal(events))}
    else:
        abort(400, 'Invalid/Missing format')
    return jsonify(**rv), 200


@app.route('/share')
def share():
    return render_template('share.html')


@app.errorhandler(400)
def custom400(error):
    response = jsonify({'message': error.description})
    response.status_code = 400
    return response