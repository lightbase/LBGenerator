
//Preencher as tags <legend>
legends = document.getElementsByTagName('legend');
for (var l=1;l<legends.length;l++){
	legend = legends[l];
	lname = legend.parentNode.previousElementSibling.getAttribute('value');
	if (lname == null){
		lname = legend.parentNode.previousElementSibling.previousElementSibling.getAttribute('value');
	}
	legend.innerHTML = lname;
}

//Trocar os atributos "for" dos labels de [descricao] para [nome]:
//Com isso, os atributos "name" dos inputs criados antes também serão mudados.
labels = document.getElementsByTagName('label');
for (var l=0;l<labels.length;l++){
	label = labels[l];
	if(label.parentNode.parentNode.previousElementSibling == '[object HTMLInputElement]' && label.parentNode.parentNode.previousElementSibling.getAttribute('value') != 'multi'){
		nome = label.parentNode.parentNode.previousElementSibling.getAttribute('value');
	}
	else{
		nome = label.parentNode.parentNode.nextElementSibling.getAttribute('value');
	}
	label.setAttribute('for',nome);
	}

//Colocar id nas fieldsets
fieldsets = document.getElementsByTagName('fieldset');
for (var f=1;f<fieldsets.length;f++){
	fieldset = fieldsets[f];
	gpfs = fieldset.parentNode.parentNode;
	gpfsid = gpfs.getAttribute('id')
	if (fieldset.previousElementSibling == '[object HTMLDListElement]'){
		label = fieldset.previousElementSibling.firstChild.firstChild;
	}
	else{
		label = fieldset.previousElementSibling.previousElementSibling.firstChild.firstChild;
	}
	fid = label.getAttribute('for');
	ct = document.getElementById('contador');
	//base_name = document.getElementById('base.nome').getAttribute('value');
	base_name = 'registro';
	if(gpfsid != null){
	 	if(gpfsid.split('.')[0] == base_name){
			fieldset.id = gpfsid + '.campo.' + ct.value + '.' + fid;
			ct.value = parseInt(ct.value) + 1;
		}
		else{
			fieldset.id = base_name + '.' + gpfsid + '.campo.' + ct.value + '.' + fid;
			ct.value = parseInt(ct.value) + 1;
		}
	}
	else{
	 	fieldset.id =  base_name + '.campo.' + ct.value + '.' + fid ;
		ct.value = parseInt(ct.value) + 1;
	}
}

labels = [];
inputs = document.getElementsByTagName('input');
for (var i=0;i<inputs.length;i++){
	input = inputs[i];
	if (input.getAttribute('value') == 'multi'){
		if(input.nextElementSibling == '[object HTMLInputElement]'){
			label = input.nextElementSibling.nextElementSibling.firstChild;
		}
		else{
			label = input.nextElementSibling.firstChild;
		}
		labels.push(label);
		//tirar o input de quem for multivalorado:
		if(input.nextElementSibling == '[object HTMLInputElement]'){
			dd = input.nextElementSibling.nextElementSibling.firstChild.nextElementSibling;
			}
		else{
			dd = input.nextElementSibling.firstChild.nextElementSibling;
		}
		//input.nextElementSibling.removeChild(dd);
		if(dd.parentNode.parentNode.getElementsByTagName('fieldset').length>0){
			dd.firstChild.setAttribute('type','hidden');
			dd.firstChild.setAttribute('value','multivalued');
		}
	}
	else {
		//Mudar os atributos "name" dos inputs criados antes:
		if(input.type != 'hidden' && input.id == '' && input.type != 'button' && input.type!='reset'){
			fs = input.parentNode.parentNode.parentNode.parentNode;
			fsid = fs.getAttribute('id');
			if(fsid != null){
				input.name = fsid + '.campo.' + ct.value + '.' + input.parentNode.parentNode.nextElementSibling.getAttribute('value');
				ct.value = parseInt(ct.value) + 1;
			}
			else{
			 	hidden = input.parentNode.parentNode.nextElementSibling;
				if(hidden.nextElementSibling!=null){
					idsplit = hidden.nextElementSibling.getAttribute('id').split('.');
					idsplit[idsplit.length-1]=null;
				}
				else{
					ct = document.getElementById('contador');
				 	idsplit = ['registro','campo',ct.value+'.']
					ct.value = parseInt(ct.value) + 1;
				}
			 	input.name = idsplit.join('.') + hidden.getAttribute('value');
			}
		}
	}
	//Acrescentar o atributo type="hidden" nos inputs que contém fieldset:
	if (input.parentNode.parentNode.nextElementSibling != null){
		if (input.parentNode.parentNode.nextElementSibling.nextElementSibling =='[object HTMLFieldSetElement]'){
			input.setAttribute('type','hidden');
			input.setAttribute('value','#grupo')
		}
	}
}

//Se o campo tem um grupo de campos, mudar os nome dos inputs criados depois para o id do fieldset:
for (var i=0;i<inputs.length;i++){
	input = inputs[i];
	if(input.parentNode.parentNode.nextElementSibling!=null){
		if(input.parentNode.parentNode.nextElementSibling.nextElementSibling == '[object HTMLFieldSetElement]'){input.name = input.parentNode.parentNode.nextElementSibling.nextElementSibling.id;}
	}
}

//Adicionar o botão [+] nos campos multivalorados:
for (var j=0;j<labels.length;j++){
	label=labels[j];
	dl = label.parentNode;
	dl.insertAdjacentHTML('beforeEnd',
	'<button id="'+j+'" type="button" onClick=create_field(this,this.id)>+</button>'
	);
}

form = document.getElementsByTagName('form')[0].cloneNode(true)
buttons = form.getElementsByTagName('button');

function create_field(elmt2,id){
 	for(var b=0;b<buttons.length;b++){
	 	button = buttons[b];
		if (button.id == id){
		 	elmt = button;
		}
	}

	div = elmt2.parentNode.parentNode;
	ct = document.getElementById('contador');

	//Verificar se tem campos dentro do multivalorado(pode ser um multivalorado simples):
	if(elmt.parentNode.nextElementSibling != null){
	 	if(elmt.parentNode.nextElementSibling == '[object HTMLFieldSetElement]'){
			oldfieldset = elmt.parentNode.nextElementSibling;
		}
		else{
			if(elmt.parentNode.nextElementSibling.nextElementSibling=='[object HTMLFieldSetElement]'){
				oldfieldset = elmt.parentNode.nextElementSibling.nextElementSibling;}
		      	else{oldfieldset = null;}
		}
	}
	else{
	 	oldfieldset = null;
	}

	newfieldset = oldfieldset.cloneNode(true);
	split = oldfieldset.id.split('.');
	if(split.length > 1){
		split[split.length-2] = ct.value;
		newfieldset.id = split.join('.');
		ct.value = parseInt(ct.value) + 1;
	}
	else{
	 	newfieldset.id = oldfieldset.id + '.' + ct.value;
		ct.value = parseInt(ct.value) + 1;
	}


	setupElement(newfieldset);

	function setupElement(element){
		//Mudar os atributos "name" dos inputs criados depois:
		nfchilds = element.childNodes;
		for (var nf=0;nf<nfchilds.length;nf++){
			nfchild = nfchilds[nf];
			if (nfchild == '[object HTMLDivElement]'){
			 	if(nfchild.firstChild == '[object HTMLInputElement]'){
				 	//plusbutton = nfchild.firstChild.nextSibling.firstChild.nextSibling.nextSibling;
				 	//plusbutton.id = ct.value;
					//ct.value = parseInt(ct.value) + 1;
				}
				dls = nfchild.childNodes;
				//Pegar os multivalorados simples(que não são os primeiros)e mudar os inputs
				for(i=0;i<dls.length;i++){
				 	dl = dls[i];
					if(dl == '[object HTMLDListElement]'){
					 	if(dl.lastChild == '[object HTMLButtonElement]'){
						 	input = dl.firstChild.nextElementSibling.firstChild;
							name = input.getAttribute('name');
							n = name.split('.');
							realname = n[n.length-1];
							input.setAttribute('name',element.id+'.campo.'+ct.value+'.'+realname)
							ct.value = parseInt(ct.value) + 1;
						}
					}
				}
			 	if(nfchild.firstChild.firstChild != null){
					input = nfchild.firstChild.firstChild.nextElementSibling.firstChild;
					name = input.getAttribute('name');
					n = name.split('.');
					realname = n[n.length-1];
					input.setAttribute('name', element.id + '.campo.' + ct.value + '.' +realname);
					ct.value = parseInt(ct.value) + 1;
				}
				else{
					input = nfchild.firstChild.nextElementSibling.firstChild.nextElementSibling.firstChild;
					realname = nfchild.firstChild.nextElementSibling.nextElementSibling.getAttribute('value');
					input.setAttribute('name', element.id + '.campo.' + ct.value + '.' +realname);
					ct.value = parseInt(ct.value) + 1;
				}
			}
		}
	}


	innerfieldsets = newfieldset.getElementsByTagName('fieldset');
	for (var ifs=0;ifs<innerfieldsets.length;ifs++){
	 	innerfieldset = innerfieldsets[ifs];
		//innerfieldset.id = innerfieldset.previousElementSibling.previousElementSibling.firstChild.nextElementSibling.firstChild.getAttribute('name');
		innerfieldset.id = innerfieldset.parentNode.getElementsByTagName('dl')[0].firstChild.nextElementSibling.firstChild.getAttribute('name');
		setupElement(innerfieldset);
	}

	newfieldset.insertAdjacentHTML('beforeEnd',
	'<button type="button" onClick=create_field(this,'+id+')>+</button>'
	);
	newfieldset.insertAdjacentHTML('beforeEnd',
	'<button type="button" onClick=remove_field(this)>-</button>'
	);
	newfieldset.insertAdjacentHTML('beforeEnd',
	'<dd><input type="hidden" value="multivalued" name=' + newfieldset.id + '></input></dd>'
	);
	div.appendChild(newfieldset);

}

function remove_field(elmt){

	grandparent = elmt.parentNode.parentNode;
	parent = elmt.parentNode;
	grandparent.removeChild(parent);

}


function validateForm(){
 	validation = true
	if(validation == true){
	 	document.forms['full'].submit();
	}
	return validation;
}
