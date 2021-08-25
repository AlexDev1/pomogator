publish_page = false;
if (!$) {
  $ = django.jQuery;
}
$(document).ready(function () {
  //Устанавливаем статус
  if (($('#id_published').is(':checked')) || ($('#id_delayed_publication').is(':checked'))) {
    $("#id_publish_field").attr("checked", true);

    //Old
    $("#id_delayed_publication").removeAttr("disabled");
    $("#id_published").removeAttr("disabled");
    publish_page = true;
  } else {
    $("#id_publish_field").attr("checked", false);
    $("#id_delayed_publication").attr("disabled");
    $("#id_published").attr("disabled");
    publish_page = false;
  }

  $("#id_publish_field").click(function () {
    publish_page = !publish_page;
    if (publish_page) {
      $("#id_published").removeAttr("disabled");
      $("#id_delayed_publication").removeAttr("disabled");
    } else {
      $("#id_published").attr("checked", false);
      $("#id_published").attr("disabled", true);
      $("#id_delayed_publication").attr("checked", false);
      $("#id_delayed_publication").attr("disabled", true);
    }
  });

  $("#id_published").click(function () {
    if (this.checked) {
      $("#id_delayed_publication").removeAttr("checked", true);
    }
  });
  $("#id_delayed_publication").click(function () {
    if (this.checked) {
      $("#id_published").removeAttr("checked", true);
    }
  })
})
