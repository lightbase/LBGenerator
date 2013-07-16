from lbgenerator.lib import model

def save_base(base_xml, base_name):
    """ Insert base in database.
    """

    engine, session, metadata = model.Engine().get_conn()
    bases_table, forms_table, regs_table, docs_table = model.Engine().mapper_all(base_name)

    if not engine.dialect.has_table(session, 'lb_bases'):
        metadata.create_all(tables=[bases_table])

    bases_nextval = session.execute(model.Bases_seq().seq)
    obj = model.LB_bases(bases_nextval,
                         base_name,
                         base_xml)

    session.add(obj)
    session.commit()
    session.expunge_all()

    return bases_nextval

def save_form(base_name, form_data):
    """ Insert form in database.
    """

    engine, session, metadata = model.Engine().get_conn()
    bases_table, forms_table, regs_table, docs_table = model.Engine().mapper_all(base_name)

    if not engine.dialect.has_table(session, 'lb_forms'):
        metadata.create_all(tables=[forms_table])

    forms_nextval = session.execute(model.Forms_seq().seq)

    obj = model.LB_forms(forms_nextval,
                         form_data['base_id'],
                         form_data['form_name'],
                         form_data['form_xml'],
                         form_data['form_html'])

    session.add(obj)
    session.commit()
    session.expunge_all()
    session.close()

    return forms_nextval

def save_reg(base_name, reg_data):
    """ Insert registry in database.
    """

    engine, session, metadata = model.Engine().get_conn()
    bases_table, forms_table, regs_table, docs_table = model.Engine().mapper_all(base_name)

    Regs = model.map_class_to_table(model.LB_regs, regs_table, 'Regs')

    obj = Regs(reg_data['id_reg'],
               bytes.decode(reg_data['reg_xml']),
               reg_data['reg_json'])

    session.add(obj)
    session.commit()
    session.expunge_all()

    docs = reg_data.get('docs')

    if docs:
        Docs = model.map_class_to_table(model.LB_docs, docs_table, 'Docs')

    for doc in docs:
        obj = Docs(doc['id_doc'],
                   reg_data['id_reg'],
                   doc['filename'],
                   doc['blob'],
                   doc['mimetype'])

        session.add(obj)
        session.commit()
        session.expunge_all()

    session.close()

    return reg_data['id_reg']

def update_reg(base_name, reg_data):
    """ Update registry in database.
    """

    engine, session, metadata = model.Engine().get_conn()
    bases_table, forms_table, regs_table, docs_table = model.Engine().mapper_all(base_name)

    Regs = model.map_class_to_table(model.LB_regs, regs_table, 'Regs')

    reg_update = {
        'xml_reg': bytes.decode(reg_data['reg_xml']),
        'json_reg': reg_data['reg_json']
    }

    up = session.query(Regs).filter_by(id_reg = reg_data['id_reg']).update(reg_update)
    session.commit()
    session.expunge_all()

    docs = reg_data.get('docs')

    if docs:
        Docs = model.map_class_to_table(model.LB_docs, docs_table, 'Docs')

    for doc in docs:
        obj = Docs(doc['id_doc'],
                   reg_data['id_reg'],
                   doc['filename'],
                   doc['blob'],
                   doc['mimetype'])

        session.add(obj)
        session.commit()
        session.expunge_all()

    session.close()

    return reg_data['id_reg']

def get_file(id_doc, id_reg, nome_doc):
    """ Return file bytes for downloading it
    """
    engine, session, metadata = model.Engine().get_conn()
    bases_table, forms_table, regs_table, docs_table = model.Engine().mapper_all(base_name)

    Docs = model.map_class_to_table(model.LB_docs, docs_table, 'Docs')
    doc = session.query(Docs.blob_doc).filter_by(id_doc = id_doc, id_reg = id_reg, nome_doc = nome_doc).first()

    return doc













