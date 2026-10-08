(* --- Interface --- *)
METHOD PROTECTED Leave
VAR_INPUT
END_VAR
VAR
	itfState : IState;
END_VAR

(* --- Implementation --- *)
itfState := Pop();
IF itfState <> 0 THEN
	itfState.Leave(THIS^);
END_IF
