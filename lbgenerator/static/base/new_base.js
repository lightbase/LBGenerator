function addCampo(elmt) {

  	//make child node and its div element
	parentNode = elmt.parentNode;
	new_child = parentNode.getAttribute('id') + '.objeto';
	new_elmt = document.createElement('div');
	new_elmt.setAttribute('id',new_child);

	contador = document.getElementById('contador');
	nome_elemento = parentNode.getAttribute('id');
	nome_elemento = nome_elemento + '.campo';
	nome_elemento = nome_elemento + '.' + contador.value;

	// Incrementar contador
	contador.value = parseInt(contador.value) + 1;

	//HTML CODE
	x=  '     <fieldset class="nested">'
	x+=          '<legend>Campo/Grupo de campos</legend>'
	x+=            '<dl>'
	x+=                '<dt>'
	x+=                    '<label for="'+ nome_elemento  + '.nome"><font><b>Nome: </b></font></label>'
	x+=                 '<input id="'+ nome_elemento + '.nome" name="'+ nome_elemento  + '.nome" type="text" style="width: 15em;"/>'
	x+=		  '<font color="red" id="'+ nome_elemento +'.nome.error" style="display:none"> Preencha este campo!</font>'
	x+=                '</dt>'
	x+=                '<dt>'
	x+=                    '<label for="'+ nome_elemento  + '.descricao" ><font><b>Descrição: </b></font></label>'
	x+=                    '<input id="'+ nome_elemento  + '.descricao" name="'+ nome_elemento  + '.descricao" type="text" style="width: 15em;"/>'
	x+=		  '<font color="red" id="'+ nome_elemento +'.descricao.error" style="display:none"> Preencha este campo!</font>'
	x+=                '</dt>'
	x+=                '<dt>'
	x+=       '<label for="'+ nome_elemento  + '.tipo" ><font><b>Tipo: </b></font></label>'

	x+=       '<select name="'+ nome_elemento  + '.tipo">'
	x+=         '<option value="AlfaNumerico"> Alfa Numerico</option>'
	x+=         '<option value="Documento"> Documento</option>'
	x+=         '<option value="Inteiro"> Inteiro</option>'
	x+=         '<option value="Decimal"> Decimal</option>'
	x+=         '<option value="Moeda"> Moeda</option>'
	x+=         '<option value="AutoEnumerado"> Auto Enumerado</option>'
	x+=         '<option value="Data"> Data</option>'
	x+=         '<option value="Hora">  Hora</option>'
	x+=         '<option value="Imagem"> Imagem</option>'
	x+=         '<option value="Som"> Som</option>'
	x+=         '<option value="Video"> Video</option>'
	x+=         '<option value="URL"> URL</option>'
	x+=         '<option value="Verdadeiro/Falso"> Verdadeiro/Falso</option><br>'
	x+=         '<option value="Texto"> Texto</option><br>'
	x+=         '<option value="Arquivo"> Arquivo</option><br>'
	x+=         '<option value="HTML"> HTML</option><br>'
	x+=         '<option value="Email"> Email</option><br>'
	x+=       '</select>'
	x+=                '</dt>'
	x+=                '<dt>'
	x+=                    '<label for="'+ nome_elemento  + '.indice"><font><b>Indexação: </b></font></label><br>'
	x+=       '<input type="checkbox" class="'+ nome_elemento  + '.indice" name="'+ nome_elemento  + '.indice" value="SemIndice" checked onclick="check(this)">  Sem Índice'
	x+=       '<input type="checkbox" disabled="true" class="'+ nome_elemento  + '.indice" name="'+ nome_elemento  + '.indice" value="Textual">  Textual'
	x+=       '<input type="checkbox" disabled="true" class="'+ nome_elemento  + '.indice" name="'+ nome_elemento  + '.indice" value="Ordenado"> Ordenado'
	x+=       '<input type="checkbox" disabled="true" class="'+ nome_elemento  + '.indice" name="'+ nome_elemento  + '.indice" value="Unico"> Único<br>'
	x+=       '<input type="checkbox" disabled="true" class="'+ nome_elemento  + '.indice" name="'+ nome_elemento  + '.indice" value="Fonetico"> Fonético'
	x+=       '<input type="checkbox" disabled="true" class="'+ nome_elemento  + '.indice" name="'+ nome_elemento  + '.indice" value="Fuzzy"> Fuzzy'
	x+=       '<input type="checkbox" disabled="true" class="'+ nome_elemento  + '.indice" name="'+ nome_elemento  + '.indice" value="Vazio"> Vazio<br>'
	x+=                '</dt>'

	x+=                '<dt>'
	x+=                    '<label for="'+ nome_elemento  + '.multi"><font><b>Multi Valorado: </b></font></label><br>'
	x+=       '<input type="checkbox" name="'+ nome_elemento  + '.multi" value="True">'
	x+=                '</dt>'
	x+=            '</dl>'
	x+=      '<div id="'+ nome_elemento  + '.objeto">';
	x+=         '<button type="button" onclick="addCampo(this)">+</button>'
	x+=         '<a>Criar campo dentro deste</a><br>'
	x+=         '<button id="mahoe" type="button" onclick="removeCampo(this)">-</button>'
	x+=         '<a>Remover este campo</a>'
	x+=      '</div>'

  	//create child node from parent
  	new_elmt.insertAdjacentHTML('afterBegin',x);
  	parentNode.appendChild(new_elmt);
}

function removeCampo(elmt){
 	divelmt = elmt.parentElement.parentElement.parentElement;
	divelmt.innerHTML="";
}

function check(elmt){
    same_class = document.getElementsByClassName(elmt.className)
    if (elmt.value == 'SemIndice'){
        c = elmt.checked
        for (var i=0; i<same_class.length; i++){
            if (same_class[i].value != 'SemIndice'){
                if (c) same_class[i].checked = !c ;
                same_class[i].disabled = c ;
            }
        }
    }
}

//ver tipo da variável
//alert(Object.prototype.toString.call(thing))

function validarDados(){
 	validation = true
	labels = document.getElementsByTagName('label')
	end = labels.length
	for (k=0;k<end;k++){

		attribute = labels[k].getAttribute('for');
		split = attribute.split('.');

		if (split[split.length-1] == 'tipo'){
			continue;
		}

		if (split[split.length-1] == 'indice'){
			continue;
		}

		if (split[split.length-1] == 'multi'){
			continue;
		}

		if (document.getElementById(attribute).value == '' ){
			labels[k].childNodes[0].setAttribute('color','red');
			document.getElementById(attribute + '.error').setAttribute('style','');
			//alert('Preencha o campo ' + split[split.length-1] + '!');
			//return false;
			validation=false;
		}
		else
		{
			labels[k].childNodes[0].setAttribute('color','black');
			//document.getElementById(attribute + '.error').setAttribute('style','display:none');
		}
		if (document.getElementById(attribute).value.indexOf(']]>') >=0 ){
		 	document.getElementById('alert2').setAttribute('style','');
			//alert('Os caracteres "]]>" não são válidos!');
			//return false;
			validation=false;
			break;
		}
		else{
			document.getElementById('alert2').setAttribute('style','display:none')
		}
		if (document.getElementById(attribute).value.indexOf('%') >=0 ){
		 	document.getElementById('alert3').setAttribute('style','');
			//alert('Os caracteres "]]>" não são válidos!');
			//return false;
			validation=false;
			break;
		}
		else{
			document.getElementById('alert3').setAttribute('style','display:none')
		}
		if (document.getElementById(attribute).value.indexOf(' ') >=0 && split[split.length-1] == 'nome'){
			labels[k].childNodes[0].setAttribute('color','red');
			validation=false;
			alert('O nome não pode ter espaços!')
			break;
		}
		else{
			labels[k].childNodes[0].setAttribute('color','black');
		}
		if (document.getElementById(attribute).value.indexOf('\'') >=0 || document.getElementById(attribute).value.indexOf('\"') >=0){
			labels[k].childNodes[0].setAttribute('color','red');
			validation=false;
			alert('Retire as aspas!')
			break;
		}
		else{
			labels[k].childNodes[0].setAttribute('color','black');
		}
		if (isNaN(parseInt(document.getElementById(attribute).value.charAt(0))) == false && split[split.length-1] == 'nome' ){
			labels[k].childNodes[0].setAttribute('color','red');
			validation=false;
			alert('O nome não pode começar com número!')
			break;
		}
		else{
			labels[k].childNodes[0].setAttribute('color','black');
		}
	}

	if (end==8){
		document.getElementById('alert1').setAttribute('style','')
		//alert('A base precisa ter pelo menos um campo!');
		//return false;
		validation=false;
	}

	else{
		document.getElementById('alert1').setAttribute('style','display:none')
	}

	if(validation == true){
	 	document.forms['dados'].submit();
	}
	return validation;
}







