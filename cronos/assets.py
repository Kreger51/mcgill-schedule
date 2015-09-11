from flask.ext.assets import Bundle, Environment

bundles = dict(

    css_all=Bundle(
        'libs/css/bootstrap.min.css',
        'libs/css/jquery-ui.min.css',
        'css/main.css',
        'css/forms.css',
        filters='cssmin',
        output='public/css/common.css'),

    js_all=Bundle(
        'libs/js/jquery.min.js',
        'libs/js/bootstrap.min.js',
        'libs/js/jquery-ui.min.js',
        'libs/js/moment.min.js',
        filters='jsmin',
        output='public/js/common.js'),

    css_calendar=Bundle(
        'libs/css/fullcalendar.css',
        'css/my-fullcalendar.css',
        filters='cssmin',
        output='public/css/calendar.css'),

    js_calendar=Bundle(
        'js/fullcalendar.js',
        'js/my-fullcalendar.js',
        filters='jsmin',
        output='public/js/calendar.js'),

)

assets = Environment()
assets.register(bundles)
