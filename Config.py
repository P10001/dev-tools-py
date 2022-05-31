
import sys

from mytools import logger
from mytools import other_tools
import json
GlobalModuleLogger=logger.Logger(out_file_name="Config_py.log",mode='w',instant_flush=True)
GlobalModule_output=logger.LogData_StrList(GlobalModuleLogger,'config_log',data_level=logger.LogData.DATA_LEVEL_DEBUG)
GlobalModule_output.set_data_signature_disp_mode(GlobalModule_output.ITEM_DISP_MODE_HIDDEN)
def SetInfoLevel(min_level,max_level=None):
    GlobalModuleLogger.set_data_level_filter(min_level,max_level)
class Config:
    EmptyValue="*"
    def __init__(self,sup_node=None,value=None,config_id=None,config_file_name=None):
        self.config_dict={}
        self.value=value
        self.sup_node=sup_node
        self.str=''
        if config_id is None:
            config_id=other_tools.GeneralGlobalCounter.GetCounterVal_Scopes("Config.count.init")
            config_id="config[{}]".format(config_id)
        other_tools.GeneralGlobalCounter.StepCounter_Scopes("Config.count.init",1)
        self.config_id=config_id
        if config_file_name is not None:
            self.load_config_file(config_file_name=config_file_name)

    def is_leaf_node(self):
        return self.config_dict=={}
    def load_config_file(self,config_file_name,replace_all=True):
        try:
            f=open(config_file_name,'r')
            src_data=f.read()
            f.close()
            table=json.loads(src_data)
            self.load_config_dict(table,replace_all)

        except Exception as e:
            GlobalModule_output.append_info_print("Error {}: in parse {}".format(e,config_file_name))
            return False
    def load_config_dict(self,src_dict,replace_all=True):
        #map_point=src_dict
        for k in src_dict:
            if self.config_dict.get(k) is None:
                info="insert option [{}]:{} in config {}".format(k,src_dict[k],self.config_id)
                self._insert_config(src_dict[k],k)
            else:
                if replace_all:
                    info="replace option [{}]:{} with [{}]:{} in config {}".format(k,self.config_dict[k],k,src_dict[k],self.config_id)
                    self._insert_config(src_dict[k],k)
                else:
                    info="skip conficted term [{}]:{} while new value is {} in config{}".format(k,self.config_dict[k],src_dict[k],self.config_id)
            GlobalModule_output.append_info_print(info=info)
        # if sup_node!=self.sup_node:
        #     GlobalModule_output.append_info_print('change supnode from {} to {}'.format(self.sup_node,sup_node))
        # self.sup_node=sup_node
    def _insert_config(self,src,k):
        if type(src)==type({}):
            new_config=Config(sup_node=self,value=None,config_id=k,config_file_name=None)
            new_config.load_config_dict(src,True)
        elif type(src)==type(""):
            if src.startswith("#"):
                new_config=Config(sup_node=self,value=None,config_id=k,config_file_name=None)
                GlobalModule_output.append_info_print("import config from {} to [{}] in root config {}".format(src,k,self.config_id))
                new_config.load_config_file(src[1:],True)
            else:
                new_config=Config(sup_node=self,value=src,config_id=k,config_file_name=None)
        else:
            new_config=Config(sup_node=self,value=src,config_id=k,config_file_name=None)
        self.config_dict[k]=new_config
    def __getitem__(self,key):

        val=self.get(key)
        if val is not None:
            return val
        else:
            raise KeyError("Key {} got None".format(key))
    def __setitem__(self,key,value):
        if self.get(key) is None:
            GlobalModule_output.append_info("insert new item {}:{} in config {}".format(key,value,self.config_id))
        else:
            GlobalModule_output.append_info("replace item {}:{} with {}:{} in config {}".format(key,self.get(key),key,value,self.config_id))
        keys=key.split(".")
        set_place=self._find_place(keys,insert_all=True)
        set_place.sup_node._insert_config(src=value,k=keys[-1])
    def _find_place(self,key_terms,insert_all=False):
        map_point=self
        for term in key_terms:
            if(term.startswith('-')):
                for _ in range(0,len(term)):
                    if map_point.sup_node is not None:
                        map_point=map_point.sup_node
                    else:
                        GlobalModule_output.append_info("trying to use '-' more than current config depth in config {}".format(self.config_id))
                        return None
            elif map_point.config_dict.get(term) is None:
                return None
            else:
                map_point=map_point.config_dict[term]
        return map_point
    def _find_root(self):
        if self.sup_node is None:
            return self
        else:
            return self.sup_node._find_root()
    def get(self,key):
        key=key.split(".")
        config_point=self._find_place(key)
        if config_point is None:
            return None
        elif config_point.value is None:
            if config_point.config_dict=={}:
                return None
            return config_point
        else:
            return config_point._resolve_value()
    def to_value(self):
        if self.config_dict=={}:
            return self._resolve_value()
        else:
            return_dict={}
            for k in self.config_dict:
                return_dict[k]=self.config_dict[k].to_value()
            return return_dict
    def _resolve_value(self):
        def __resolve(val):
            if type(val)==type(""):
                if val.startswith("@"):
                    var_name=val[1:]
                    GlobalModule_output.append_info_print("get @{} as value, tring to resolve referenced value for config{}".format(var_name,self.config_id))
                    val_get=self.get(var_name)
                    if val_get is None:
                        root=self._find_root()
                        if root ==self:
                            #print("sup {}".format(self.sup_node))
                            pass
                        else:
                            GlobalModule_output.append_info_print("find value None in {}, trying to resolve value from global space".format(self.config_id))
                            val_get=root.get(var_name)

                    self.value=val_get
                    GlobalModule_output.append_info_print("replaced value  with resolved val {}".format(self.value))
                    return val_get
                else:
                    return val
            else:
                return val
        if self.value is None:
            return None
        elif type(self.value)==type([]):
            self.value=[__resolve(val) for val in self.value]
        else:
            self.value=__resolve(self.value)
        return self.value
    def __str__(self):
        if self.str=='':

            if self.is_leaf_node():
                self.str='{}:{}'.format(self.config_id,self._resolve_value())
                return self.str
            else:
                self.str='{}:...\n\t'.format(self.config_id)
                sub_node_str='-->{}\n'
                for i in self.config_dict:
                    node=self.config_dict[i]
                    sub_res=sub_node_str.format(str(node))
                    self.str+=sub_res.replace('\n','\n\t')
                return self.str
        else:
            return self.str
    def __iter__(self):
        return iter(self.config_dict)


