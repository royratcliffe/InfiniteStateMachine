(* --- Interface --- *)
METHOD PUBLIC AtLevel : IState
VAR_INPUT
	iLevel : INT;
END_VAR

(* --- Implementation --- *)
IF 0 <= iLevel AND iLevel < iDepth THEN
	AtLevel := itfStates[iLevel];
END_IF
