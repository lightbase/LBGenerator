from ... import model
from ... import config
from ..entities import LB_Users, get_doc_table
from ..context.document import DocumentContextFactory


class UserContextFactory(DocumentContextFactory):

    """ This is the interface for storing token data information
    """
    def __init__(self, request):
        super(UserContextFactory, self).__init__(request)

    @property
    def base_name(self):
        return '_user'

    def get_member(self, user_id):
        try:
            self.single_member=True

            # TODO: Buscar o usuário pelo username, ao invés do ID, será
            # necessário fazer a consulta pela query literal! By Landim
            member=self.session.query(self.entity).filter("id_user = '" + user_id+"'").first()

            return member or None
        except Exception:
            return None

    def get_member_by_api_key(self, api_key):
        try:
            self.single_member=True

            # NOTE: Fazer a consulta pela query literal! By Questor
            member=self.session.query(self.entity).filter("api_key = '" + api_key +"'").first()

            return member or None
        except Exception:
            return None

    def generate_token(self, length, allowed_chars):

        # NOTE: We assume that the token will be enough random, otherwise we
        # need to make sure the generated token doesn't exists previously in DB!
        # By John Doe
        return ''.join([choice(allowed_chars) for i in range(length)])

    def retrieve(self, username, scope):
        pass

    def retrieve(self, token):
        """This method retrieves the data for a token from the storage.

        :param token: The token to retrieve.
        :returns: Token information
        :rtype: dict

        """

        raise NotImplementedError # NOTE: "pragma: no cover"! By John Doe

    def store(self, token, username, scope, expires_in):
        """This method stores token data class dict in the storage.

        :param token: The token to store the value under.
        :param username: The username related to the token to store.
        :param expires_in: Optional expiration time in seconds from now.
        :type value: dict
        :returns: True if the data was stored successfully, False otherwise.
        :rtype: boolean

        """

        raise NotImplementedError # NOTE: "pragma: no cover"! By John Doe

    def delete(self, token):
        """This method deletes a token data dict from the storage

        :param token: The token of the data to be removed.

        :returns: True if the delete proceeded ok, regardless of if the key
                  actually existed or not.
        :rtype: boolean

        """

        raise NotImplementedError # NOTE: "pragma: no cover"! By John Doe

    def purge_expired(self):
        """This method purges all expired data from the storage

        All expired data should be purged from the TokenStore when this method
        is called. TokenStore's that automatically expire old data must still
        implement this method, but can do nothing.

        """

        raise NotImplementedError # NOTE: "pragma: no cover"! By John Doe
