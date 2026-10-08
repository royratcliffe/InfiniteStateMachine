(* --- Interface --- *)
METHOD PROTECTED Enter
VAR_IN_OUT
	itfState : IState;
END_VAR

(* --- Implementation --- *)
IF Push(itfState) THEN
	itfState.Enter(THIS^);
END_IF
