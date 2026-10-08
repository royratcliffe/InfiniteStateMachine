(* --- Interface --- *)
METHOD PROTECTED Pop : IState
VAR_INPUT
END_VAR

(* --- Implementation --- *)
IF iDepth > 0 THEN
	iDepth := iDepth - 1;
	Pop := itfStates[iDepth];
    (*
     * Clear the popped state from the stack. This is not strictly necessary,
     * but it can help catch use-after-free bugs.
     *)
	itfStates[iDepth] := 0;
ELSE
	Pop := 0;
END_IF
