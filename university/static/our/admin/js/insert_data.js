var attributes = ["nome", "genero", "morada", "nif", "cc", "estadoCivil", "ccValidade", "telefone", "telemovel", "emergencia", "email", "profissao", "nacionalidade", "pais", "frequesia", "concelho", "distrito"];

function getFormValues() {
    var formValues = {};

    for(var i = 0; i < attributes.length; i++) {
        var inputId = attributes[i];
        if (inputId == "estadoCivil" || inputId == "genero") {
            formValues[inputId] = $("#" + inputId + ":checked").val();
        } else {
            formValues[inputId] = $("#" + inputId).val();
        }
    }

    return formValues;
}

function addStudent() {
    var formValues = getFormValues();
    console.log(formValues);
}

function addTeacher() {
    var formValues = getFormValues();
    console.log(formValues);
}

$("input").on("keyup", function(){
    var inputWithValues = 0;
    var myInputs = $("input:not([type='submit'])");

    myInputs.each(function(e){
        if ( $(this).val() ) {
            inputWithValues += 1;
        }
    });

    if (inputWithValues == myInputs.length) {
        $("#submit").prop("disabled", false);
    } else {
        $("#submit").prop("disabled", true);
    }
});