
//Globals
	fields_history = [];
	containersCounter = 0;
	items_backup = {};

Ext.onReady(function(){

	fieldStore = Ext.create('Ext.data.Store', {
	    storeId:'fieldStore',
	    fields:['nome', 'descricao', 'tipo'],
	    data:{'items': eval(document.getElementById('gridData').getAttribute('value'))},
	    proxy: {
	        type: 'memory',
	        reader: {
	            type: 'json',
	            root: 'items'
	        }
	    }
	});

	fields_grid = Ext.create('Ext.grid.Panel', {
	    store: Ext.data.StoreManager.lookup('fieldStore'),
	    columns: [
	        { header: 'Campo',  dataIndex: 'nome' },
	        { header: 'Descrição', dataIndex: 'descricao', flex: 1 },
	        { header: 'Tipo', dataIndex: 'tipo' }
	    ],
	    viewConfig: {
		plugins: {
		    ddGroup: 'fieldsGrid',
		    ptype: 'gridviewdragdrop',
		    enableDrop: false
		}
            },
	    enableDragDrop: true
	});


	formPanel = Ext.create('Ext.form.Panel', {
	    id: 'LB_form',
	    title: 'Área de Trabalho',
	    region: 'center',
	    bodyStyle  : 'padding: 15px;',
		autoScroll: true
	});

	tabPanel = Ext.create('Ext.tab.Panel', {
	    title: 'Configurações',
	    width: '35%',
	    height: '100%',
	    collapsible: true,
	    split: true,
	    region:'west',
	    items: [{
			title: 'Adicionar campos',
			items: fields_grid
	    }, {
			title: 'Campo'
	    }, {
			title: 'formulário',
			items: [{
					xtype:'form',
	    			bodyStyle  : 'padding: 15px;',
					items: [{
							xtype:'textfield',
							id:'formName-input',
							fieldLabel: 'Nome',
							allowBlank: false,
					}],
					buttons: [{
						text: 'Save',
						handler: function() {

							if (this.up('form').getForm().isValid() == true){}
							else { return false }

							conf = confirm('Salvar formulário?');
							if (!conf) return false

							base_name = window.location.pathname.split('/')[2];

							Ext.Ajax.request({
								url: 'http://neo.lightbase.cc/lb/' +base_name+ '/form/new',
								params: {
									form_html: document.getElementById('LB_form-body').outerHTML,
									form_name: document.getElementById('formName-input-inputEl').value,
									containers_counter: containersCounter,
									items_backup: JSON.stringify(items_backup)
								},
								success: function(response){
									form_name = document.getElementById('formName-input-inputEl').value;
									redirect = 'http://neo.lightbase.cc/lb/' +base_name+ '/reg/' +form_name+ '/new';
									window.location.href= redirect;
								}
							});
						}
						},{
						text: 'Cancel',
						handler: function() {
							this.up('form').getForm().reset();
						}
					}]
				}
			]
	    }]
	});

	mainPanel = Ext.create('Ext.panel.Panel', {
	  	width: '100%',
		height: '100%',
		items: [{
			    xtype: 'box',
			    id: 'header',
			    region: 'north',
			    html: '<h1>Criar Formulário</h1>'
			},
		    tabPanel,
		    formPanel
		],
		layout: 'border',
		renderTo: 'mainPanel'
	});

	var formPanelDropTargetEl =  formPanel.body.dom;

	var formPanelDropTarget = Ext.create('Ext.dd.DropTarget', formPanelDropTargetEl, {
	    ddGroup: 'fieldsGrid',
	    notifyEnter: function(ddSource, e, data) {
			formPanel.body.stopAnimation();
			formPanel.body.highlight();
	    },
	    notifyDrop : function(ddSource, e, data){

			pos = { x: e.browserEvent.clientX, y: e.browserEvent.clientY }
			anchor = formPanel.body.getAnchorXY()
			anchorxy = { x: anchor[0], y: anchor[1] }

			selectedRecord = ddSource.dragData.records[0];
			fieldName = ddSource.dragData.records[0].data.nome;
			fieldDesc = ddSource.dragData.records[0].data.descricao;
			fieldType = ddSource.dragData.records[0].data.tipo;

			added = formPanel.add(toField(fieldName, fieldDesc, fieldType, selectedRecord, pos, anchorxy));
			if (added.items.items[0].$className == 'Ext.button.Button'){
				added.el.dom.setAttribute('id', 'form_buttons');
			}

			else{
				added.el.dom.setAttribute('id', containersCounter);
				containersCounter += 1;
			}

			fields_history.push(added);

			// Delete record from the source store.  not really required.
			ddSource.view.store.remove(selectedRecord);

			return true;
	    }
	});

});


function toField(fieldName, fieldDesc, fieldType, gridData, pos, anchor){

	lbElms = document.getElementById('lbElms').getAttribute('value');
	lbElms = eval(lbElms);

	for(elm=0; elm<=lbElms.length - 1; elm++){
		if (fieldName == lbElms[elm].name){
			items = lbElms[elm];
			break ;
		}
	}

    console.warn(items);
	container = Ext.create('Ext.container.Container', {
	  	griddata: gridData,
		draggable: true,
        resizable: true,
		style:{
			top: pos.y -anchor.y -15,
			left: pos.x -anchor.x -15
		},
		items: items,
		listeners: {
			afterrender: function(e, eOpts){
				e.el.dom.setAttribute('onContextMenu',"javascript:removeContainer(this);return false;");
			}
        },
		maxWidth: 400,
	});

	items_backup[containersCounter] = items;

	return container;
}

function removeContainer(el){
	for(i in fields_history){
		if(fields_history[i].el != null){
			if(fields_history[i].el.dom == el){
				formPanel.remove(fields_history[i]);
				fieldStore.add(fields_history[i].griddata);
				items_backup[el.id] = 'null';
			}
		}
		//fields_history.pop(i);
	}
}



