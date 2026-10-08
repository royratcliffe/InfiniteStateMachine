(* --- Interface --- *)
METHOD PROTECTED Enter
VAR_INPUT
	itfState : IState;
END_VAR

(* --- Implementation --- *)
IF Push(itfState) THEN
	itfState.Enter(THIS^);
END_IF
