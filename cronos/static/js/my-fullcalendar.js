//-----------------------------------------------
//    Google OAuth
// From https://developers.google.com/google-apps/calendar/quickstart/js
//-----------------------------------------------
var CLIENT_ID = '1024060921596-rbc4dlpa1np62vtd8etcroppkv72pjg7.apps.googleusercontent.com';
var SCOPES = ['https://www.googleapis.com/auth/calendar'];

/**
 * Check if current user has authorized this application.
 */
function checkAuth() {
  gapi.auth.authorize(
    {
      'client_id': CLIENT_ID,
      'scope': SCOPES,
      'immediate': true
    }, handleAuthResult);
}

/**
 * Handle response from authorization server.
 *
 * @param {Object} authResult Authorization result.
 */
function handleAuthResult(authResult) {
  if (authResult && !authResult.error) {
    // Hide auth UI, then load client library.
    loadCalendarApi().then( function(val) {
        insertEvents();
    });
  } else {
    woops();
  }
}

/**
 * Initiate auth flow in response to gcal export.
 */
function handleAuthClick() {
  gapi.auth.authorize(
    {client_id: CLIENT_ID, scope: SCOPES, immediate: false},
    handleAuthResult);
  return false;
}

/**
 * Load Google Calendar client library.
 */
function loadCalendarApi() {
  return gapi.client.load('calendar', 'v3');
}

function insertEvents() {
    var success = false
    gapi.client.calendar.calendars.insert({
        'summary': calName
    }).execute(function(response) {

        if (response.error) {
            console.log(response.error);
            woops();
        }
        var calID = response.id;
        console.log("new calId:" + calID);
        g_events.forEach(function(e) {
            gapi.client.calendar.events.insert({
                'calendarId': calID,
                'resource': e
            }).then(function(response){
                success = true;
            }, function(reason){
                console.log(reason);
                woops();
            });
        });
        alert('Calendar created.');
        yay();
    });
}

/**
 * Print the summary and start datetime/date of the next ten events in
 * the authorized user's calendar. If no events are found an
 * appropriate message is printed.
 */

function listUpcomingEvents() {
  var request = gapi.client.calendar.events.list({
    'calendarId': 'primary',
    'timeMin': (new Date()).toISOString(),
    'showDeleted': false,
    'singleEvents': true,
    'maxResults': 10,
    'orderBy': 'startTime'
  });

  request.execute(function(resp) {
    var events = resp.items;
    appendPre('Upcoming events:');

    if (events.length > 0) {
      for (i = 0; i < events.length; i++) {
        var event = events[i];
        var when = event.start.dateTime;
        if (!when) {
          when = event.start.date;
        }
        appendPre(event.summary + ' (' + when + ')')
      }
    } else {
      appendPre('No upcoming events found.');
    }

  });
}





var abbrvs = {
    Monday: "M",
    Tuesday: "T",
    Wednesday: "W",
    Thursday: "R",
    Friday: "F"
};
colors = [
    ['#F44336', '#e53935'],  // Red
    ['#9C27B0', '#8E24AA'],  // Purple
    ['#2196F3', '#1E88E5'],  // Blue
    ['#8BC34A', '#7CB342'],  // Light Green
    ['#FFC107', '#FFB300'],  // Amber
    ['#3F51B5', '#3949AB'],  // Indigo
    ['#607D8B', '#546E7A']   // Blue Grey
]

function makeFevent(e) {
    fevent = jQuery.extend({}, e);
    var colrs = colors[e.group - 1];
    fevent.backgroundColor = colrs[0];
    fevent.borderColor = colrs[1];
    return fevent;
}

function makeCalendar() {
    $('#calendar').fullCalendar({
        defaultDate: '2015-09-10',
        eventLimit: true, // allow "more" link when too many events
        defaultView: 'agendaWeek',
        header: false,
        allDaySlot: false,
        columnFormat: 'dddd',
        slotDuration: '01:00:00',
        slotLabelInterval: '01:00:00',
        // timezone: 'local',
        minTime: "08:00:00",
        maxTime: "21:00:00",
        weekends: false,
        height: 'auto',
        displayEventTime: false,
        // aspectRatio: 1.82,
        events: fevents,
        eventClick: function (calEvent, jsEvent, view) {
            $("#dialog").attr('title', calEvent.title);
            $("#dialog #description").html(
                calEvent.description.split("\n").join("<br/>")
            );
            $("#dialog #location").text(calEvent.location);
            console.log($("#dialog").html());
            $("#dialog").dialog({
                autoOpen: false,
            });
            $('#dialog').dialog('open');
            $('.ui-dialog-titlebar').css('background', calEvent.backgroundColor);
            $('.ui-dialog-titlebar-close').html(
                '<i class="icon ion-close-round"></i>'
            )
        },
    });
}
function download(filename, text) {
  var element = document.createElement('a');
  element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
  element.setAttribute('download', filename);

  element.style.display = 'none';
  document.body.appendChild(element);

  element.click();

  document.body.removeChild(element);
}

//---------------------
//       Modal
//---------------------
var duration = 'slow'
function displayModalBody(modalBody) {
    $('.modal-body').slideUp(duration);
    $('.modal-footer').slideUp(duration);
    if (modalBody.css('display') === 'none'){
        $(modalBody).slideToggle(duration);
    }
};

function validate_input(el) {
    var val = el.val();
    var valid = /^[A-Za-z\d\s]+$/.test(val);
    console.log(valid);
    return valid;
};

function woops() {
    displayModalBody($('.modal-body#download-error'));
}

function yay() {
    $('.modal-body').slideUp(duration);
    $('.modal-footer').slideDown(duration);
}

$(document).ready(function() {

    // We do this here because we might want to have
    // user-input formatters eventually.
    $.ajax({
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({courses: COURSES, format: FORMATTER}),
        dataType: 'json',
        url: '/events',
    }).done(function(data) {
        events = data.events;
        fevents = events.map(makeFevent);
        makeCalendar();
    });

    // Show only abbreviated day names for small screens
    if (matchMedia) {
        var mq = window.matchMedia("(max-width: 400px)");
        if (mq.matches) {
            $('.fc-day-header span').text(function (i) {
                return abbrvs[$(this).text()]
            });
        }
    }

    $('.modal-header a').bind('click', function() {
        var toShow = $('.modal-body#' + $(this).attr('id') + '-instructions');
        displayModalBody(toShow);
    });

    // Submit
    $('.modal-body button').bind('click', function() {
        var calNameInput = $(this).parent().find('input');
        if (calNameInput) {
            if (!validate_input(calNameInput)) {
                calNameInput.addClass('invalid');
                calNameInput.focus();
                return;
            }
            calName = calNameInput.val();
        }
        var format = $(this).attr('calendar');
        var r = $.ajax({
            type: 'POST',
            // Provide correct Content-Type, so that Flask will know how to process it.
            contentType: 'application/json',
            // Encode your data as JSON.
            data: JSON.stringify({events: events, format: format}),
            // This is the type of data you're expecting back from the server.
            dataType: 'json',
            url: SCRIPT_ROOT + '/calendar',
        }).done(function(data) {
            if (data.hasOwnProperty('calendar')) {
                download('calendar.ics', data.calendar);
                yay();
            } else {
                g_events = data.events;
                handleAuthClick();
            }

        }).fail(woops);
    });
});

