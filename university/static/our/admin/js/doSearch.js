function DoSearch(id_input, id_table, n_column) {
    var input, filter, table, tr, td, i;
    
    input = document.getElementById(id_input);
    filter = input.value.toUpperCase();
    
    table = document.getElementById(id_table);
    tr = table.getElementsByTagName("tr");
    
    for (i = 0; i < tr.length; i++) {
      td = tr[i].getElementsByTagName("td")[n_column];
      
      if (td) {
        if (td.innerHTML.toUpperCase().indexOf(filter) > -1) {
          tr[i].style.display = "";
        } else {
          tr[i].style.display = "none";
        }
      }
    }
  };