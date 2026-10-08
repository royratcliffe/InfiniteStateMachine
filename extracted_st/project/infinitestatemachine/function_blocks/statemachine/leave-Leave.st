(* --- Interface --- *)
METHOD PROTECTED Leave
VAR_IN_OUT
	itfState : IState;
END_VAR

(* --- Implementation --- *)
itfState := Pop();
IF itfState <> 0 THEN
	itfState.Leave(THIS^);
END_IF
