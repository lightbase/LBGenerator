import json

import logging
import requests

from .. import config

# TODO: Encontrar o ponto do codigo do lightbase onde se pode enserir essa
# paradas! By Landim
basePath=config.LBRELACIONAL_URL

# TODO: Que porra é essa? Serve para o quê? Não deveria estar no *.ini?
# By Questor
lightPath="http://192.168.56.101/lbgenerator/"

reservedNames=[
    "_history", 
    "_app_config", 
    "_portal", 
    "log_lbindex", 
    "log_lbconverter", 
    "_user"
]
light_to_robot_dic={"Text":"varchar(200)"}

# NOTE: Inteface de base de dados! By Questor
class RobotInterface:
    @staticmethod
    def getAllStructsFromLightbase():
        structs=[]
        r=requests.get(lightPath)
        if not r.status_code == requests.codes.ok:
            # NOTE: Faz log de error! By John Doe

            return structs
        json=r.json()
        jsonList=json["results"]
        for i in jsonList:
            valor={}
            valor["name"]=i["metadata"]["name"]
            valor["id"]=i["metadata"]["id_base"]
            valor["struct"]=i["metadata"]["model"]
            if valor["name"] not in reservedNames:
                structs += [valor]
        return structs;

    @staticmethod
    def getAllContentsFromLightBase():
        structs=RobotInterface.getAllStructsFromLightbase()
        contents=[]
        for base in structs:
            r=requests.get(lightPath + "/" + base["name"] + "/doc" )
            if not r.status_code == requests.codes.ok:
                # NOTE: Faz log de error! By John Doe

                return []
            json=r.json()
            jsonList=json["results"]
            for i in jsonList:
                content={}
                content["base_name"]=base["name"]
                content["id"]=i["_metadata"]["id_doc"]
                content["value"]=i
                del content["value"]["_metadata"]
                contents += [content]
        return contents;

    @staticmethod
    def light_to_robot(struct):
        listCamps=[]
        for i in struct:
            listCamps += [i]
        for i in listCamps:
            struct[i]=light_to_robot_dic[struct[i]]
        return struct

    # NOTE: Save in robot! By John Doe
    @staticmethod
    def baseStructSaveLight(name, struct):
        struct=json.loads(struct)
        RobotInterface.baseStructSave(name, struct["metadata"]["model"])
        pass

    @staticmethod
    def baseStructSave(name, struct):
        if(len(basePath) > 0):
            restPath=basePath + 'tables/' + name
            try:
                headers={'Content-Type': 'application/json'}
                valor=json.dumps(struct)
                r=requests.post(restPath, data=valor, headers=headers)
                if not r.status_code == requests.codes.ok:
                    pass
            except Exception as e:
                pass
        return

    # NOTE: Update in robot! By John Doe
    @staticmethod
    def baseStructUpdate(name, struct):
        if(len(basePath) > 0):
            restPath=basePath + "tables/" + name
            r=requests.put(restPath, struct)
            if r.status_code == requests.codes.ok:
                # NOTE: Faz o looger de problema aqui! By John Doe

                pass
        return

    # NOTE: Delete in robot! By John Doe
    @staticmethod
    def baseStructDelete(name):
        if(len(basePath) > 0):
            restPath=basePath + "tables/" + name
            r=requests.delete(restPath)
            if r.status_code == requests.codes.ok:
                # NOTE: faz o looger de problema aqui! By John Doe

                pass
        return

    # NOTE: Load of dadabase date! By John Doe
    @staticmethod
    def baseStructLoadFromLightBase():
        listBases=RobotInterface.getAllStructsFromLightbase()
        for i in listBases:
            i["struct"]=RobotInterface.light_to_robot(i["struct"])
            RobotInterface.baseStructSave(i["name"], i["struct"])
        return

    # NOTE: Para content! By John Doe
    @staticmethod
    def baseContentLoad():
        listBases=RobotInterface.getAllContentsFromLightBase()
        for i in listBases:
            RobotInterface.baseContentSave(i["base_name"], i["value"], i["id"])

    # NOTE: Save in robot! By John Doe
    @staticmethod
    def baseContentSaveLight(name, content ,id):
        content=json.loads(content)
        RobotInterface.baseContentSave(name, content, id)

    @staticmethod
    def baseContentSave(name, content ,id):
        if(len(basePath) > 0):
            restPath=basePath + "content/" + name + "?lb_id=" + str(id) +\
                    "&database=lightbase"
            headers={'Content-Type': 'application/json'}
            valor=json.dumps(content)
            r=requests.post(restPath, data=valor, headers=headers)
            if not r.status_code == requests.codes.ok:
                # NOTE: Faz o looger de problema aqui! By John Doe

                pass
        return

    # NOTE: Update in robot! By John Doe
    @staticmethod
    def baseContentUpdate(name, content, id):
        if(len(basePath) > 0):
            restPath=basePath + "content/" + name + "?lb_id=" + str(id) + "&database=lightbase"
            r=requests.put(restPath, content)
            if r.status_code == requests.codes.ok:
                # NOTE: Faz o looger de problema aqui! By John Doe

                pass
        return

    # NOTE: Update in robot! By John Doe
    @staticmethod
    def baseContentDelete(name):
        if(len(basePath) > 0):
            restPath=basePath + "content/" + name + "?lb_id=" + str(id) + "&database=lightbase"
            r=requests.delete(restPath)
            if not r.status_code == requests.codes.ok:
                pass
        return

