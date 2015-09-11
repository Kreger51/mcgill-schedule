
$(document).ready(function () {

    /* Highlight completed steps only */
    var curStep = $(".wizard").attr("step");
    $(".wizard-step").each( function(idx, object) {
        if(idx < curStep){
            object.removeAttribute("disabled");
        }
    });
});