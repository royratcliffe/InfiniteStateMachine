(* --- Interface --- *)
FUNCTION IsSameState : BOOL
VAR_INPUT
	itfStateLHS : IState;
	itfStateRHS : IState;
END_VAR
VAR
END_VAR

(* --- Implementation --- *)
IsSameState := itfStateLHS = itfStateRHS;
