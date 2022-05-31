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

class GlobalMap:
    meta_map={}
    def GetMap(map_name):
        if GlobalMap.meta_map.get(map_name) is None:
            GlobalMap.meta_map[map_name]={}
        return GlobalMap.meta_map[map_name]
    
class BreakPointImp:
    Global_num_count=0
    def __init__(self,info=None):
        pass
        self.options_dict={"Finish":self._finish,"Sleep":self._sleep,"Pass":self._pass}
        self.translation_table={}
        self.active=True
        self.sleep=False
        self.sleep_period=None
        self.sleep_count=0
        self.output_info=info if info is not None else "Point {"+str(BreakPoint.Global_num_count)+"}"
        BreakPoint.Global_num_count+=1
    def Reset(self):
        self.active=True
        self.sleep=False
        self.sleep_count=0
    def Invoke(self):
        if self.active:
            if self.sleep:
                self.sleep_count+=1
                if self.sleep_count>=self.sleep_period:
                    self.sleep_count=0
                    self.sleep=False
            else:
                i=input(self.output_info)
                if self.translation_table.get(i) is not None:
                    i=self.translation_table[i]
                action=self.options_dict.get(i)
                if action is None:
                    print('breakpoint behaviour [{}] not defined'.format(i))
                    return
                else:
                    action()
        else:
            return
    def SetTranslationPair(self,*pairs):
        for pair in pairs:
            if self.options_dict.get(pair[0]) is not None:
                print('Ambiguous alias for pair [{}] to [{}]: {} is already defined for {}'.format(pair[0],pair[1],pair[0],self.options_dict[pair[0]]))
            else:
                print("Set alias of {} to {} ".format(pair[1],pair[0]))
                self.translation_table[pair[0]]=pair[1]

    def _finish(self):
        self.active=False
    def _pass(self):
        pass
    def _sleep(self,duration=None):
        if duration is not None:
            self.sleep_period=duration
        self.sleep_count=0
        self.sleep=True
class BreakPoint(BreakPointImp):
    def __init__(self,info,alias_pairs=[('p','Pass'),('f',"Finish"),('s','sleep')]):
        super().__init__(info)
        self.SetTranslationPair(*alias_pairs)
class LimitedTimesBreakPoint(BreakPoint):
    def __init__(self,info,alias_pairs=[],limited_times=1):
        if alias_pairs==[]:
            super().__init__(info)
        else:
            super().__init__(info,alias_pairs)
        self.limited_times=limited_times
        self.current_hit=0
    def Invoke(self):
        #print("hit {} limit{}".format(self.current_hit,self.limited_times))
        if self.current_hit>=self.limited_times:
            
            return
        else:
            super().Invoke()
            self.current_hit+=1
    def Reset(self):
        super().Reset()
        self.current_hit=0
class BreakPointsManager:
    STATUS_IN_USE=0
    STATUS_CLOSED=1
    STATUS_IDLE=2
    class BreakPointInManager:
        STATUS_IN_USE=0
        STATUS_CLOSED=1
        STATUS_IDLE=2
        def __init__(self,breakpoint_main,status_info,uid):
            self.breakpoint_main=breakpoint_main
            self.status_info=status_info
            self.uid=uid
    single_bp_pool=[]
    uid_map_to_bp={}
    def find_bp(uid):
        return BreakPointsManager.uid_map_to_bp.get(uid).breakpoint_main if BreakPointsManager.uid_map_to_bp.get(uid) is not None else None
    def get_breakpoint_single(info='',times=1,alias_setting=[]):
        BreakPointsManager.__update_bp_pool_status()
        STATUS_IN_USE=BreakPointsManager.STATUS_IN_USE
        for bp in BreakPointsManager.single_bp_pool:
            if bp.status_info!=STATUS_IN_USE:
                bp.status_info=STATUS_IN_USE
                bp.breakpoint_main.Reset()
                return bp.breakpoint_main,bp.uid
        return BreakPointsManager.__extend_new_bp_term_single(info,times,alias_setting)
        

    def __update_bp_pool_status():
        for bp in BreakPointsManager.single_bp_pool:
            if bp.breakpoint_main.active:
                bp.status_info=BreakPointsManager.BreakPointInManager.STATUS_IN_USE
            else:
                bp.status_info=BreakPointsManager.BreakPointInManager.STATUS_CLOSED
    def __generate_new_breakpoint_single(info='',times=1,alias_setting=[]):
        if info=='':
            info="Breakpoint[single] ({})".format(GlobalCounter.GetCounterVal("single_breakpoints_num"))
        if alias_setting==[]:
            bp=LimitedTimesBreakPoint(info=info,limited_times=times)
        else:
            bp=LimitedTimesBreakPoint(info=info,limited_times=times,alias_pairs=alias_setting)
        GlobalCounter.StepCounter("single_breakpoints_num",1)
        return bp
    def __extend_new_bp_term_single(info='',times=1,alias_setting=[]):
        new_bp=BreakPointsManager.__generate_new_breakpoint_single(info,times,alias_setting)
        uid=GlobalCounter.GetCounterVal('bp_uid')
        GlobalCounter.StepCounter('bp_uid',1)
        bp_complete=BreakPointsManager.BreakPointInManager(new_bp,BreakPointsManager.BreakPointInManager.STATUS_IDLE,uid)
        BreakPointsManager.uid_map_to_bp[uid]=bp_complete
        BreakPointsManager.single_bp_pool.append(bp_complete)
        return new_bp,uid
    
def GetBreakPointSingle(info='',times=1,alias_setting=[]):
    return BreakPointsManager.get_breakpoint_single(info=info,times=times,alias_setting=alias_setting)
def SetOneBreakPointSingle(bp_signature,info='',times=1,alias_setting=[]):
    register_record=GlobalMap.GetMap('BreakpointsSetRegiister')
    uid=register_record.get(bp_signature)
    bp=BreakPointsManager.find_bp(uid)
    if bp is None:
        
        bp_here, uid_here=GetBreakPointSingle(info,times,alias_setting)
        register_record[bp_signature]=uid_here
        bp_here.Invoke()
    else:
        bp.Invoke()
