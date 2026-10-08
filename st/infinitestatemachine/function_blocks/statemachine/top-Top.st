(* --- Interface --- *)
METHOD PUBLIC Top : IState
VAR_INPUT
END_VAR

(* --- Implementation --- *)
IF iDepth > 0 THEN
	Top := itfStates[iDepth - 1];
END_IF
