"use strict";


/* -------------------------------------------------- Criar horaio inscriçoes ------------------------------------------------------------------------------- */

var weekdays= ['Horas/Dias','SEGUNDA','TERÇA','QUARTA','QUINTA','SEXTA','SÁBADO'];

function buildSchedule(horary){
    buildEmptySchedule("8:00", "20:00");
    insertClasses(horary);
}

function buildEmptySchedule(start, end){
    var table= document.getElementById("tabelaSchedule");
    var header= table.insertRow(-1);
    var headerHTML= "";
    for(var i=0; i<weekdays.length; i++){
        headerHTML+= "<th>" + weekdays[i] + "</th>";
    }
    header.innerHTML= headerHTML;

    var numLines= minutesBetween2Hours(start, end) / 30;
    //l -> line       
    for(var l = 0; l<numLines; l++){
        var linha= table.insertRow(-1);
        linha.setAttribute("id", l);
        var corpolinha="";
        //c-> column
        for(var c=0; c<weekdays.length; c++){
            if (c == 0) corpolinha+= "<td id="+ start + ">" + start +"-"+ addMinutes(start, 30) + "</td>";
            else corpolinha+= "<td id=" + l +":"+c + "></td>";
        }
        linha.innerHTML= corpolinha;
        var start = addMinutes(start, 30);
    }
}


function insertClasses(scheduleDict){
    var subjectColor = {};
    var lstColors= ["rgb(255, 209, 115)", "rgb(183, 244, 110)", "rgb(97, 183, 207)", "rgb(118, 115, 217)", "rgb(150, 107, 214)", "rgb(231, 104, 171)", "#A8FFFF", "#87CEFA", "#AFEEEE", "rgb(255, 115, 115)"];
    
    for (var weekday in scheduleDict){
        insertClassesInWeekday(weekday, scheduleDict[weekday], subjectColor, lstColors);
    }

    //organizar todos os divs por linha
    var linhas_divs = {};
    var allDivs= document.getElementsByClassName("inline");
    for(var d=0; d<allDivs.length; d++){
        var linhaDoDiv= allDivs[d].id.split("|")[0];
        if (linhaDoDiv in linhas_divs){
            linhas_divs[linhaDoDiv] = linhas_divs[linhaDoDiv].concat(allDivs[d]);
        }else{
            linhas_divs[linhaDoDiv]= [allDivs[d]];
        }
    }

    //por os divs com a altura da td para cada linha
    for (var linha in linhas_divs){
        var linha_divs= linhas_divs[linha];
        var tdHeight= linha_divs[0].parentElement.offsetHeight;
        linha_divs[0].style.borderLeft = "1px solid black";
        for (var i = 0; i<linha_divs.length; i++){
            linha_divs[i].style.height= tdHeight + "px";
        }
    }
}

function insertClassesInWeekday(weekdaySTR, classes, dicSubjectColor, lcolors ){
    for(var a= 0; a<classes.length; a++){
        // same subjects must have the same color
        if (classes[a][2] in dicSubjectColor){
            var color= dicSubjectColor[classes[a][2]];
        }
        else {
            var color= lcolors.shift();
            dicSubjectColor[classes[a][2]] = color; //add to dicSubjectColor the new subject
        }

        //the block/cell position
        var linha= document.getElementById(classes[a][0]).parentElement.id; //the time that the class starts
        var weekday= weekdays.indexOf(weekdaySTR);

      
        //adicionar aula (set of blocks)
        var numBlocks= hourToMinutes(classes[a][1])/30; //duration
        for(var b=0; b<numBlocks; b++){ 
            var td = document.getElementById((+(linha)+b) + ":" + weekday); 
            var div= document.createElement("Div"); 
            //assim todos os divs da mesma aula tem a mesma class
            div.setAttribute("class", "inline "+ linha+"/"+weekday+"/"+classes[a][4]);
            div.setAttribute("style", "background-color:" + color);
            td.appendChild(div);
            var columnDivInBlock = td.childElementCount-1; //esta na ultima posiçao da td pq foi inserido agora

            if (b == 0) { //class start here
                div.innerHTML= "<span class=subject>" + classes[a][2] + "</span> " + classes[a][3] +" "+ classes[a][4];
                div.style.borderTop= "1px solid black";
                var blocksInsideTd= td.children;
                var width = (100/(blocksInsideTd.length)) + "%" ;
                //se a largura de um div foi alterado entao a largura de todos os divs desse block tem q ser alterados
                for (var d=0; d<blocksInsideTd.length; d++){
                    blocksInsideTd[d].style.width= width; 
                    
                    //incluindo os divs de outros blocks que pertencem a mesma aula
                    if (d != blocksInsideTd.length-1){ //nao vale apena modificar a aula q estou a inserir agora
                        var BlockClass= blocksInsideTd[d].getAttribute("class").split(" ")[1];
                        var allBlocksWithCass= document.getElementsByClassName(BlockClass); //aula
                        for (var i=0; i<allBlocksWithCass.length; i++){
                            allBlocksWithCass[i].style.width= width;
                            
                        }
                        var blockID= allBlocksWithCass[0].id.split("|")
                        var blockHaEsquerdaID= blockID[0]+"|"+blockID[1]+"|"+(parseInt(blockID[2])-1)
                        var blockHaEsquerda= document.getElementById(blockHaEsquerdaID) //retangulo a esquerda
                        if (blockHaEsquerda != null) {
                            var BlockClass= blockHaEsquerda.getAttribute("class").split(" ")[1];
                            var allBlocksWithCass= document.getElementsByClassName(BlockClass);
                            for (var i=0; i<allBlocksWithCass.length; i++){
                                allBlocksWithCass[i].style.width= width;
                                
                            }
                        }
                    }
                }
                div.setAttribute("id", +(linha)+b+"|"+weekday+"|"+columnDivInBlock);
            }else{
                //todos os divs da mesma aula tem q ter a mesma largura
                var blockAbove= document.getElementById((+(linha)+(b-1) + ":" + weekday));
                var columnDivInBlockAbove = blockAbove.childElementCount-1
                var divAbove= blockAbove.children[columnDivInBlockAbove];
                var widthAbove= divAbove.style.width;
                div.style.width= widthAbove;
              
                //por o div que acabei de criar alinhado verticalmente com os restantes divs pertencentes a mesma aula                
                while (columnDivInBlock < columnDivInBlockAbove){
                    var emptyBlock= document.createElement("Div");
                    emptyBlock.style.width= widthAbove;
                    emptyBlock.setAttribute("class", "inline "+ linha+"/"+weekday+"/"+classes[a][4]+ " empty");
                    td.insertBefore(emptyBlock, td.children[td.childElementCount-1]);
                    emptyBlock.setAttribute("id", +(linha)+b+"|"+weekday+"|"+columnDivInBlock);
                    columnDivInBlock= td.childElementCount-1;
                }

                div.setAttribute("id", +(linha)+b+"|"+weekday+"|"+columnDivInBlock);
            }

            if( b == numBlocks-1){
                div.style.borderBottom= "1px solid black";
            }
        }
    }    
}

function minutesBetween2Hours(start, end){
    return hourToMinutes(end) - hourToMinutes(start);
}

function hourToMinutes(hour){
    var lhour= hour.split(":");
    return lhour[0]*60 + parseInt(lhour[1]);
}

function addMinutes(hour, minutes){
    var totalmin= hourToMinutes(hour) + minutes;
    return Math.floor(totalmin / 60) + ":" + ((totalmin % 60 == 0) ? "00" : totalmin % 60); //hh:mm
}

//aula -> set of blocks
//block -> set of divs (>1 div se houver sobreposiçoes), é a td
//div -> empty or not



/* -------------------------------------------------- choose lessons and horario atual ------------------------------------------------------------------------------- */
function criarHorario(semestre) {
    console.log(semestre)

    //todas os botoes das turmas q foram "activados" num semestre
    var allTurmasEscolhidas = document.querySelectorAll("button[data-" + semestre + "=true]");

    var lstLessons = []
    for (var i = 0; i < allTurmasEscolhidas.length; i++) {
      var turma = allTurmasEscolhidas[i].getAttribute("data-lessons")
      var turmaLessons = turma.split("|").slice(0, -1);
      lstLessons = lstLessons.concat(turmaLessons)
    }
    //reset pq os valores do dic tem q estar ordenados
    document.getElementById("tabelaSchedule").innerHTML= "";

    var dicDiasDaSemena= formatarOrdenarLstLessons(lstLessons)
    buildSchedule(dicDiasDaSemena);
}


function formatarOrdenarLstLessons(lstLessons){
    /*
    lstLessons:
    horario: exemplo1-> ['QUARTA,11:00,1:00,Redes de Computadores (LTI),T,1.5.67', 'QUINTA,09:30,1:00,Redes de Computadores (LTI),T,2.1.14', 
    'QUINTA,08:00,1:30,Redes de Computadores (LTI),TP,2.1.15', 'TERÇA,09:00,2:00,Segurança Informática,T,2.1.12', 
    'TERÇA,11:00,1:30,Segurança Informática,TP,2.1.11']
    calendario: exemplo2-> ["QUARTA,08:00,Contabilidade Geral I,PL,13", "SEGUNDA,09:00,Introdução às Tecnologias Web,T,21", "SEGUNDA,11:30,Introdução às Tecnologias Web,TP,25"]

    ensure:
    exemplo1->     var scheduleDict= {
                        "QUARTA" : [["11:00", "1:00", "RC", "T", "1.5.67"]],
                        "QUINTA"   : [["8:00", "1:30", "RC", "TP", "2.1.15"], ["9:30", "1:00", "RC", "T", "2.1.14"]], 
                        "TERÇA"  : [["9:00", "2:00", "SI", "T", "2.1.12"], ["11:00", "1:30", "SI", "TP", "2.1.11"]]
                    }
    exemplo2->      var scheduleDict= {
                        "Quarta" : [["8:00", "CGI", "PL", "13"]],
                        "Segunda"   : [["9:00", "IT", "T", "21"], ["11:30", "IT", "TP", "25"]]
                    }
    */
    console.log(lstLessons)

    //percorrer a lista com todas as lessons
    var lstlesson = []
    for (var i = 0; i < lstLessons.length; i++) {
      var lesson = lstLessons[i].split(",")
        if (lesson.length == 6){
            lesson[1] = format(lesson[1])
            lesson[3] = getSigla(lesson[3])
        }else{
            lesson[0] = lowerCaseAllWordsExceptFirstLetters(lesson[0])
            lesson[1] = format(lesson[1])
        }
      lstlesson.push(lesson)
    }

    var scheduleDict = {}

    for (var i = 0; i < lstlesson.length; i++) {
      if (lstlesson[i][0] in scheduleDict) {
        scheduleDict[lstlesson[i][0]].push(lstlesson[i].slice(1, lstlesson[i].length))
      } else {
        scheduleDict[lstlesson[i][0]] = [lstlesson[i].slice(1, lstlesson[i].length)]
      }
    }
    console.log(scheduleDict)

    // Importante: para o mesmo dia de semana, as aulas TEM QUE ESTAR POR ORDEM!! (by time) 
    // tenho q formatar primeiro a hora e depois ordenar
    for (var key in scheduleDict) {
      scheduleDict[key] = scheduleDict[key].sort(function (a, b) {
        return maior(a[0], b[0])
      });
    }

    console.log(scheduleDict)
    return scheduleDict;
}


function lowerCaseAllWordsExceptFirstLetters(string) {
    return string.replace(/\w\S*/g, function (word) {
        return word.charAt(0) + word.slice(1).toLowerCase();
    });
}

  function maior(str1, str2){
    console.log(str1 + " " + str2)
    var res;
    if ((str1.length + str2.length) == 9 ){
    //"10:00" > "9:30"
    console.log(! (str1 > str2))
    res= (! (str1 > str2))
    }
    else{
      res= str1 > str2
    }

    if (res){
      return 1
    }else{
      return -1
    }
  }

  function format(hour) {
    //ex: 08:00 -> 8:00
    if (hour[0] == "0") {
      hour = hour.substring(1)
    }
    return hour
  }


  function getSigla(umaString) {
    console.log(umaString)
    var lista = umaString.split(" ")
    var sigla = ""
    for (var i = 0; i < lista.length; i++) {
      if (lista[i].length > 3 && lista[i].indexOf('(') <= -1) {
        sigla = sigla + lista[i][0]
      }else if (lista[i].indexOf('I') > -1 && lista[i].indexOf('(') <= -1) { //(LTI) / PII
                sigla = sigla + lista[i]
      }else if (lista[i].length == 1) { //(LTI) / PII
        sigla = sigla + lista[i]
      
      }
    }
    console.log(sigla)
    return sigla
  }

/* -------------------------------------------------- choose lessons ------------------------------------------------------------------------------- */
function marcado(obj,id) {
    var semestre= id.split("|")[0];
    console.log(semestre)
    obj.style.border= "2px solid black";
    obj.style.opacity= "0.8";
    obj.classList.remove("w3-khaki");
    obj.style.boxShadow= "none";
    obj.style.backgroundColor = "beige";
    obj.setAttribute('data-'+semestre, true)
    var e = document.getElementById(id).children;
    for (var i= 0; i< e.length; i++){
        if (e[i] != obj){
            e[i].style.border= "none";
            e[i].style.opacity= "1";
            e[i].style.boxShadow= "1px 2px 6px 1px #1b3680";
            e[i].classList.add("w3-khaki");
            e[i].setAttribute('data-'+semestre, false) 
        }
    }  
}


//barra de progresso
function move() {
    var totalAllLessons = document.getElementsByClassName("turmas").length;
    var allTurmasEscolhidas1sem = document.querySelectorAll("button[data-1sem=true]").length;
    var allTurmasEscolhidas2sem = document.querySelectorAll("button[data-2sem=true]").length;

    var escolhidos= allTurmasEscolhidas1sem + allTurmasEscolhidas2sem
    var aumento= 100/totalAllLessons;
    console.log(totalAllLessons)

    var elem = document.getElementById("myBar");   
    var prog = document.getElementById("percent");
    var width= prog.innerHTML; 

    console.log(aumento)
    console.log(escolhidos)
    width = escolhidos * aumento; 
    console.log(width)
    elem.style.width = width + '%'; 
    prog.innerHTML = width.toFixed(2);
    if (width >= 100) {
      elem.style.backgroundColor= "green";
      elem.style.color= "white";
      elem.innerHTML= "Finalize a inscriçao! ";
    }

  }


/* -------------------------------------------------- inscriçoes subject ------------------------------------------------------------------------------- */

function prepareTRs(ano){
	minicToggleAno(ano)
}


function minicToggleAno(ano){
	$.each($("tr[data-ano='"+ano+"toggle']"), function () {
		if ($(this).is(":visible")){
			$(this).hide();
			var val= $(this)[0].getAttribute('value')
			$.each($("tr[data-mcName='"+val+"']"), function () {
				$(this).hide();
			});
		}else{
            console.log(121)
			$(this).show();
		}
	});
}


function minicToggle(mcName){
	$.each($("tr[data-mcName='"+mcName+"']"), function () {
		$(this).toggle();
	});
}

/* -------------------------------------------------- nav bar shadow ------------------------------------------------------------------------------- */


window.onscroll = function() {myFunction()};
    
function myFunction() {
	if (document.body.scrollTop > 15|| document.documentElement.scrollTop > 15) {
		document.getElementById("bar_nav").classList.add("nse-top-navigation--with-bottom-shadow");
	} else {
		document.getElementById("bar_nav").classList.remove("nse-top-navigation--with-bottom-shadow");
	}
}


/* -------------------------------------------------- calendario registar presenças ------------------------------------------------------------------------------- */

"use strict";

var meses = ["Janeiro","Fevereiro","Março","Abril","Maio","Junho","Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"];
var diasDaSemana= ['Domingo','Segunda','Terça','Quarta','Quinta','Sexta','Sábado'];



//clicar nas setas ou botao hoje
function calend(triger, dicAulas){
    var MesAnoDeHojeManipuladaSTR= "/09/2018";
    var DiaDeHojeCerto= new Date().getDate();
    var DataDeHojeManipuladaSTR= DiaDeHojeCerto + MesAnoDeHojeManipuladaSTR;
    var d = DataDeHojeManipuladaSTR.split("/");
    var DataDeHojeManipulada= new Date(d[2], parseInt(d[1])-1, d[0]);
    


    if (triger == undefined){
        var mes = DataDeHojeManipulada.getMonth();
        var ano = DataDeHojeManipulada.getFullYear();

    }else{
        var mesActual= meses.indexOf(document.getElementById("mes").innerHTML.split("<br>")[0]);
        var anoActual= parseInt(document.getElementById("ano").innerHTML);
    
        if (triger == "anterior"){
            if (mesActual == 0) {
                var mes= 11;
                var ano= anoActual - 1;
            }else{
                var mes= mesActual - 1;
                var ano= anoActual;
            }
        }

        if (triger == "proximo"){
            if (mesActual == 11) {
                var mes= 0;
                var ano= anoActual + 1;
            }else{
                var mes= mesActual + 1;
                var ano= anoActual;
            }
        }
    }

    buildCalendar(mes, ano, DataDeHojeManipulada);
    inserirAulas(dicAulas,mes,ano);
    responsiveModel();

}


function buildCalendar(mes, ano, DataDeHojeManipulada){
    console.log(mes + "," + ano);
    var feriados = ['1/1', '19/4', '21/4', '25/4', '1/5', '10/6', '20/6', '15/8', '5/10', '1/11', '1/12', '8/12', '25/12']
    var ferias= [["4/3/"+ano, "6/3/"+ano], //carnaval
                ["17/4/"+ano, "23/4/"+ano]] //pascoa

    document.getElementById("mes").innerHTML= meses[mes] + "<br> <span id='ano' style='font-size:13px'>" + ano + "</span>";
    var table = document.getElementById("tabelaCalend");
    table.innerHTML = ""; //reset
    var linhaDiasDaSemana= table.insertRow(-1);
    for (var i= 0; i<diasDaSemana.length; i++){
        linhaDiasDaSemana.innerHTML += "<td class='celulaDiasDaSemana'>" + diasDaSemana[i] + "</td>";
    }

    var preencher = false;
    var contDia= 1;

    while (contDia <= getDiasNumMes(mes, ano)){

        var corpoTab= table.insertRow(-1);
        for(var diaDeSemana=0; diaDeSemana<diasDaSemana.length; diaDeSemana++){ //para cada dia da semana
            if (getDiaDaSemana(1, mes, ano) == diaDeSemana && preencher == false)(
                preencher = true
            )
            if(contDia > getDiasNumMes(mes, ano)) preencher = false;

            //por os numeros
            if(preencher){
                var dma= contDia + "/" + mes + "/" + ano
                var dmaCheck= contDia + "/" + (mes+1) + "/" + ano
                var dm= contDia + "/" + (mes+1)
                console.log(dma)

                var td = document.createElement("td")
                td.setAttribute("id", contDia)
                td.setAttribute("data-DMA", dma)
                td.setAttribute("class", "celulaDias")

                if (is_dateBetweenOrEqual2dates("17/09/2018", "19/12/2018", dmaCheck)){
                    td.setAttribute("data-aulas", "true")
                    td.setAttribute("data-aulas1sem", "true")
                }else if (is_dateBetweenOrEqual2dates("18/02/2019", "31/05/2019", dmaCheck)){
                    td.setAttribute("data-aulas", "true")
                    td.setAttribute("data-aulas2sem", "true")
                }else{
                    td.setAttribute("data-aulas", "false")
                }
                
                if(is_ferias(dmaCheck, ferias)){
                    td.setAttribute("bgcolor", 'blanchedalmond')
                    td.setAttribute("data-aulas", "false")
                }else if (feriados.indexOf(dm) >= 0){
                    td.setAttribute("bgcolor", 'beige')
                    td.setAttribute("data-aulas", "false")
                }

                if (mes == DataDeHojeManipulada.getMonth() && contDia == DataDeHojeManipulada.getDate()){ //se for o dia de hoje
                    td.innerHTML= "<div class='diaDeHoje'>" + contDia +"</div><div class='boxAulas'></div>"
                }else{
                    td.innerHTML= "<div>" + contDia +"</div><div class='boxAulas'></div>"
                }
                //console.log(td)
                corpoTab.appendChild(td)

                contDia++;
            }else{
                corpoTab.insertCell(diaDeSemana); //celula vazia
            }
        }
    }
}


function is_dateBetweenOrEqual2dates(dateFrom, dateTo, dateCheck){
    //format of dates: "dd/mm/yyyy", mm-> janeiro : 1
    var d1 = dateFrom.split("/");
    var d2 = dateTo.split("/");
    var c = dateCheck.split("/");

    var from = new Date(d1[2], parseInt(d1[1])-1, d1[0]);  // -1 because months are from 0 to 11
    var to   = new Date(d2[2], parseInt(d2[1])-1, d2[0]);
    var check = new Date(c[2], parseInt(c[1])-1, c[0]);

    return check >= from && check <= to
}

function is_ferias(date, ferias){
    //format of date: "dd/mm/yyyy", mm -> janeiro : 1
    //format of ferias: [["4/3/201*", "6/3/201*"], ["17/4/201*", "23/4/201*"]], mm -> janeiro : 1
    for(var i=0; i<ferias.length; i++){
        var lstFerias= ferias[i]
        if (is_dateBetweenOrEqual2dates(lstFerias[0], lstFerias[1], date)){
            return true
        }
    }
    return false
}

function inserirAulas(dicAulas,mes,ano){
    var dicSubjectColor= {}
    var lstColors= ["rgb(255, 209, 115)", "#4CAF4C", "rgb(97, 183, 207)", "rgb(118, 115, 217)", "rgb(150, 107, 214)", "rgb(231, 104, 171)", "#A8FFFF", "#87CEFA", "#AFEEEE", "rgb(255, 115, 115)"];

    for (var sem in dicAulas) {
        var dicAulasSem= dicAulas[sem]
        for (var diaDaSemana in dicAulasSem) { //para cada dia da semana 
            var lstAulas= dicAulasSem[diaDaSemana] //as aulas que tenho nesse dia de semana

            var HTMLaulas="";

            for (var a= 0; a < lstAulas.length; a++){ 
                //criar o html das aulas que vou ter nesse dia de semana
                if (lstAulas[a][1] in dicSubjectColor){
                    var color= dicSubjectColor[lstAulas[a][1]];
                }
                else {
                    var color= lstColors.shift();
                    dicSubjectColor[lstAulas[a][1]] = color; //add to dicSubjectColor the new subject
                }

                HTMLaulas += "<div data-sem="+sem+" data-nomeSubj='" + lstAulas[a][1] + "' onclick='aulaEscolhida(this)' class='aulas' style='background-color:" + color + ";'><span style='font-weight: bold;'>"+ lstAulas[a][0] +"</span>  <span>"+ getSigla(lstAulas[a][1]) + "</span> <span>"+ lstAulas[a][2] + lstAulas[a][3] +"</span></div>";
            }

            var coluna= colunaDeUmDiaDeSemana(diaDaSemana, mes, ano); //obtenho todos os dias q calham nesse dia de semana
            //console.log(coluna)
            for (var d = 0; d<coluna.length; d++){ //para cada um desses dias
                var dia= document.getElementById(coluna[d].toString());
                //console.log(dia)
                var attribute= "data-aulas" + sem
                if (dia.getAttribute("data-aulas") == "true" && dia.getAttribute(attribute) == "true"){
                    //o dia/celula so tem link se tiver aulas e se nao for um feriado
                    var link = "<a class='link' style='display:none' onclick='showAulas(this)'>+<span id='cont" + coluna[d] + "'></span> more</a>";
                    dia.children[1].innerHTML = HTMLaulas + link; //por as aulas nesse dia
                }
            }
        }
    }

}


function getDiasNumMes(mes, ano){
    //mes+1 por causa do indice ex: março= 2+1 
    // ex: (março) getDiasNumMes(3, 2019) -> 31
    return new Date(ano, mes+1,0).getDate();
}

function getDiaDaSemana(dia, mes, ano){
    return new Date(ano, mes, dia).getDay();
}

function colunaDeUmDiaDeSemana(diaDaSemanaSRT,mes,ano){
    //ex: colunaDeUmDiaDeSemana("Terça",2,2019) --> [5, 12, 19, 26]   (2 é março)
    var diaDaSemana= diasDaSemana.indexOf(diaDaSemanaSRT);
    var coluna= [];
    for (var dia = 1; dia<=getDiasNumMes(mes, ano); dia++)
        if (diaDaSemana == getDiaDaSemana(dia, mes, ano))
            coluna.push(dia);
    return coluna;
}

function showAulas(link){
    //tabela
    var boxAulas = link.parentElement;
    var diaMesAno= boxAulas.parentElement.getAttribute("data-DMA").split("/");
    var diaDaSemana= getDiaDaSemana(diaMesAno[0], diaMesAno[1], diaMesAno[2]);

    //modal
    var modalAulas = document.getElementById("showAulas"); 
    modalAulas.setAttribute("data-DMA", diaMesAno[0] + "/"+diaMesAno[1]+ "/"+diaMesAno[2]);
    var HTMLheader= "<div class='headerModal'><div> " + diasDaSemana[diaDaSemana] + ", " + diaMesAno[0] + " " + meses[diaMesAno[1]] + 
    "<span onclick=document.getElementById('modalContent').style.display='none' class='closeButton'>&times;</span></div></div>";
    modalAulas.innerHTML = HTMLheader;
    var lst = boxAulas.children;
    for (var i = 0; i<lst.length -1; i++){
        var aula = lst[i].cloneNode(true);
        aula.style.display = "block";
        modalAulas.appendChild(aula);
    }
    document.getElementById("modalContent").style.display = "block";

}




function aulaEscolhida(aula){
    var div= aula.parentElement;

    //se escolher a aula no modal
    if (div.id == "showAulas"){
        var DMA= div.getAttribute("data-DMA");
    }
    //se escolher a aula do calendario
    else{
        var DMA= div.parentElement.getAttribute("data-DMA");
    }
    //dma, mm -> janeiro : 0
    console.log(DMA, aula.children[0].innerHTML, aula.children[1].innerHTML, aula.children[2].innerHTML)

    $.ajax({
        type: "POST",
        url: 'presencas_registar',
        data: JSON.stringify({
          'sem': aula.getAttribute("data-sem"),
          'cadeiraEscolhida': aula.getAttribute("data-nomesubj"),
          'turmaEscolhida': aula.children[2].innerHTML
        }),
        success: function (data) {
            console.log(data)

          if (data['message'] == "success") {
            document.getElementById("option1Header").innerHTML= "<span class='fa fa-navicon'>&nbsp;</span>1. Escolher novamente"
            var opcao2 = document.getElementById("option2");
            $("#option2").css("display", "block");
            $("#option1").toggle();

            var lstDMA= DMA.split("/")
            var aulaEscolhidaTxt = ""
            var diaDaSemana= getDiaDaSemana(lstDMA[0], lstDMA[1], lstDMA[2])
            var date= lstDMA[0] +"/"+ (parseInt(lstDMA[1])+1) + "/" + lstDMA[2]
            aulaEscolhidaTxt += "<h5>Dia: " + diasDaSemana[diaDaSemana] + ", " + date + "</h5>"
            aulaEscolhidaTxt += "<h5>Hora: " + aula.children[0].innerHTML + "</h5>"
            var nomeSubj= aula.getAttribute("data-nomesubj")
            aulaEscolhidaTxt += "<h5>Cadeira: <span id='cadeiraEscolhida'>" + nomeSubj + "</span> ("+aula.children[1].innerHTML + ") </h5>"
            var turmaEscolhida= aula.children[2].innerHTML
            aulaEscolhidaTxt += "<h5>Turma: " + turmaEscolhida + "</h5>"
            opcao2.innerHTML = aulaEscolhidaTxt;

            //tabela
            var table= document.createElement("Table"); 
            table.setAttribute("id", 'students_table')
            table.setAttribute("class", 'table')
            opcao2.appendChild(table)

            var listAlunos= data['alunos']
            if (listAlunos.length == 0){
                table.innerHTML = "Esta vazia :("

            }else{
                var tableHeader= table.insertRow(-1);
                tableHeader.innerHTML = "<th>Número</th><th>Nome</th><th></th>"

                for(var l = 0; l<listAlunos.length; l++){
                    var linha= table.insertRow(-1);
                    linha.innerHTML = "<td>"+ listAlunos[l][0] +"</td><td>"+ listAlunos[l][1] +"</td><td><div class='checkbox'><label><input type='checkbox' name='presenca' value="+ listAlunos[l][0] +"></label></div></td>"
                }

                opcao2.innerHTML += "<button onclick=guardarPresenças('"+ diasDaSemana[diaDaSemana]+"','"+ date +"','"+ turmaEscolhida+ "') style='float: right' class='btn btn-lg btn-primary'>Submit</button>"
            }

            console.log(nomeSubj + ", " + date + ", " + turmaEscolhida)
            //obter os dados guardados temporariamente
            if(localStorage.getItem(nomeSubj + ", " + date + ", " + turmaEscolhida) != undefined){
                var alunosEscolhidos = JSON.parse(localStorage.getItem(nomeSubj + ", " + date + ", " + turmaEscolhida))
                for (var i = 0; i<alunosEscolhidos.length; i++){
                    $("input[value='"+alunosEscolhidos[i]+"']").prop("checked", true );
                }
            }

          } else {
            alert("Ocorreu um problema, volte a tentar.")
          }
        }
      });
}

function guardarPresenças(week_day, date, turmaEscolhida){
    var alunosEscolhidos= [];
    var alunosNaoEscolhidos= [];
    $.each($("input[type='checkbox']"), function () {
        if ($(this).is(":checked")){
            alunosEscolhidos.push($(this).val())
        }else{
            alunosNaoEscolhidos.push($(this).val())
        }
    });
    console.log(alunosEscolhidos)
    console.log(alunosNaoEscolhidos)

    var cadeiraEscolhida= document.getElementById("cadeiraEscolhida").innerHTML

    //guardar temporariamente, assim se quizer mudar alguma opçao nao presisa de escolher todo novamente
    var alunosEscolhidosLessonDate= JSON.stringify(alunosEscolhidos);
    localStorage.setItem(cadeiraEscolhida + ", " + date + ", " + turmaEscolhida, alunosEscolhidosLessonDate);
        
    $.ajax({
        type: "POST",
        url: 'presencas_registar',
        data: JSON.stringify({
        'alunosEscolhidos': alunosEscolhidos,
        'alunosNaoEscolhidos': alunosNaoEscolhidos,
        'week_day':week_day.toUpperCase(),
        'date':date,
        'cadeiraEscolhida': cadeiraEscolhida,
        'turmaEscolhida': turmaEscolhida
        }),
        success: function (data) {
            console.log(data)
            alert("Presenças guardadas")
        }
    });
}

// ------------------------------ Calendario responsive -----------------------------------------------------
var sizes = [ 
    window.matchMedia("(max-height: 600px)"),
    window.matchMedia("(max-height: 500px)"),
    window.matchMedia("(max-height: 300px)")
]
function responsiveModel(){
    for (var i=0; i<sizes.length; i++){ 
        myFunction(); 
        sizes[i].addListener(myFunction); 
    }
}

function myFunction(){
    var boxAulas = document.getElementsByClassName("boxAulas");
    var lstPrim= []; //as primeiras aulas
    var lstSeg= []; //as segundas aulas
    var lstTer= []; //as terceiras aulas
    for (var i = 0; i<boxAulas.length; i++){
         if (boxAulas[i].children[0] != undefined && boxAulas[i].children[0].className != "link")
            lstPrim.push(boxAulas[i].children[0]);
         if (boxAulas[i].children[1] != undefined && boxAulas[i].children[1].className != "link") 
            lstSeg.push(boxAulas[i].children[1]);
         if (boxAulas[i].children[2] != undefined && boxAulas[i].children[2].className != "link") 
            lstTer.push(boxAulas[i].children[2]);
    }
    
    for (var i = 0; i < lstPrim.length; i++){
        if (sizes[2].matches) lstPrim[i].style.display = "none"; //se for menor q 300px
        else lstPrim[i].style.display = "block"; //se for maior q 300px
    }

    for (var i = 0; i < lstSeg.length; i++){
        if (sizes[1].matches) lstSeg[i].style.display = "none"; //se for menor q 500px
        else lstSeg[i].style.display = "block"; //se for maior q 500px
    }

    for (var i = 0; i < lstTer.length; i++){
        if (sizes[0].matches) lstTer[i].style.display = "none"; //se for menor q 600px
        else lstTer[i].style.display = "block"; //se for maior q 600px
    }

    var lstLink= document.getElementsByClassName("link"); // o link pode ser o seg, ou ter, ...
    for (var i = 0; i < lstLink.length; i++){ //para cada dia em q ha aulas
        var lstAulas = lstLink[i].parentElement.children; //lista de aulas desse dia

        var contHidden = 0;
        for(var j= 0; j < lstAulas.length - 1; j++){ //quantas aulas faltam aparecer, -1 para nao contar com o link
            if (j >= 3) lstAulas[j].style.display = "none"; //nunca aparecem mais do q 3 aulas
            if (lstAulas[j].style.display ==  "none") contHidden++;
        }
        if (contHidden != 0) { //se falta aparecer alguma aula
            var idSpan= lstAulas[lstAulas.length -1].firstElementChild.id;
            document.getElementById(idSpan).innerHTML = contHidden; //atualiza o numero de aulas escondidas
            lstLink[i].style.display = "block"; 
        }else{
            lstLink[i].style.display = "none"; 
        }
    }
    
}



/* ----------------------- Arrastar model aulas ----------------------- */

function dragElement(elmnt) {
    var pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;
    if (document.getElementById(elmnt.id + "header")) {
      /* if present, the header is where you move the DIV from:*/
      document.getElementById(elmnt.id + "header").onmousedown = dragMouseDown;
    } else {
      /* otherwise, move the DIV from anywhere inside the DIV:*/
      elmnt.onmousedown = dragMouseDown;
    }
  
    function dragMouseDown(e) {
      e = e || window.event;
      // get the mouse cursor position at startup:
      pos3 = e.clientX;
      pos4 = e.clientY;
      document.onmouseup = closeDragElement;
      // call a function whenever the cursor moves:
      document.onmousemove = elementDrag;
    }
  
    function elementDrag(e) {
      e = e || window.event;
      // calculate the new cursor position:
      pos1 = pos3 - e.clientX;
      pos2 = pos4 - e.clientY;
      pos3 = e.clientX;
      pos4 = e.clientY;
      // set the element's new position:
      elmnt.style.top = (elmnt.offsetTop - pos2) + "px";
      elmnt.style.left = (elmnt.offsetLeft - pos1) + "px";
    }
  
    function closeDragElement() {
      /* stop moving when mouse button is released:*/
      document.onmouseup = null;
      document.onmousemove = null;
    }
  }



