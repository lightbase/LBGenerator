
class LbException(Exception):
    def __init__(self, except_msg="", except_msg_other=""):
        """
        Exceção "base" do LightBase.
        """

        '''
        If a exception message was not informed this class will set a 
        default one to system!
        '''
        if except_msg == "":
            except_msg = "LightBase exception!"

        '''
        Seta informações adicionais sobre o erro se passadas no 
        parâmetro "except_msg_other"!
        '''
        if except_msg_other != "":
            except_msg = except_msg + " " + except_msg_other

        '''
        Call the base class constructor with the parameters it 
        needs!
        '''
        Exception.__init__(self, except_msg)