(* --- Interface --- *)
METHOD PROTECTED Push : BOOL
VAR_INPUT
	itfState : IState;
END_VAR

(* --- Implementation --- *)
Push := iDepth < ISM.gc_iMaxDepth;
IF Push THEN
	itfStates[iDepth] := itfState;
	iDepth := iDepth + 1;
END_IF
