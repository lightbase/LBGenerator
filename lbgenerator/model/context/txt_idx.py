import json

import logging
from sqlalchemy import insert
from sqlalchemy import update
from sqlalchemy import delete
from sqlalchemy.util import KeyedTuple

from ...lib.cache_master import CacheMaster
from . import CustomContextFactory
from ..entities import Lb_Txt_Idx
from ...lib.lb_exception import LbException
from ...lib import utils
from ...lib.utils import LbUseful
from ... import model

log = logging.getLogger()


class TxtIdxContextFactory(CustomContextFactory):
    """ Contexto p/ manipulação dos dados da rota "_txt_idx".
    """

    entity = Lb_Txt_Idx

    def __init__(self, request):
        super(TxtIdxContextFactory, self).__init__(request, "cfg_idx")

    def create_member(self, data):

        try:
            member = self.entity(**data)
        except Exception as e:
            raise LbException("Failed to format persistence object!", str(e))

        try:
            self.session.add(member)
            self.session.commit()

            # Note: Manipula o cache conforme as regras dessa rota!
            # By Questor
            member_on_db = self.session.query(self.entity)\
                .filter_by(nm_idx=data["nm_idx"]).first()
            self.set_item(data["nm_idx"], member_on_db)

        except Exception as e:
            raise LbException("Failed to persist data!", str(e))
        finally:
            self.session.close()

        return member

    def update_member(self, data):

        # Note: Obtêm o nome do índice textual na rota submetida! 
        # By Questor
        nm_idx = self.request.matchdict['nm_idx']
        self.single_member = True

        try:
            stmt = update(self.entity.__table__).where(
                self.entity.__table__.c.nm_idx == nm_idx)\
                .values(**data)
        except Exception as e:
            raise LbException("Failed to format persistence object!", str(e))

        try:
            result = self.session.execute(stmt)
            self.session.commit()

            '''
            NOTE: Checa se algum item foi "updetado" e se foi checa 
            se o campo "nm_idx" foi modificado! By Questor
            '''
            if result.rowcount > 0:
                data_nm_idx = ""
                try:
                    data_nm_idx = data["nm_idx"]
                except Exception:
                    pass

                # Note: Manipula o cache conforme as regras dessa 
                # rota! By Questor
                if data_nm_idx is not "" and data_nm_idx != nm_idx:
                    member = self.session.query(self.entity)\
                        .filter_by(nm_idx=data_nm_idx).first()
                    self.refresh_item(nm_idx, member, data_nm_idx)
                else:
                    member = self.session.query(self.entity)\
                        .filter_by(nm_idx=nm_idx).first()
                    self.refresh_item(nm_idx, member)

            return result.rowcount
        except Exception as e:
            raise LbException("Failed to persist data!", str(e))
        finally:
            self.session.close()

    def delete_member(self):

        # Note: Obtêm o nome do índice textual na rota submetida! 
        # By Questor
        nm_idx = self.request.matchdict['nm_idx']
        self.single_member = True

        try:
            stmt = delete(self.entity.__table__).where(
                self.entity.__table__.c.nm_idx == nm_idx)
        except Exception as e:
            raise LbException("Failed to format persistence object!", str(e))

        try:
            result = self.session.execute(stmt)
            self.session.commit()

            # Note: Manipula o cache conforme as regras dessa rota! 
            # By Questor
            if result.rowcount > 0:
                self.remove_item(nm_idx)

            return result.rowcount
        except Exception as e:
            raise LbException("Failed to persist data!", str(e))
        finally:
            self.session.close()

    def get_member(self, nm_idx=None):

        # Note: Obtêm o nome do índice textual na rota submetida! 
        # By Questor

        if nm_idx is None:
            nm_idx = self.request.matchdict['nm_idx']

        self.single_member = True

        try:
            member = self.get_item(nm_idx)

            # Note: Manipula o cache conforme as regras dessa rota! 
            # By Questor
            if member is None:
                member = self.session.query(self.entity)\
                    .filter_by(nm_idx=nm_idx).first()
                self.set_item(nm_idx, member)

            '''
            NOTE: Perceba que o método "member_to_dict(self, 
            member, fields=None)" sempre será chamado implicitamente 
            quando é feita um query conforme o modelo abaixo! 
            By Questor
            '''
            return member
        except Exception as e:
            raise LbException("Failed get data!", str(e))
        finally:
            self.session.close()

    def member_to_dict(self, member, fields=None):

        '''
        TODO: Não consegui entender pq o sempre verifica se há o método 
        "_asdict()" visto que ele nunca está disponível! By Questor
        '''
        try:
            dict_member = member._asdict()
        except AttributeError as e:
            if not isinstance(member, KeyedTuple):
                member = self.member2KeyedTuple(member)

        dict_member = utils.json2object(member._asdict()['struct'])

        # TODO: Qual o uso disso aqui? Remover? By Questor
        # fields = getattr(self,'_query', {}).get('select')
        # if fields and not '*' in fields:
            # return {'settings':
                # {field: dict_member['settings'][field] for field in fields}
            # }

        return dict_member
