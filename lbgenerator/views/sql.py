"""
This file contains the view that receives SQL commands

Creator: Danilo Carvalho
"""
import logging
import json
import datetime

from ..model import begin_session

def execute_sql(request):
    # get SQLAlchemy session
    session = begin_session()

    # get commands from json request
    commands = request.json_body['commands']

    # TODO: check if commands are valid?
    # TODO: check users?

    # array to store results
    results = []
    success = True

    for command in commands:
        try:
            # execute command
            result = session.execute(command)

            # if the command returns rows...
            if result.returns_rows:
                # ... create a list to contain the rows
                res = {
                   'row_count': result.rowcount,
                   'rows': []
                }
                for row in result.fetchall():
                    # convert row obj to dictionary (for serialization)
                    row_dict = dict()
                    for key in row.keys():
                        value = serialize(row[key])
                        row_dict[key] = value
                    # add row to list of rows
                    res['rows'].append(row_dict)
                # 
                results.append(res)
            else:
                # command doesn't return rows
                results.append({
                    'success': True
                })
                pass
        except Exception as e:
            # an error occurred
            results.append({
                'success': False,
                'error_msg': str(e)
            })
            success = False
            break

    if success:
        session.commit()
    else:
        session.rollback()
    
    # N >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # session.begin()
    # session.commit()
    # session.flush()
    # session.close()
    # N <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    # O >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    session.close()
    # O <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

    return results

def serialize(value):
    """
    Converts datetime and other objects to formats accepted by 
    pyramid's JSON renderer
    """
    if isinstance(value, datetime.datetime):
        res = value.strftime('%d/%m/%Y %H:%M:%S')
    elif isinstance(value, datetime.time):
        res = value.strftime('%H:%M:%S')
    elif isinstance(value, datetime.date):
        res = value.strftime('%d/%m/%Y')
    else:
        try:
            res = json.loads(value)
        except Exception as e:
            res = value

    return res

