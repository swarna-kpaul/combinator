from util.manageperm import getresultfromDB
from environment.dbcred import USERERRORFLATFEE
######## Billing rules ########
######## API's are billed per request call (including streaming apis)
######## graph's are billed at fixed rate per run basis
######## streaming graphs are billed @ per second runtime
######## 


def logapicall(userid,apiname,quantity,runid,starttime,endtime,runstatus):
	query = """ Insert into apirequestlog(userid,apiname,isdataapi,calltime,quantity,endtime,runstatus,runid) select %s, functionname, isdataapi,%s,%s,%s,%s,%s from reusablefun where functionname= %s ;
              commit;"""
	inputlist = [userid,starttime,quantity,endtime,runstatus,runid,apiname]
	try:
		output = getresultfromDB(query,inputlist,output_req=False)
		return output
	except Exception as e:
		raise NameError("Store failed for logapicall "+apiname+" for user "+userid+" "+str(e).replace(":", " "))
	

def loggraphcall(userid,graphname,runid,starttime,endtime,runstatus):
	query = """ Insert into graphrequestlog(userid,graphname,calltime,endtime,runstatus,runid) values (%s, %s,%s, %s,%s,%s) ;
              commit;"""
	inputlist = [userid,graphname,starttime,endtime,runstatus,runid]
	try:
		output = getresultfromDB(query,inputlist,output_req=False)
		return output
	except Exception as e:
		raise NameError("Store failed for loggraphcall "+graphname+" for user "+userid+" "+str(e).replace(":", " "))
		
		
def loggraphtrans(runid):
	query = """insert into user_transactions_current (userid,graphname,rundate,runtime,runstatus,runcost,discount)
			select userid,graphname,calltime,total_runtime,runstatus,
			case when runstatus='internalerror' then 0 when runstatus='usererror' then """+str(USERERRORFLATFEE)+""" else coalesce(graphcost,0)+coalesce(apicost,0) end runcost,
			case when runstatus='internalerror' then 0 when runstatus='usererror' then 0 else coalesce(apidiscounts,0)+coalesce(graphdiscount,0)+coalesce(graphtimediscount,0) end discounts from graphcostperrun(%s);
			commit;"""
	inputlist = [runid]
	try:
		output = getresultfromDB(query,inputlist,output_req=False)
		return output
	except Exception as e:
		raise NameError("Store failed for user transactions for runid "+runid+" "+str(e).replace(":", " "))
		
		
def check_credit(userid):
	query = """select sum(coalesce(credit,0.00)+coalesce(discount,0.00)-coalesce(runcost,0.00)) from user_transactions_current where userid = %s"""
	inputlist = [userid]
	try:
		output = getresultfromDB(query,inputlist,output_req=True)
	except Exception as e:
		raise NameError("Store failed for user transactions for userid "+userid+" "+str(e).replace(":", " "))	
	try:
		return output[0][0]
	except:
		return 0
		

def logstreamapicall(userid,apiname,calls,is_data_api = 'N'):
	query = """ Insert into streamapirequestlog values (%s, %s,%s, now(),%s) ;
              commit;"""
	inputlist = [userid,apiname,is_data_api,calls]
	try:
		output = getresultfromDB(query,inputlist,output_req=False)
		return output
	except Exception as e:
		raise NameError("Store failed for logstreamapicall "+apiname+" for user "+userid+" "+str(e).replace(":", " "))

def logstreamgraphcall(userid,graphname,runtime):
	query = """ Insert into streamgraphrequestlog values (%s, %s, now(),%s) ;
              commit;"""
	inputlist = [userid,graphname,runtime]
	try:
		output = getresultfromDB(query,inputlist,output_req=False)
		return output
	except Exception as e:
		raise NameError("Store failed for logstreamgraphcall "+graphname+" for user "+userid+" "+str(e).replace(":", " "))

def registergraphbillingrate(graphname,billingrate,currency,is_streaming='N'):
	query = """ delete from graphbillingrate where graphname = %s;
				Insert into graphbillingrate values (%s, %s, %s,%s) ;
        commit;"""
	inputlist = [graphname,graphname,is_streaming,billingrate,currency]
	try:
		output = getresultfromDB(query,inputlist,output_req=False)
		return output
	except Exception as e:
		raise NameError("Store failed for registergraphbillingrate "+graphname+" "+str(e).replace(":", " "))
		
def registerapibillingrate(apiname,billingrate,currency):
	query = """ delete from apibillingrate where apiname = %s;
				Insert into apibillingrate values (%s, %s, %s);
        commit; """
	inputlist = [apiname,apiname,billingrate,currency]
	try:
		output = getresultfromDB(query,inputlist,output_req=False)
		return output
	except Exception as e:
		raise NameError("Store failed for registerapibillingrate "+apiname+" "+str(e).replace(":", " "))


##################  billing rules
#### rate_rule -- *; + 
#### rate -- <rate>
#### usage_slab = <lowerlimit>-<upperlimit>; * 
#### usage_moy = month of the year; 0
#### usage_wom = week of the month; 0
#### usage_dom = day of the month; 0
#### usage_dow = day of the week; 0


################## get user transactions 
def gettransactions(userid,startdate=None,enddate=None):
	if startdate == None or enddate == None:
		query = """select userid,graphname,rundate,runtime,runstatus,runcost,discount,credit,creditnote from user_transactions_current where userid = %s"""
		inputlist = [userid]
	else:
		query = """select userid,graphname,rundate,runtime,runstatus,runcost,discount,credit,creditnote from user_transactions_archived where userid = %s and runtime between %s and %s"""
		inputlist = [userid,startdate,enddate]
	try:
		output = getresultfromDB(query,inputlist,output_req=True)
		return output
	except Exception as e:
		raise NameError("Store failed for addusagebillingrule for user "+userid+" "+str(e).replace(":", " "))	

################ add credit
def addcredit(userid,credit,creditnote):
	query = """insert into user_transactions_current(userid,rundate, credit,creditnote) values (%s,now(),%s,%s);
			commit;"""
	try:
		output = getresultfromDB(query,inputlist,output_req=False)
		return output
	except Exception as e:
		raise NameError("Add credit failed for for user "+userid+" "+str(e).replace(":", " "))	
		
################ add free credit
def addfreecredit(userid):
	query = """delete from user_transactions_current where userid = %s and creditnote = 'free credit';
			insert into user_transactions_current(userid,rundate, credit,creditnote) select %s,now(),credit,'free credit' from freecredit where freq = 'monthly';
			commit;"""
	inputlist=[userid,userid]
	try:
		output = getresultfromDB(query,inputlist,output_req=False)
		return output
	except Exception as e:
		raise NameError("Add credit failed for for user "+userid+" "+str(e).replace(":", " "))	


		
################ monthly transastion maintainence
def archivetransactions(freq="monthly"):
	query = """select count(1) from user_transactions_current  where rundate<date_trunc('month', now());"""
	inputlist=[]
	try:
		output = getresultfromDB(query,inputlist,output_req=True)
	except Exception as e:
		raise NameError("Querying user_transactions_current failed "+str(e).replace(":", " "))
	if output[0][0] > 0:
	########## archive transactions 
		query = """insert into user_transactions_current(userid,rundate,credit,creditnote) 
				select userid,now(),case when creditleft <= 0 then 0 else creditleft end creditleft,'carryover credit'
				from (
				select userid,nc - case when fc_cost >0 then 0 else fc_cost end creditleft
				from (
				select userid,sum((case when coalesce(creditnote,'') = 'free credit' then coalesce(credit,0) else 0 end) -coalesce(runcost,0)+coalesce(discount,0)) fc_cost,
				sum(case when coalesce(creditnote,'') = 'free credit' then 0  else coalesce(credit,0) end) nc from user_transactions_current
				group by userid) a ) b;
				Insert into user_transactions_archived select * from user_transactions_current where calltime<date_trunc('month', now());
				delete from user_transactions_current where calltime<date_trunc('month', now());
				commit;"""
		try:
			output = getresultfromDB(query,inputlist,output_req=False)
		except Exception as e:
			raise NameError("TRansactions archiving failed for "+str(e).replace(":", " "))
	############# add free credit ###############
	query = """delete from user_transactions_current  where rundate>=date_trunc('month', now()) and creditnote = 'free credit';
				insert into user_transactions_current(userid,rundate,credit,creditnote)
				select userid,now(),credit,'free credit' from users a, freecredit b where b.freq='monthly';
				commit;"""
	try:
		output = getresultfromDB(query,inputlist,output_req=False)
	except Exception as e:
		raise NameError("Add credit failed: "+str(e).replace(":", " "))
	return output