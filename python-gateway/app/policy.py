from dataclasses import dataclass
@dataclass
class Decision:
    allowed:bool
    approval_required:bool=False
    reason:str=""

def evaluate(tool:str,args:dict)->Decision:
    # Deterministic policy, not LLM reasoning.
    if tool=="ops_restart_service":
        env=str(args.get("environment","")).lower()
        if env=="production":
            return Decision(True,True,"production restart requires explicit approval")
    if tool=="crm_create_ticket":
        priority=str(args.get("priority","")).lower()
        if priority not in {"low","medium","high","critical"}:
            return Decision(False,False,"invalid priority")
    return Decision(True,False,"allowed by policy")
