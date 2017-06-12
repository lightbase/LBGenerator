import json
import logging
import datetime

from ..model import begin_session


def execute_sql(request):

    # NOTE: Get SQLAlchemy session! By John Doe
    session = begin_session()

    # NOTE: Get commands from json request! By John Doe
    commands = request.json_body['commands']

    # TODO I: Check if commands are valid? By John Doe

    # TODO II: Check users? By John Doe

    # NOTE: Array to store results! By John Doe
    results = []

    success = True

    for command in commands:
        try:

            # NOTE: Execute command! By John Doe
            result = session.execute(command)

            # NOTE: If the command returns rows! By John Doe
            if result.returns_rows:

                # NOTE: Create a list to contain the rows! By John Doe
                res = {
                   'row_count': result.rowcount,
                   'rows': []
                }

                for row in result.fetchall():

                    # NOTE: Convert row obj to dictionary (for serialization)!
                    # By John Doe
                    row_dict = dict()

                    for key in row.keys():
                        value = serialize(row[key])
                        row_dict[key] = value

                    # NOTE: Add row to list of rows! By John Doe
                    res['rows'].append(row_dict)

                results.append(res)
            else:

                # NOTE: Command doesn't return rows! By John Doe
                results.append({
                    'success': True
                })

                pass
        except Exception as e:

            # NOTE: An error occurred! By John Doe
            results.append({
                'success': False,
                'error_msg': str(e)
            })

            success = False
            break

    if success:
        # session.commit()

        # NOTE: Tentar fechar a conexão de qualquer forma!
        # -> Na criação da conexão "coautocommit=True"!
        # By Questor
        try:
            if session.is_active:
                session.close()
        except:
            pass

    else:
        session.rollback()

    # NOTE: Tentar fechar a conexão de qualquer forma!
    # -> Na criação da conexão "coautocommit=True"!
    # By Questor
    try:
        if session.is_active:
            session.close()
    except:
        pass

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
