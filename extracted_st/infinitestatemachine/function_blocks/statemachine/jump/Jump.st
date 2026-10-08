(* --- Interface --- *)
METHOD Jump
VAR_INPUT
	itfState : IState;
END_VAR

(* --- Implementation --- *)
iDepth := DepthOfState(itfState, ISM.gc_iMaxDepth, itfStates);
