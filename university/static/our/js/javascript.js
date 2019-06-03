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



/* -------------------------------------------------- Opçoes de jogo ------------------------------------------------------------------------------- */
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


/* -------------------------------------------------- inscriçoes subject ------------------------------------------------------------------------------- */

function prepareTRs(ano){
	minicToggleAno(ano)
	somCredTroncoComum(ano)
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



//nao pode haver cadeiras opcionais no tronco comum 
function somCredTroncoComum(ano){
    var soma= 0
    console.log("tr[data-mcName='"+ano+"principais']")
	$.each($("tr[data-mcName='"+ano+"principais']"), function () {
        console.log($(this))
		//soma += $(this)
		soma += parseInt($(this).children()[3].getAttribute('value'))
	});
	document.getElementById(ano+"credNecessPrinc").innerHTML= soma
}



function minicToggle(mcName){
	$.each($("tr[data-mcName='"+mcName+"']"), function () {
		$(this).toggle();
	});
}
