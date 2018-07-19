$(function() {
  $('#id_contest').change(function () {
    const contest = $('#id_contest :selected').val();
    const date_time = $('#id_date_time').val();
    $.ajax({
      dataType: "json",
      url: 'get_matches/',
      type: 'GET',
      data: {'contest': contest, 'date_time': date_time},
      timeout: 5000,
      success: function (result) {
        const matches = result["matches"];
        $('#id_matches').find('option').remove();
        $.each(matches, function(key, value) {
          $('#id_matches')
            .append($("<option></option>")
              .attr("value",key)
              .text(value));
        });
      },
      error: function (result) {
        console.log(result.responseText)
      }
    });
  });
  $('#id_date_time').change(function () {
    const contest = $('#id_contest :selected').val();
    const date_time = $('#id_date_time').val();
    $.ajax({
      dataType: "json",
      url: 'get_matches/',
      type: 'GET',
      data: {'contest': contest, 'date_time': date_time},
      timeout: 5000,
      success: function (result) {
        const matches = result["matches"];
        $('#id_matches').find('option').remove();
        $.each(matches, function (key, value) {
          $('#id_matches')
            .append($("<option></option>")
              .attr("value", key)
              .text(value));
        });
      },
      error: function (result) {
        console.log(result.responseText)
      }
    });
  });
  $('#id_matches').change(function () {
    const matches = [];
    $.each($("#id_matches :selected"), function(){
      matches.push($(this).val());
    });
    console.log({'matches': matches});
    $.ajax({
      dataType: "json",
      url: 'get_teams/',
      type: 'GET',
      data: {'matches': matches},
      timeout: 5000,
      success: function (result) {
        const teams = result["teams"];
        $('#id_teams').find('option').remove();
        $.each(teams, function (key, value) {
          $('#id_teams')
            .append($("<option></option>")
              .attr("value", key)
              .text(value));
        });
      },
      error: function (result) {
        console.log(result.responseText)
      }
    });
  });
});