$(document).ready(function() {
    disableOptions();
    $("#productId").on("change", function(){
        $("#fromLocation option").not(":first").remove();
        if ($("#productId").val()) {
            ajaxCall("get-from-locations");
            enableOptions();
        } else {
            disableOptions();
        }
        return false;
    });

    $("#submitLocation").on("click", function(e){
      e.preventDefault();
      $.ajax({
        data: {
          location: $("#location_name").val(),
        },
        type: "POST",
        url: "/dub-locations/",
      }).done(function (data) {
        if (data.output) {
          $("#location_form").submit();
          console.log(data.output);
        } else {
          alert("This Name is already used, please choose other one.");
        }
      });
    });


    $("#submitChemicalLocation").on("click", function(e){
      e.preventDefault();
      $.ajax({
        data: {
          chemical_location: $("#chemical_location_name").val(),
        },
        type: "POST",
        url: "/dub-chemical-locations/",
      }).done(function (data) {
        if (data.output) {
          $("#chemical_location_form").submit();
          console.log(data.output);
        } else {
          alert("This Name is already used, please choose other one.");
        }
      });
    });

    $("#submitStorage").on("click", function(e){
      e.preventDefault();
      $.ajax({
        data: {
          storage: $("#storage_name").val(),
        },
        type: "POST",
        url: "/dub-storages/",
      }).done(function (data) {
        if (data.output) {
          $("#storage_form").submit();
          console.log(data.output);
        } else {
          alert("This Name is already used, please choose other one.");
        }
      });
    });


    $("#submitHazard").on("click", function(e){
      e.preventDefault();
      $.ajax({
        data: {
          hazard: $("#hazard_name").val(),
        },
        type: "POST",
        url: "/dub-hazards/",
      }).done(function (data) {
        if (data.output) {
          $("#hazard_form").submit();
          console.log(data.output);
        } else {
          alert("This Name is already used, please choose other one.");
        }
      });
    });

    $("#submitStorageCategory").on("click", function(e){
      e.preventDefault();
      $.ajax({
        data: {
          storage_category: $("#storage_category_name").val(),
        },
        type: "POST",
        url: "/dub-storage-categories/",
      }).done(function (data) {
        if (data.output) {
          $("#storage_category_form").submit();
          console.log(data.output);
        } else {
          alert("This Name is already used, please choose other one.");
        }
      });
    });

    
    $("#submitChemical").on("click", function (e) {
      e.preventDefault();
      $.ajax({
        data: {
          chemical_name: $("#chemical_name").val(),
        },
        type: "POST",
        url: "/dub-chemicals/",
      }).done(function (data) {
        if (data.output) {
          $("#chemical_form").submit();
          console.log(data.output);
        } else {
          alert("This Name is already used, please choose other one.");
        }
      });
    });

     $("#submitConsumable").on("click", function (e) {
      e.preventDefault();
      $.ajax({
        data: {
          consumable_name: $("#consumable_name").val(),
        },
        type: "POST",
        url: "/dub-consumables/",
      }).done(function (data) {
        if (data.output) {
          $("#consumables_form").submit();
          console.log(data.output);
        } else {
          alert("This Name is already used, please choose other one.");
        }
      });
    });

    $("#updateChemical").on("click", function (e) {
      e.preventDefault();
      $("#chemical_form").submit();
    });

    $("#updateConsumable").on("click", function (e) {
      e.preventDefault();
      $("#consumables_form").submit();
    });

    $("#chemical_form").submit(function (e) {
        if (!$("#chemical_name").val()) {
          e.preventDefault();
          alert("Please fill the chemical name first");
        }
    });

    $("#consumables_form").submit(function (e) {
        if (!$("#consumable_name").val()) {
          e.preventDefault();
          alert("Please fill the consumable name first");
        }
    });

    $("#location_form").submit(function (e) {
        if (!$("#location_name").val()) {
          e.preventDefault();
          alert("Please fill the location name first");
        }
    });

    $("#storage_form").submit(function (e) {
        if (!$("#storage_name").val()) {
          e.preventDefault();
          alert("Please fill the storage name first");
        }
    });

    $("#hazard_form").submit(function (e) {
        if (!$("#hazard_name").val()) {
          e.preventDefault();
          alert("Please fill the hazard name first");
        }
    });

    $("#chemical_location_form").submit(function (e) {
        if (!$("#chemical_location_name").val()) {
          e.preventDefault();
          alert("Please fill the chemical location first");
        }
    });

    $("#storage_category_form").submit(function (e) {
        if (!$("#storage_category_name").val()) {
          e.preventDefault();
          alert("Please fill the chemical location first");
        }
    });

    $("#movements_from").submit(function (e) {
        var msg = ''
        if ($("#qty").val() && $("#qty").val() <=0 ){
            msg += "Please add postive number";
        }

        if (!$("#productId").val() || !$("#qty").val()) {
          msg += "Please fill the missing fields\n";
        }

        if (!$("#fromLocation").val() && !$("#toLocation").val()) {
          msg += "Please choose a warehouse\n";
        }

        if (
          parseInt($("#fromLocation option:selected").attr("data-max")) <
          parseInt($("#qty").val())
        ) {
          msg +=
            "Please Note that the quantity in the warehouse must be less than ( " +
            $("#fromLocation option:selected").attr("data-max") +
            " )";
        }

        if (msg) {
          e.preventDefault();
          alert(msg);
        }
    });
    
    if ($("#productId").val()) {
        enableOptions();
    }

    function enableOptions()
    {
        $("#qty").prop("disabled", false);
        $("#toLocation").prop("disabled", false);
        $("#fromLocation").prop("disabled", false);
    }

    function disableOptions()
    {
        $("#qty").prop("disabled", "disabled");
        $("#toLocation").prop("disabled", "disabled");
        $("#fromLocation").prop("disabled", "disabled");
    }

    function ajaxCall(table){
      $.ajax({
        data: {
          productId: $("#productId").val(),
          location: $("#fromLocation").val(),
        },
        type: "POST",
        url: table,
      }).done(function (data) {
        $.each(data, function (index,value){
            $("#fromLocation").append(
              $("<option>", {
                value: index,
                text: index,
                "data-max": value.qty,
              })
            );
        });

      });
    }
   /*  function ajaxCallLocation() {
      $.ajax({
        data: {
          location: $("#location_name").val(),
        },
        type: "POST",
        url: "dub-locations",
      }).done(function (data) {
        if(data.output) {
          console.log(data.output)
        } else {
          alert("This Name is already used, please choose other one.");
          return false;
        }
      });
    } */


});
