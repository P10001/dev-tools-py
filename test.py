import logger
from torch import tensor as ts
def test_logger():
    test_lg=logger.PesudoLogger_test(out_file_name=None)
    test_lg_f=logger.Logger(out_file_name="test_res.log")
    perf_lg=logger.PerfStatData(test_lg,test_lg_f)
    test_prediction=ts([[1],[1],[1],[0],[0],[0]])
    test_label=ts([[1],[1],[0],[1],[0],[0]])
    test_output=ts([[1,2],[6,2],[2,5],[3,5],[1,5],[0,3]])
    perf_lg.append_info(test_prediction,test_label,test_output)
    perf_lg.perf_summary()
def test_counter():
    import other_tools
    g_counter=other_tools.GeneralGlobalCounter
    g_counter.StepCounter_Scopes("simple.output1",3)
    g_counter.StepCounter_Scopes("global.fs1",2)
    g_counter.StepCounter_Scopes("fss",1)
    print("val: {} {} {}".format(g_counter.GetCounterVal_Scopes("simple.output1"),g_counter.GetCounterVal_Scopes("fss"),g_counter.GetCounterVal_Scopes("global.fs1")))
    g_counter.display()
test_counter()
test_logger()