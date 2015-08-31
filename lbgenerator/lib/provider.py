
class AuthProvider():

    PERMS = {
      'view'  : 'group:viewers',
      'create': 'group:creators',
      'edit'  : 'group:editors',
      'delete': 'group:deleters'
    }

    def __init__(self, owner, base, resource):
        self.owner = owner
        self.base = base
        self.resource = resource

    def get_authorization(self, pattern):
        """ Get User Authorizarion
        """
        pattern_split = pattern.split(':')
        level = len(pattern_split)
        auth_levels = {
            0: self.no_auth,         # ''
            1: self.admin_auth,      # 'admin'
            2: self.base_auth,       # 'owner-base:perm1,perm2'
            3: self.resource_auth    # 'owner-base:resource:perm1,perm2'
        }
        return auth_levels[level](*pattern_split)

    def no_auth(self, *args):
        """ Commom User has no authorization.
        """
        return [ ]

    def admin_auth(self, *args):
        """ Commom User has no authorization.
        """
        return [
            self.PERMS['view'], 
            self.PERMS['create'], 
            self.PERMS['edit'], 
            self.PERMS['delete']
        ]

    def base_auth(self, base_pattern, perms_pattern):
        """ Base User has granted authorization by base owner
            to acces his base structure and configurations.
        """
        owner, base = base_pattern.split('-')

        if owner != self.owner:
            return None 
        if base != self.base:
            return None
            
        perms = perms_pattern.split(',')
        authorization = [ ]
        for perm in perms:
            authorization.append(self.PERMS[perm])
        return authorization

    def resourse_auth(self, base_pattern, resource, perms_pattern):
        """ Base User has granted authorization by base owner
            to acces his base resources.
        """
        base_auth = self.base_auth(base_pattern, perms_pattern)
        if not base_auth:
            return None
        if resource != self.resourse:
            return None
        return base_auth
