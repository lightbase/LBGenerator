
//GLOBALS
containers_ct = parseInt(document.getElementById('containers_ct').value);
xcounter = parseInt(document.getElementById('xcounter').value);
hiddenFieldsList = [] ;
renderedFieldsList = [];
nameConfig = {
	root: 'LB_form',
 	separator: 'campo',
}

formItems = document.getElementById('items_backup').value;
formItems = formItems.replace(/'/g, '"');
formItems = JSON.parse(formItems);

var style = document.getElementById('LB_form-body').getAttribute('style');
document.getElementById('LB_form-body').setAttribute('style', style + 'top:0px; width: 100%; height: 100%;');


function configHandler(object){
	// Configure plus/minus buttons to add/remove fieldsets.

 	if (object.hasOwnProperty('handler')){
	  	if (object.text == '+'){
	  		object.handler = function(){ addFieldSet(this); }
		}
	  	if (object.text == '-'){
	  		object.handler = function(){ removeFieldSet(this); }
		}
	}
	if (object.hasOwnProperty('items')){
		for(var o=0; o<=object.items.length-1; o++){
			configHandler(object.items[o])
		}
	}
}

function configFields(object, parentName){
	// Configure inputs names.	

	var root = nameConfig.root;
	var sep = nameConfig.separator;

	if(parentName == null){

		object.id = [root, sep, xcounter, object.name].join('.');
		object.name = [root, sep, xcounter, object.name].join('.');
		xcounter += 1;
	}
	else{

		object.id = [parentName, sep, xcounter, object.name].join('.');
		object.name = [parentName, sep, xcounter, object.name].join('.');
		xcounter += 1;

		if (! checkItem(parentName, hiddenFieldsList)){
			hiddenFieldsList.push(parentName);
		}
	}

	if (object.hasOwnProperty('items')){

		for(var i=0; i<=object.items.length-1; i++){

			//if (object.items[i].xtype == 'button'){ continue; }
			configFields(object.items[i], object.name)
		}
	}

}

function configAddedFields(config, parentName){
 	//Configure multivalued input names created by button click.

	var split = config.name.split('.');

 	if (parentName == null){

		split[split.length-2] = xcounter;
		xcounter += 1;
		config.id = split.join('.');
		config.name = split.join('.');
	}
	else{

		var slice = split.slice(-3);
		slice[1] = xcounter;
		xcounter += 1;
		var newname = slice.join('.');
	 	config.id = [parentName, newname].join('.');
	 	config.name = [parentName, newname].join('.');

		if (! checkItem(parentName, hiddenFieldsList)){
			hiddenFieldsList.push(parentName);
		}
	}

	if (config.hasOwnProperty('items')){

	 	for (var i=0; i<=config.items.length-1; i++){
		 	//if (config.items[i].xtype == 'button'){ continue; }
		 	configAddedFields(config.items[i], config.name)
		}
	}

	return config
}

//Configure buttons handlers and input names. 
for(var i=0; i<=containers_ct-1; i++){
 	configHandler(formItems[i]);
	configFields(formItems[i], parentName=null);
}

function addFieldSet(elm){

	var container = elm.up('fieldset').up('container');
	var fieldset = elm.up('fieldset');
  	var config = Ext.apply({}, configAddedFields(fieldset.initialConfig));
  	container.add(config);
}

function removeFieldSet(elm){

	var container = elm.up('fieldset').up('container');
	if (container.items.length == 1) return false;
	var fieldset = elm.up('fieldset');
	var remove_items = 0;
	for(var c=0;c<=container.items.items.length-1; c++){
	 	if(container.items.items[c].fieldLabel == fieldset.fieldLabel){
		 	remove_items += 1;
		}
	}

	if(remove_items > 1){
	 	for(var i=0; i<hiddenFieldsList.length; i++){
	 		if (hiddenFieldsList[i] != undefined){
		 		if(hiddenFieldsList[i].indexOf(fieldset.name) >= 0){
			 		delete hiddenFieldsList[i];
				}
			}
		}
		container.remove(fieldset);
	}
}

Ext.onReady(function(){

	for (var ct=0; ct<=containers_ct-1; ct++){

		var elm = document.getElementById(ct);
		if (elm == null) { continue }
		var elmId = '#' + ct.toString();
		$(elmId).empty();

		var container = Ext.create('Ext.container.Container', {
			//renderTo: ct.toString(),
			items: formItems[ct],
			style: {
				left: elm.style.left,
				top: elm.style.top,
				width: elm.style.width,
				position: 'relative',
			}
		});

		renderedFieldsList.push(container);
	}

	$('#LB_form').empty();

	formPanel = Ext.create('Ext.form.Panel', {
		autoScroll: true,
		title: 'Basic Form',
		renderTo: 'LB_form',
		width: '100%',
		height: '100%',
		items: renderedFieldsList,
		buttons: [{
			text: 'Submit',
			scale: 'large',
			handler: function() {
				buildHiddenInputs();
				var form = this.up('form').getForm();
				if (form.isValid()) {
					form.submit({
						waitMsg: 'Saving...',
						url: 'new',
						success: function(fp, o) {
							Ext.Msg.alert('Success', 'Your photo "' + o.result.file + '" has been uploaded.');
						},
						failure: function(form, action) {
							loc = window.location.pathname.split('/');
							base_name = loc[2];
							form_name = loc[4];
							reg_id = JSON.parse(action.response.responseText).reg_id;
							new_loc = '/lb/'+base_name+'/reg/'+form_name+'/view/'+reg_id;
							window.location.href = new_loc;
                    	}
					});
				}
				else{
					 Ext.Msg.alert('Erro', 'Complete os campos corretamente!');
				}
			}
		},{
			text: 'Reset',
			scale: 'large',
			handler: function() {
				var form = this.up('form').getForm();
				form.reset();
			}
		}]
	});
});


function checkItem(item, list){

 	for(var i=0; i<=list.length-1; i++){
	 	if (item == list[i]){
		 	return true
		}
		else{
		 	continue
		}
	}

	return false
}

function buildHiddenInputs(){

	for(var i=0; i<=hiddenFieldsList.length-1; i++){
	 	if (hiddenFieldsList[i]){
			formPanel.add({
				xtype: 'hiddenfield',
				name: hiddenFieldsList[i],
				value: '#grupo'
			});
		}
	}
}





