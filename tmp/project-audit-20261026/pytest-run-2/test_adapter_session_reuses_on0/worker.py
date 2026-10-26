import json,sys
count=0
for line in sys.stdin:
 count+=1; value=json.loads(line); print(json.dumps({'count':count,'value':value['value']}),flush=True)
