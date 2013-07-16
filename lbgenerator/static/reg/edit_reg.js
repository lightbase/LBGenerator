
//-----------------------------Globals----------------------------------//

var reg_data = JSON.parse(document.getElementById('reg_data').textContent);
var reg_json = JSON.parse(reg_data.reg_json);
var items_ct = document.getElementById('containers_ct').value
var items_backup = document.getElementById('items_backup').value.replace(/'/g, '"');
var items_backup = JSON.parse(items_backup);
var xcounter = 0;
var elm_ids = new Array();
var hidden_fields = new Array() ;
var nameConfig = {
	root: 'LB_form',
 	separator: 'campo',
}

//-----------------------------Functions----------------------------------//

function addFieldSet(elm, rem){
 	// Function to add multivalued groups/fields.

	var container = elm.up('fieldset').up('container');
	var fieldset = elm.up('fieldset');
  	//var config = Ext.apply({}, fieldset.initialConfig);
  	var config = Ext.apply({}, configAddedFields(fieldset.initialConfig, parentName=null));
  	container.add(config);
}

function removeFieldSet(elm){
 	// Function to remove multivalued groups/fields.

	var container = elm.up('fieldset').up('container');
	if (container.items.length == 1) return false;
	var fieldset = elm.up('fieldset');
	var remove_items = 0;

	for(var c=0;c<=container.items.items.length-1; c++)
	 	if(container.items.items[c].fieldLabel == fieldset.fieldLabel) remove_items += 1;

	if(remove_items > 1){

	 	for (var i=0; i<hidden_fields.length; i++){
	 		if (hidden_fields[i] != undefined){
		 		if (hidden_fields[i].indexOf(fieldset.name) >= 0)
			 		delete hidden_fields[i];
			}
		}

	 	for (var i=0; i<elm_ids.length; i++){
	 		if (elm_ids[i] != undefined){
		 		if (elm_ids[i].indexOf(fieldset.name) >= 0)
			 		delete elm_ids[i]; //<< desnecessário ?
			}
		}
		container.remove(fieldset);
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
	 	if (object.xtype == 'button'){

		 	if(object.text == '+') var btn_name = 'plusButton';
		 	if(object.text == '-') var btn_name = 'minusButton';

			object.id = [parentName, sep, xcounter, btn_name].join('.');
			xcounter += 1;

			if ($.inArray(object.id, elm_ids) == -1)
				elm_ids.push(object.id);

			return true;
		}

		object.id = [parentName, sep, xcounter, object.name].join('.');
		object.name = [parentName, sep, xcounter, object.name].join('.');
		xcounter += 1;

		if ($.inArray(parentName, hidden_fields) == -1)
			hidden_fields.push(parentName);
	}

	if ($.inArray(object.id, elm_ids) == -1)
	 	elm_ids.push(object.id);

	if (object.hasOwnProperty('items')){

		for(var i=0; i<=object.items.length-1; i++)
			configFields(object.items[i], object.name);
	}

}

function configAddedFields(config, parentName){
 	//Configure multivalued input names created by plus-button click.

 	if (parentName == null){

		var split = config.name.split('.');
		split[split.length-2] = xcounter;
		xcounter += 1;
		config.name = split.join('.');
		config.id = split.join('.');
	}
	else{

	 	if (config.xtype == 'button') var split = config.id.split('.');
		else var split = config.name.split('.');

		var slice = split.slice(-3);
		slice[1] = xcounter;
		xcounter += 1;
		var newname = slice.join('.');
	 	config.name = [parentName, newname].join('.');
	 	config.id = [parentName, newname].join('.');

		if ($.inArray(parentName, hidden_fields) == -1)
			hidden_fields.push(parentName);
	}

	if ($.inArray(config.name, elm_ids) == -1)
		elm_ids.push(config.name);

	if (config.hasOwnProperty('items')){

	 	for (var i=0; i<=config.items.length-1; i++)
		 	configAddedFields(config.items[i], config.name);
	}

	return config
}

function configHandler(object){
	// Configure plus buttons to add fieldsets.

 	if (object.hasOwnProperty('handler')){
	  	if (object.text == '+'){
	  		object.handler = function(){ addFieldSet(this); }
		}
	  	if (object.text == '-'){
	  		object.handler = function(){ removeFieldSet(this); }
		}
	}
	if (object.hasOwnProperty('items')){
		for(var o=0; o<object.items.length; o++){
			configHandler(object.items[o])
		}
	}
}

function getLevel(level){

 	lvl = new Array();
 	lvl[0] = 4;
	lvl[1] = level +6;
	if (lvl[level]) return lvl[level];
	else return level +8;
}

function getId(name, level, button){

	for (var i=0; i<elm_ids.length; i++){

		if (!elm_ids[i]) continue ;

		var id_split = elm_ids[i].split('.');
		var lvl = getLevel(level)

		if (button){
			if (id_split[id_split.length-1] == 'plusButton'
			&& id_split.length == lvl
			&& elm_ids[i].indexOf(name) != -1){
				return elm_ids[i];
			}
		}
		else{
			if (id_split[id_split.length-1] == name && id_split.length == lvl ){
				var field_id = elm_ids[i];
				delete elm_ids[i];
				return field_id;
			}
		}
	}
}

function configFileElm(id, file_elm, file_data, field_name){
	var cmp = Ext.getCmp(id)
	cmp.inputEl.dom.value = file_data.nome_doc;

	var del_btn = new Ext.button.Button({
		renderTo: id,
		id: id + '-delete',
		text: 'Deletar arquivo',
		handler: function() {
			conf = confirm('Deseja deletar arquivo?')
			if (! conf) return false;
			this.disable();
			var Cpm = Ext.getCmp(this.renderTo);
			Cpm.reset();
			var base_name = reg_json.registro._baseinfo.nome;
			var id_reg = reg_json.registro['@id'];
			var id_doc = file_data.id_doc;
			Ext.Ajax.request({
				url: ['/delete', base_name, id_reg, id_doc].join('/'),
				success: function(response){
					text = response.responseText;
                    formPanel.add({
                        xtype: 'hiddenfield',
                        name: 'deleted_file',
                        value: id
                    });
				}
			});
		}
	});
}


function configValues(name, reg, level){
	// Set each field value according to registry respective field.

	if (!reg) return false

	var group = false;
	var file = false;

	if (reg.grupo){
	 	var group = true;
		if (reg.grupo.nome) file = true;
	}

	if (!file){
		var id = getId(name, level);
		var elm = Ext.getCmp(id);
		try{ elm.setValue(reg); }
		catch(err){}
	}

	if (group){
		if (file){

			var id = getId(name, level);
			file_elm = document.getElementById(id)
			//var file_elm = Ext.get(id + '-inputEl');
			//var file_elm = Ext.getCmp(id);
			if (file_elm){
			 	//file_elm.dom.value = reg.grupo.nome;
				file_data = { 'nome_doc': reg.grupo.nome, 'id_doc': reg.grupo.id };
				configFileElm(id, file_elm, file_data, name);
			}
			return true;
		}

		level ++; // registry inner level

		if (reg.grupo.constructor === Array){

			for (var i in reg.grupo){

			 	btn_id = getId(id, level, button=true);
				var btn = Ext.getCmp(btn_id);
				if (! btn) continue ;
				for (var j in reg.grupo[i])
					configValues(j, reg.grupo[i][j], level);

				if (i != reg.grupo.length-1){
			 		btn.el.dom.click();
				}
			}
		}
		if (reg.grupo.constructor === Object){
			if (!reg.grupo.nome) { //if not file
				for (var i in reg.grupo)
					configValues(i, reg.grupo[i], level);
			}
		}
	}
}

function buildHiddenInputs(){

	for(var i=0; i<=hidden_fields.length-1; i++){
	 	if (hidden_fields[i]){
			formPanel.add({
				xtype: 'hiddenfield',
				name: hidden_fields[i],
				value: '#grupo'
			});
		}
	}
}


//-----------------------------Program Execution----------------------------------//

for(var i=0; i<=items_ct-1; i++){
	// Configure buttons handlers. 
 	configHandler(items_backup[i]);
	// Configure fields names. 
	configFields(items_backup[i], parentName=null);
}

Ext.onReady(function(){
  	// Build fields within ExtJS containers.

	var containers = new Array();

	for (var ct=0; ct<=items_ct-1; ct++){

		var elm = document.getElementById(ct);
		if (elm == null) continue;

		var container = Ext.create('Ext.container.Container', {
			items: items_backup[ct],
			style: {
				left: elm.style.left,
				top: elm.style.top,
				width: elm.style.width,
				position: 'relative',
			}
		});

		containers.push(container);
	}

	$('#LB_form').empty();

	formPanel = Ext.create('Ext.form.Panel', {
		autoScroll: true,
		title: window.location.pathname.split('/')[4],
		renderTo: 'LB_form',
		width: '100%',
		height: '650px',
		items: containers,
		buttons: [{
			text: 'Submit',
			scale: 'large',
			handler: function() {
				var form = this.up('form').getForm();
				buildHiddenInputs();
				form.submit({
				 	params: {
						'reg_id': window.location.pathname.split('/')[6]
					},
					success: function(fp, o) {
						Ext.Msg.alert('Success', 'Your photo has been uploaded.');
					},
					failure: function(form, action) {
						Ext.Msg.alert('Fail','efwfgew');
                        a = action
                        location.reload(true);
					}
				});
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

	for (var i in reg_json.registro){
	 	// Configure fields values.

		if (i.indexOf('@') != -1 || i == '_baseinfo') continue;
		configValues(i, reg_json.registro[i], level=0);
	}

});

