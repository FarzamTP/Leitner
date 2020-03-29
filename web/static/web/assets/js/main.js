$(document).ready(function () {
    $("#add_category").click(function(){
        if($("#edit_category_form").is(":visible")){
            $("#edit_category_form").slideUp("slow");
        }

        if($("#delete_category_form").is(":visible")){
            $("#delete_category_form").slideUp("slow");
        }

        if($("#inherit_ownership_form").is(":visible")){
            $("#inherit_ownership_form").slideUp("slow");
        }

        $("#add_category_form").slideToggle("slow");
    });

    $("#edit_category").click(function(){
        if($("#add_category_form").is(":visible")){
            $("#add_category_form").slideUp("slow");
        }

        if($("#delete_category_form").is(":visible")){
            $("#delete_category_form").slideUp("slow");
        }

        if($("#inherit_ownership_form").is(":visible")){
            $("#inherit_ownership_form").slideUp("slow");
        }

        $("#edit_category_form").slideToggle("slow");
    });

    $("#delete_category").click(function(){
        if($("#edit_category_form").is(":visible")){
            $("#edit_category_form").slideUp("slow");
        }

        if($("#add_category_form").is(":visible")){
            $("#add_category_form").slideUp("slow");
        }

        if($("#inherit_ownership_form").is(":visible")){
            $("#inherit_ownership_form").slideUp("slow");
        }

        $("#delete_category_form").slideToggle("slow");
    });

    $("#inherit_ownership").click(function () {
        if($("#delete_category_form").is(":visible")){
            $("#delete_category_form").slideUp("slow");
        }

        if($("#edit_category_form").is(":visible")){
            $("#edit_category_form").slideUp("slow");
        }

        if($("#add_category_form").is(":visible")){
            $("#add_category_form").slideUp("slow");
        }

        $("#inherit_ownership_form").slideToggle("slow");
    });

    $("#category_name_selector").change(function () {
        var current_category_name = $("#category_name_selector").val();
        $("#new_category_name").val(current_category_name);

        $.ajax({
            url: "get_category_color/",
            type: "POST",
            dataType: "json",
            data: {'category_name': current_category_name},
            success: function (color) {
                $("#edit_category_color_code").val(color.category_color);
            }
        });
    });

    $("#show_meaning").click(function () {
        $("#word_extensions").slideToggle("slow");
    });

    $("#sender").change(function () {
        var user_id = $(this).val();
        // Gets user categories names
        $.ajax({
            url: 'get_selected_user_categories/',
            type: 'POST',
            dataType: 'json',
            data: {'user_id': user_id},
            success: function (data) {
                var select = $("#sender_category_name");
                for(var i = 0; i < data.user_categories_name.length; i++){
                    var category_name = data.user_categories_name[i];
                    select.append(new Option(category_name, category_name));
                }
            }
        });
    });

});