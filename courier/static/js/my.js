
$(document).ready(function () {
    $("#zone").change(function () {
        var val = $(this).val();
        if (val == "Dhaka Metro") {
            $("#weight").html("<option value='1'>Upto 1KG</option><option value='2'>Upto 3KG</option>");
        } else if (val == "Outside Dhaka") {
            $("#weight").html("<option value='1'>Upto 3KG</option><option value='2'>Upto 5KG</option>");
        } else if (val == "Next Day") {
            $("#weight").html("<option value='1'>Upto 3KG</option>");
        }
        else if (val == "item0") {
            $("#weight").html("<option value=''>--Select weight--</option>");
        }
    });
});

