import os
import time
import sys

from numpy import disp


from mytools import other_tools,dbgtools
GlobalCounter=other_tools.GlobalCounter
GeneralGlobalCounter=other_tools.GeneralGlobalCounter
SetOneBreakPointSingle=dbgtools.SetOneBreakPointSingle
module_log_info=None
module_debug_logger=None

class GlobalInfo:
    basic_dir_name='./expr_output/test_res'
    set_up_flag=False
    def Set_Basic_dir(target_loc):
        global module_log_info
        if os.path.exists(target_loc):
            dir_all=os.listdir(target_loc)
            if len(dir_all) !=0:
                module_log_info.append_info("Error: target loc {"+target_loc+"} already exists")
                return False
            else:
                GlobalInfo.set_up_flag=True
        else:
            GlobalInfo.set_up_flag=True
            module_log_info.append_info("set basic dir at {}".format(target_loc))
            os.mkdir(target_loc)
        GlobalInfo.basic_dir_name=target_loc
    def Basic_file_dir():
        if GlobalInfo.set_up_flag:
            return GlobalInfo.basic_dir_name
        dir_name=GlobalInfo.basic_dir_name
        mark=0
        flag=[False,False]
        while os.path.exists(dir_name) and len(os.listdir(dir_name))!=0:
            dir_name=GlobalInfo.basic_dir_name+str(mark)
            mark+=1
            if mark>=50:
                if not flag[0]:
                    print("pleas clear log files")
                    flag[0]=True
            if mark>=200:
                print("Too many logs")
                return None
        GlobalInfo.set_up_flag=True
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        GlobalInfo.basic_dir_name=dir_name
        module_log_info.append_info("use {} as base dir".format(dir_name))
        return dir_name
class Logger:
    DATA_LEVEL_DEBUG=0
    DATA_LEVEL_HINT=1
    DATA_LEVEL_RESULT=2
    DATA_LEVEL_FATAL=3
    def __init__(self,out_file_name,mode='a',instant_flush=False,use_base_dir=True):
        if use_base_dir:
            self.out_file_name=os.path.join(GlobalInfo.Basic_file_dir(),out_file_name)
        else:
            self.out_file_name=out_file_name
        self.rt_mode=instant_flush
        self.file_io_mode=mode
        self.save_buf=[]
        if mode=='w':
            try:
                f=open(self.out_file_name,mode)
                f.close()
            except Exception as e:
                print(e)
                raise e
        self.data_level_min=None
        self.data_level_max=None
    def set_data_level_filter(self,min_level=None,max_level=None):
        self.data_level_min=min_level
        self.data_level_max=max_level
    def append_info(self,info,data_level=None):
        if data_level is None:
            data_level=Logger.DATA_LEVEL_FATAL
        if self.data_level_min is not None and self.data_level_min>data_level:
            return
        if self.data_level_max is not None and self.data_level_max<data_level:
            return
        if self.rt_mode:
            self._append_info(info)
        else:
            self.save_buf.append(info)
    def manual_flush(self):
        if self.save_buf!=[]:
            for s in self.save_buf:
                self._append_info(s)
            self.save_buf=[]
    def _append_info(self,info):
        #print("{} >> {}".format(info,self.out_file_name))
        try:
            out_f=open(self.out_file_name,'a')
            out_f.write(str(info))
            out_f.close()
        except:
            print("info {} log out failed in path {}".format(info,self.out_file_name))
    def append_info_print(self,info):
        print(str(info))
        self.append_info(info)
    def log_timestamp(self):
        self.append_info(time.strftime("%D:%H:%M:%S"))
def code_back_up(code_file_post_fix=".py",code_dir="code"):
    back_up_dir=os.path.join(GlobalInfo.Basic_file_dir(),code_dir)
    if not os.path.exists(back_up_dir):
        os.makedirs(back_up_dir)
        module_log_info.append_info("backup code at {}".format(back_up_dir))
    command="cp *"+code_file_post_fix+" "+back_up_dir
    if os.system(command)!=0:
        module_log_info.append_info("Error:code back up failed")
class PesudoLogger_test(Logger):
    def __init__(self,out_file_name=None,mode='a',instant_flush=False,use_base_dir=True):
        super().__init__(None,None,None,False)
        #print(self)
    def append_info(self,info,data_level):
        print("level[{}]:{}".format(data_level,info))
    def __str__(self):
        return "this is a test logger, only put all info to print()"
class LogData:
    ITEM_DISP_MODE_ALL=0
    ITEM_DISP_MODE_HIDDEN=1
    ITEM_DISP_MODE_ONCE=2

    DATA_LEVEL_DEBUG=0
    DATA_LEVEL_HINT=1
    DATA_LEVEL_RESULT=2
    DATA_LEVEL_FATAL=3
    def __init__(self,bind_logger,data_item_name,data_item_disp_mode=0,data_level=0):
        self.output_logger=bind_logger
        self.data_item_name=data_item_name
        self.disp_mode=data_item_disp_mode
        self.disp_item=self.data_item_name
        self.data_level=data_level
    def format_item_name(self,format_str):
        self.disp_item=format_str.format(self.data_item_name)
    def append_info(self,info):
        if self.data_item_name is not None:
            if self.disp_mode==0:
                self.output_logger.append_info(self.disp_item+"\n")
            elif self.disp_mode==1:
                pass
            elif self.disp_mode==2:
                if GeneralGlobalCounter.GetCounterVal_Scopes('output_records.{}'.format(self.data_item_name))==0:
                    GeneralGlobalCounter.StepCounter_Scopes('output_records.{}'.format(self.data_item_name),1)
                    self.output_logger.append_info(self.disp_item+"\n")
        
        self.output_logger.append_info(info,self.data_level)
    def log_timestamp(self):
        self.output_logger.log_timestamp()
    def set_data_signature_disp_mode(self,mode):
        self.disp_mode=mode
    def append_info_print(self,info):
        print(info)
        self.append_info(info)
class LogData_StrList(LogData):
    def __init__(self,bind_logger,data_item_name=None,data_level=0):
        if data_item_name is None:
            data_item_name="STR_DATA"+str(GeneralGlobalCounter.GetCounterVal_Scopes("data.str.number"))
        GeneralGlobalCounter.StepCounter_Scopes("data.str.number",1)
        super().__init__(bind_logger,data_item_name,data_level)
    def append_info(self,info,plus_mark='\n'):
        super().append_info(info+plus_mark)
class LogData_UniqueRecord(LogData):
    def __init__(self,bind_logger,data_item_name=None,data_level=0,empyt_info=''):
        if data_item_name is None:
            data_item_name="UniqueRec{}".format(GeneralGlobalCounter.GetCounterVal_Scopes("data.uqr.number"))
        GeneralGlobalCounter.StepCounter_Scopes("data.uqr.number",1)
        super().__init__(bind_logger,data_item_name,data_level)
        self.unique_map={}
        self.empyt_info=empyt_info#as replacement of replicated info
    def append_info(self,unique_info,format_str=''):
        if format_str=='' or format_str is None:
            info=unique_info
        else:
            info=format_str.format(unique_info)
        if self.unique_map.get(unique_info) is not None:
            if self.empyt_info is not None and self.empyt_info!="":
               super().append_info(self.empyt_info)
        else:
            self.unique_map[unique_info]=True
            super().append_info(info)
class PerfStatData(LogData):
    def __init__(self,detail_full_logger,summary_logger,data_item_name=None,sample_step=0.5,belta=1.0,manual_boundary=(0,10)):
        if data_item_name is None:
            data_item_name="perf"+str(GeneralGlobalCounter.GetCounterVal_Scopes("data.perf.number"))
        GeneralGlobalCounter.GetCounterVal_Scopes("data.perf.number")
        super().__init__(detail_full_logger,data_item_name,data_level=LogData.DATA_LEVEL_RESULT)
        self.detail_full_logger=detail_full_logger
        self.summary_logger=summary_logger
        self.sample_step=sample_step
        self.belta=belta
        self.scores_keys=["tp","tn","fp","fn","rp","rn"]
        self.scores_buf={key:[] for key in self.scores_keys}
        self.prediction_count={}.fromkeys(self.scores_keys,0)
        self.scores_output_idx={}.fromkeys(self.scores_keys,0)
        self.manual_boundary=manual_boundary
    def append_info(self,prediction,label,output):
        ordered_keys=["fn","tn","fp","tp"]
        ex_ordered_keys=["rp","rn"]
        
        for idx in range(0,len(prediction)):
            prediction_match_flag=int(prediction[idx]==label[idx])
            postive_flag=int(prediction[idx]==1)
            state_flag=prediction_match_flag+postive_flag*2
            target_key=ordered_keys[state_flag]#0,1,2,3 respectively
            self.prediction_count[target_key]+=1
            self.scores_buf[target_key].append(float(output[idx,1]-output[idx,0]))
            target_key_ex=ex_ordered_keys[int(state_flag%3!=0)]
            
            self.prediction_count[target_key_ex]+=1
            self.scores_buf[target_key_ex].append(float(output[idx,1]-output[idx,0]))
        
        #output info
        if self.detail_full_logger is not None:
            #output all scores
            self.set_data_signature_disp_mode(self.ITEM_DISP_MODE_HIDDEN)
            for key in self.scores_keys:
                output_idx=self.scores_output_idx[key]
                score_buf=self.scores_buf[key]
                if output_idx==0:#the first-time output
                    super().append_info("{0}_len{1},".format(key,len(score_buf)))
                for i in range(output_idx,len(score_buf)):
                    super().append_info("{},".format(score_buf[i]))
                output_idx=len(score_buf)
                self.scores_output_idx[key]=output_idx
    def perf_summary(self):
        rp_scores=self.scores_buf["rp"]
        rn_scores=self.scores_buf["rn"]
        rp_total=len(rp_scores)
        rn_total=len(rn_scores)
        number_total_dict={"rp":rp_total,"rn":rn_total}
        reverse_mapping={"rp":"rn","rn":"rp"}
        if self.manual_boundary is None:
            sub_bound=min(min(rp_scores),min(rn_scores))
            sup_bound=max(max(rp_scores),max(rp_scores))
        else:
            sub_bound=self.manual_boundary[0]
            sup_bound=self.manual_boundary[1]
        left_fence=sub_bound
        right_fence=left_fence+self.sample_step
        finished=False
        statistic_dict_all={"rp":{},"rn":{}}
        
        while not finished:
            if right_fence>=sup_bound:
                right_fence=sup_bound
                finished=True
            bound_key=(left_fence,right_fence)
            left_fence=right_fence
            right_fence=left_fence+self.sample_step
            statistic_dict_all["rp"][bound_key]=0
            statistic_dict_all["rn"][bound_key]=0
        #count
        disperse_state_dict_all={"rp":{},"rn":{}}
        display_dict={k:{} for k in disperse_state_dict_all.keys()}
        for key in ["rp","rn"]:
            scores=self.scores_buf[key]
            statistic_dict=statistic_dict_all[key]
            donw_side_outlier=0
            up_side_outlier=0
            for s in scores:
                if s>sup_bound:
                    up_side_outlier+=1
                elif s<sub_bound:
                    donw_side_outlier+=1
                else:
                    for bound_key in statistic_dict:
                        left_fence=bound_key[0]
                        right_fence=bound_key[1]
                        if s>=left_fence and s<right_fence:
                            statistic_dict[bound_key]+=1
                            break
            disperse_state_dict_all[key]={}.fromkeys(map(lambda k:"<{}".format(k[0]),statistic_dict.keys()),donw_side_outlier)
            for threshold in disperse_state_dict_all[key]:
                th_val=float(threshold[1:])
                for bound_key in statistic_dict:
                    distance=bound_key[0]-th_val
                    if distance<0 and distance**2>(0.01*self.sample_step)**2:
                        disperse_state_dict_all[key][threshold]+=statistic_dict[bound_key]
            disp_dict=dict(list(map(lambda k:("[{},{})".format(k[0],k[1]),statistic_dict[k]),statistic_dict.keys())))
            disp_dict["<{}".format(sub_bound)]=donw_side_outlier
            disp_dict[">{}".format(sup_bound)]=up_side_outlier
            display_dict[key]=disp_dict
        type_keys=["positive","negative"]
        metric_keys=["precision","recall","f-{}-score".format(int(self.belta))]
        perf_scores_dict={k1:{k2:{k3:None for k3 in metric_keys} for k2 in type_keys} for k1 in disperse_state_dict_all["rp"].keys()}
        selector_basic=lambda x,y:x
        selector_judge_table={"rn":lambda x,y:selector_basic(x,y),"rp":lambda x,y:selector_basic(y,x)}
        max_value_record_dict={kx:{mk:{"threshold":'',"value":0.0} for mk in metric_keys}for kx in ["rp","rn"]}
        for threshold in perf_scores_dict:
           
            perf_scores_item=perf_scores_dict[threshold]
            translation_table={"rp":0,"rn":1}
            for dic_type_k in ["rp","rn"]:
                beneath_ones=disperse_state_dict_all[dic_type_k][threshold]
                upper_ones=number_total_dict[dic_type_k]-beneath_ones
                other_key=reverse_mapping[dic_type_k]
                beneath_others=disperse_state_dict_all[other_key][threshold]
                upper_others=number_total_dict[other_key]-beneath_others
                perf_dic_type_key=type_keys[translation_table[dic_type_k]]
                judge_selector=selector_judge_table[dic_type_k]
                true_ones=judge_selector(beneath_ones,upper_ones)
                false_ones=judge_selector(beneath_others,upper_others)
                
                precision=true_ones/(true_ones+false_ones) if true_ones!=0 or false_ones!=0 else 0
                recall=true_ones/(beneath_ones+upper_ones)
                f_belta_score=(1+self.belta**2)*precision*recall/(self.belta**2*precision+recall) if precision!=0 or recall!=0 else 0
                record_dict=dict(zip(metric_keys,[precision,recall,f_belta_score]))
                perf_scores_item[perf_dic_type_key]=record_dict
                
                for m_k in max_value_record_dict[dic_type_k]:
                    if max_value_record_dict[dic_type_k][m_k]["value"]<record_dict[m_k]:
                        max_value_record_dict[dic_type_k][m_k]["value"]=record_dict[m_k]
                        max_value_record_dict[dic_type_k][m_k]["threshold"]=threshold
       
        self.summary_logger.append_info("data dispersion :\n")
        for type_k in disperse_state_dict_all:
            self.summary_logger.append_info("for data type {}:\n".format(type_k))
            for th in disperse_state_dict_all[type_k]:
                self.summary_logger.append_info("data in range {} : {}\n".format(th,disperse_state_dict_all[type_k][th]))
        self.summary_logger.append_info("threshold selection:\n")
        for th in perf_scores_dict:
            self.summary_logger.append_info("with threshold value {}\n".format(th[1:]))
            single_perf_dict=perf_scores_dict[th]
            table_head="\t\t\t{}\t{}\t{}\n".format(*metric_keys)
            self.summary_logger.append_info(table_head)
            for real_data_type in single_perf_dict:
                self.summary_logger.append_info("{}\t".format(real_data_type))
                fix="\t\t"
                for mk in metric_keys:
                    length=4
                    data=str(single_perf_dict[real_data_type][mk])[:length]
                    if data=="0":
                        data="0.0"
                    data=data+"0"*(length-len(data) if length-len(data)>0 else 0)
                    data=data+fix
                    fix=fix[:-1]
                    self.summary_logger.append_info(data)
                self.summary_logger.append_info("\n")
        for d_k in max_value_record_dict:
            for m_k in max_value_record_dict[d_k]:
                self.summary_logger.append_info("for the max {} of {} data:\n".format(m_k,d_k)) 
                self.summary_logger.append_info("best th: {}, value: {}\n".format(max_value_record_dict[d_k][m_k]['threshold'],max_value_record_dict[d_k][m_k]['value']))
        self.summary_logger.manual_flush()
        
def quick_put(filename,info):
    f=open(filename,"w")
    f.write(info)
    f.close()

if __name__=="__main__":
    print("This module has no main function")
else:
    module_debug_logger=Logger('logger_module_output.log',use_base_dir=False,instant_flush=True,mode='a')
    module_log_info=LogData_StrList(module_debug_logger,'logger.py:')