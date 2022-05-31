import json

class GlobalCounter:
    all_counter_dict={}
    def StepCounter(counter_name,inc_step):
        if  GlobalCounter.all_counter_dict.get(counter_name) is None:
            GlobalCounter.all_counter_dict[counter_name]=0
        GlobalCounter.all_counter_dict[counter_name]=GlobalCounter.all_counter_dict[counter_name]+inc_step
    def GetCounterVal(counter_name):
        if GlobalCounter.all_counter_dict.get(counter_name) is None:
            return 0
        else:
            return  GlobalCounter.all_counter_dict[counter_name]
class DataScopesCounter:
    def __init__(self):
        self.all_counter_dict={}
    def _pre_process(self,counter_name_list):
        map_point=self.all_counter_dict
        for name in counter_name_list[:-1]:
            if map_point.get(name) is None:
                map_point[name]={}
            map_point=map_point[name]
        last_name=counter_name_list[-1]
        if map_point.get(last_name) is None:
            map_point[last_name]=0
        return map_point,last_name
    def StepCounter(self,counter_name_list,inc_step):
        map_point,last_name=self._pre_process(counter_name_list)
        map_point[last_name]=map_point[last_name]+inc_step
        return map_point[last_name]
    def GetCounterVal(self,counter_name_list):
        map_point,last_name=self._pre_process(counter_name_list)
        return map_point[last_name]
    def StepCounter_Scopes(self,scoped_counter_name,inc_step):
        return self.StepCounter(scoped_counter_name.split("."),inc_step)
    def GetCounterVal_Scopes(self,scoped_counter_name):
        return self.GetCounterVal(scoped_counter_name.split("."))
    def display(self,print_f=print):
        print_f(self.all_counter_dict)

if __name__=="__main__":
    print("trying to execute other_tools.py as main program: not supported")
else:
    GeneralGlobalCounter=DataScopesCounter()
    ModuleReservedCounter=DataScopesCounter()

def parsing_args(input_terms):
    
    value_table={}
    temp_para=None
    def _insert_key_val(key,val):
        def __parse_value(val):
            try:
                res=int(val)
            except:
                try:
                    res=float(val)
                except:
                    res=val
            return res        
        value_table[key]=__parse_value(val)
    for term in input_terms:
        if temp_para is None:
            temp_para=term
            for i in range(0,len(term)):
                if term[i]=="=":
                    key=term[:i]
                    val=term[i+1:]
                    _insert_key_val(key,val)
                    temp_para=None
                    break
        else:
            _insert_key_val(temp_para,term)
    return value_table
def parsing_post_fix(file_name):
    for i in range(0,len(file_name)):
        if file_name[i]==".":
            return parsing_post_fix(file_name[i+1:])
    return file_name        
        
def save_file(data,format,name):
    map_format={
        "pickle":lambda df,n:df.to_pickle(n)
    }
    if map_format.get(format) is None:
        print("{} is not supported for data saving in {}".format(format,name))
        return False
    else:
        map_format[format](data,name)
        return True            

class ClassMaker:
    def __init__(self,class_type,**parameters):
        self.class_type=class_type
        self.parameters=parameters
    def __call__(self,**more_parameters):
        parameters=self.parameters
        for k in more_parameters:
            parameters[k]=more_parameters[k]
        return self.class_type(**parameters)
